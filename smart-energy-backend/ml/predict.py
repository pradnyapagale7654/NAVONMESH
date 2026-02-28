import os
from functools import lru_cache
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd

from database.db import engine
from .train_models import get_model_paths


def _as_float(value, default: float = 0.0) -> float:
  try:
    if value is None:
      return default
    return float(value)
  except (TypeError, ValueError):
    return default


def _load_bundle(path: str) -> Dict:
  if not os.path.exists(path):
    raise FileNotFoundError(f'Model file not found: {path}. Train models first.')
  obj = joblib.load(path)
  # Backwards compatibility: allow plain estimators.
  if isinstance(obj, dict) and 'model' in obj and 'features' in obj:
    return obj
  return {'model': obj, 'features': [], 'feature_means': {}}


def _dataset_feature_means() -> Dict[str, float]:
  """Compute global numeric column means from energy_records for missing features."""
  try:
    df = pd.read_sql_query('SELECT * FROM energy_records', con=engine)
  except Exception:
    return {}

  if df.empty:
    return {}

  num_df = df.select_dtypes(include='number')
  return num_df.mean(numeric_only=True).fillna(0.0).to_dict()


def _build_feature_vector(bundle: Dict, input_data: Dict) -> Tuple[np.ndarray, Dict]:
  model = bundle['model']
  feature_names = bundle.get('features') or []
  feature_means = dict(bundle.get('feature_means') or {})

  # If the bundle does not include feature metadata (older models), fall back to dataset means.
  if not feature_names:
    if hasattr(model, 'n_features_in_'):
      # Use generic numeric columns from the DB to approximate features.
      means = _dataset_feature_means()
      feature_names = sorted(means.keys())[: model.n_features_in_]
      feature_means = means
    else:
      feature_names = []

  if not feature_means:
    feature_means = _dataset_feature_means()

  row = []
  for name in feature_names:
    if name in input_data and input_data.get(name) is not None:
      row.append(_as_float(input_data[name]))
    else:
      row.append(_as_float(feature_means.get(name, 0.0)))

  x = np.array([row], dtype=float) if row else np.zeros((1, 0), dtype=float)
  return x, {'model': model, 'features': feature_names}


@lru_cache(maxsize=1)
def _load_anomaly_model():
  paths = get_model_paths()
  return _load_bundle(paths.anomaly)


@lru_cache(maxsize=1)
def _load_cost_model():
  paths = get_model_paths()
  return _load_bundle(paths.cost)


@lru_cache(maxsize=1)
def _load_efficiency_model():
  paths = get_model_paths()
  return _load_bundle(paths.efficiency)


def predict_anomaly(input_data: Dict) -> Dict:
  """Return anomaly status (Normal/Anomaly) and anomaly score."""
  bundle = _load_anomaly_model()
  x, meta = _build_feature_vector(bundle, input_data)
  model = meta['model']

  pred = int(model.predict(x)[0])  # 1 normal, -1 anomaly
  score = float(model.decision_function(x)[0])

  status = 'Anomaly' if pred == -1 else 'Normal'
  return {'anomaly_status': status, 'anomaly_score': score}


def predict_cost(input_data: Dict) -> float:
  """Predict energy cost (INR) for the provided features."""
  bundle = _load_cost_model()
  x, meta = _build_feature_vector(bundle, input_data)
  model = meta['model']

  pred = float(model.predict(x)[0])
  return max(0.0, pred)


def predict_efficiency(input_data: Dict) -> float:
  """Predict efficiency score from 0..1 (clipped for UI friendliness)."""
  bundle = _load_efficiency_model()
  x, meta = _build_feature_vector(bundle, input_data)
  model = meta['model']

  pred = float(model.predict(x)[0])
  # For dashboard/UI, keep this in a stable range.
  return float(np.clip(pred, 0.0, 1.0))

