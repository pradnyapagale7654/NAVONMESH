import logging
import os
from dataclasses import dataclass
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.linear_model import LinearRegression

from database.db import engine

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ModelPaths:
  anomaly: str
  cost: str
  efficiency: str


def _base_dir() -> str:
  return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_model_paths() -> ModelPaths:
  models_dir = os.path.join(_base_dir(), 'models')
  return ModelPaths(
    anomaly=os.path.join(models_dir, 'anomaly_model.pkl'),
    cost=os.path.join(models_dir, 'cost_model.pkl'),
    efficiency=os.path.join(models_dir, 'efficiency_model.pkl'),
  )


def _models_exist(paths: ModelPaths) -> bool:
  return os.path.exists(paths.anomaly) and os.path.exists(paths.cost) and os.path.exists(paths.efficiency)


def _load_training_dataframe() -> pd.DataFrame:
  """Load full energy_records table into a DataFrame."""
  query = 'SELECT * FROM energy_records'
  df = pd.read_sql_query(query, con=engine)
  return df


def _numeric_dataframe(df: pd.DataFrame) -> pd.DataFrame:
  num_df = df.select_dtypes(include='number').copy()
  if num_df.empty:
    raise RuntimeError('No numeric columns available for model training.')
  num_df = num_df.fillna(0.0)
  return num_df


def _exclude_identifier_columns(columns) -> Tuple[str, ...]:
  excluded = []
  for col in columns:
    lower = str(col).lower()
    if lower == 'id' or lower.endswith('_id') or lower.endswith('id'):
      excluded.append(col)
  return tuple(excluded)


def _feature_bundle(model, X: pd.DataFrame) -> Dict:
  means = X.mean(numeric_only=True).fillna(0.0).to_dict()
  return {
    'model': model,
    'features': list(X.columns),
    'feature_means': means,
  }


def train_anomaly_model(df: pd.DataFrame) -> Dict:
  num_df = _numeric_dataframe(df)
  id_like = _exclude_identifier_columns(num_df.columns)
  feature_cols = [c for c in num_df.columns if c not in id_like]
  X = num_df[feature_cols]

  model = IsolationForest(
    n_estimators=250,
    contamination='auto',
    random_state=42,
  )
  model.fit(X.to_numpy(dtype=float))
  return _feature_bundle(model, X)


def train_cost_model(df: pd.DataFrame) -> Dict:
  df_num = _numeric_dataframe(df)

  if 'energy_cost' in df_num.columns:
    df_num['energy_cost'] = df_num['energy_cost'].astype(float)
  elif {'energy_kwh', 'electricity_tariff'}.issubset(df_num.columns):
    df_num['energy_cost'] = (df_num['energy_kwh'] * df_num['electricity_tariff']).astype(float)
  else:
    raise RuntimeError(
      'Cannot compute energy_cost – ensure either energy_cost column exists or both energy_kwh and electricity_tariff.',
    )

  target = 'energy_cost'
  id_like = set(_exclude_identifier_columns(df_num.columns))
  feature_cols = [c for c in df_num.columns if c not in id_like and c != target]
  X = df_num[feature_cols]
  y = df_num[target].to_numpy(dtype=float)

  model = LinearRegression()
  model.fit(X.to_numpy(dtype=float), y)
  return _feature_bundle(model, X)


def train_efficiency_model(df: pd.DataFrame) -> Dict:
  df_num = _numeric_dataframe(df)

  if 'efficiency' in df_num.columns:
    df_num['efficiency'] = df_num['efficiency'].astype(float)
  elif {'production_output', 'energy_kwh'}.issubset(df_num.columns):
    # Avoid division by zero.
    energy = df_num['energy_kwh'].replace(0, np.nan)
    eff = (df_num['production_output'] / energy).replace([np.inf, -np.inf], np.nan)
    eff = eff.fillna(0.0)
    df_num['efficiency'] = eff.astype(float)
  else:
    raise RuntimeError(
      'Cannot compute efficiency – ensure either efficiency column exists or both production_output and energy_kwh.',
    )

  target = 'efficiency'
  id_like = set(_exclude_identifier_columns(df_num.columns))
  feature_cols = [c for c in df_num.columns if c not in id_like and c != target]
  X = df_num[feature_cols]
  y = df_num[target].to_numpy(dtype=float)

  model = RandomForestRegressor(
    n_estimators=250,
    random_state=42,
    n_jobs=-1,
  )
  model.fit(X.to_numpy(dtype=float), y)
  return _feature_bundle(model, X)


def train_all_models() -> Tuple[Dict, Dict, Dict]:
  df = _load_training_dataframe()
  if df.empty:
    raise RuntimeError('No records found in energy_records table; cannot train ML models.')

  anomaly_bundle = train_anomaly_model(df)
  cost_bundle = train_cost_model(df)
  efficiency_bundle = train_efficiency_model(df)
  return anomaly_bundle, cost_bundle, efficiency_bundle


def ensure_models_trained(force: bool = False) -> None:
  paths = get_model_paths()
  os.makedirs(os.path.dirname(paths.anomaly), exist_ok=True)

  if not force and _models_exist(paths):
    logger.info('ML models already exist; skipping training.')
    return

  logger.info('Training ML models from CSV dataset...')
  print('Training ML models from CSV dataset...')
  try:
    anomaly_bundle, cost_bundle, efficiency_bundle = train_all_models()
  except Exception as exc:  # noqa: BLE001
    # If the dataset isn't loaded yet, we don't want to block app startup.
    logger.warning('Skipping ML training (no data available yet): %s', exc)
    return

  joblib.dump(anomaly_bundle, paths.anomaly)
  joblib.dump(cost_bundle, paths.cost)
  joblib.dump(efficiency_bundle, paths.efficiency)

  print('ML models trained successfully')
  logger.info('ML models trained successfully and saved to %s', os.path.dirname(paths.anomaly))

