from typing import Dict, Optional

import numpy as np
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session

from database.db import engine
from database.models import EnergyRecord
from ml.predict import predict_anomaly, predict_cost, predict_efficiency


def _as_float(value, default: float = 0.0) -> float:
  try:
    if value is None:
      return default
    return float(value)
  except (TypeError, ValueError):
    return default


def _machine_averages(db: Session, machine_id: str) -> Dict[str, float]:
  row = (
    db.query(
      func.avg(EnergyRecord.power_kw),
      func.avg(EnergyRecord.load_percent),
      func.avg(EnergyRecord.temperature),
      func.avg(EnergyRecord.downtime_minutes),
      func.avg(EnergyRecord.power_factor),
      func.avg(EnergyRecord.energy_kwh),
      func.avg(EnergyRecord.electricity_tariff),
      func.avg(EnergyRecord.idle_flag),
    )
    .filter(EnergyRecord.machine_id == machine_id)
    .first()
  )

  if row is None or all(v is None for v in row):
    # Fall back to global averages if machine_id has no rows.
    row = (
      db.query(
        func.avg(EnergyRecord.power_kw),
        func.avg(EnergyRecord.load_percent),
        func.avg(EnergyRecord.temperature),
        func.avg(EnergyRecord.downtime_minutes),
        func.avg(EnergyRecord.power_factor),
        func.avg(EnergyRecord.energy_kwh),
        func.avg(EnergyRecord.electricity_tariff),
        func.avg(EnergyRecord.idle_flag),
      )
      .first()
    )

  (
    avg_power_kw,
    avg_load_percent,
    avg_temperature,
    avg_downtime_minutes,
    avg_power_factor,
    avg_energy_kwh,
    avg_tariff,
    avg_idle_flag,
  ) = row

  return {
    'power_kw': _as_float(avg_power_kw),
    'load_percent': _as_float(avg_load_percent),
    'temperature': _as_float(avg_temperature),
    'downtime_minutes': _as_float(avg_downtime_minutes),
    'power_factor': _as_float(avg_power_factor),
    'energy_kwh': _as_float(avg_energy_kwh),
    'electricity_tariff': _as_float(avg_tariff),
    'idle_rate': float(np.clip(_as_float(avg_idle_flag), 0.0, 1.0)),
  }


def run_full_analysis(machine_id: str, on_time_hours: float, off_time_hours: float, db: Session) -> Dict:
  on_time_hours = max(_as_float(on_time_hours), 0.0)
  off_time_hours = max(_as_float(off_time_hours), 0.0)

  avg = _machine_averages(db, machine_id)

  # Estimated energy (kWh) using average power draw over requested runtime.
  estimated_energy = max(0.0, avg['power_kw']) * on_time_hours

  try:
    # ML predictions
    anomaly_pred = predict_anomaly(
      {
        'power_kw': avg['power_kw'],
        'load_percent': avg['load_percent'],
        'temperature': avg['temperature'],
        'downtime_minutes': avg['downtime_minutes'],
        'power_factor': avg['power_factor'],
        'energy_kwh': avg['energy_kwh'],
      },
    )

    predicted_cost = predict_cost(
      {
        'power_kw': avg['power_kw'],
        'load_percent': avg['load_percent'],
        'on_time_hours': on_time_hours,
        'electricity_tariff': avg['electricity_tariff'],
      },
    )

    efficiency_score = predict_efficiency(
      {
        'load_percent': avg['load_percent'],
        'downtime_minutes': avg['downtime_minutes'] + (10.0 if off_time_hours < 4 else 0.0),
        'temperature': avg['temperature'],
        'power_factor': avg['power_factor'],
      },
    )
  except Exception:
    anomaly_pred = {'anomaly_status': 'Normal', 'anomaly_score': 0.0}
    predicted_cost = estimated_energy * avg['electricity_tariff']
    efficiency_score = 0.0

  # Spec: energy_wasted = idle_flag × energy_kwh.
  # We approximate this over the requested runtime by scaling the machine-average wasted energy.
  avg_on_time = (avg['energy_kwh'] / avg['power_kw']) if avg['power_kw'] > 0 else 1.0
  avg_on_time = max(avg_on_time, 0.1)
  scale = on_time_hours / avg_on_time
  energy_wasted = (avg['idle_rate'] * avg['energy_kwh']) * scale

  return {
    'machine_id': machine_id,
    'anomaly_status': anomaly_pred['anomaly_status'],
    'anomaly_score': float(anomaly_pred['anomaly_score']),
    'predicted_cost': int(round(predicted_cost)),
    'efficiency_score': float(round(efficiency_score, 4)),
    'energy_wasted': float(round(energy_wasted, 2)),
    'estimated_energy': float(round(estimated_energy, 2)),
  }


def get_dashboard_ml_insights(limit: Optional[int] = None) -> Dict:
  """Compute ML-based dashboard insights over the stored dataset.

  - anomaly_count: predicted anomalies using IsolationForest
  - average_efficiency_ml: average predicted efficiency using RandomForestRegressor
  """
  query = """
    SELECT
      power_kw,
      load_percent,
      temperature,
      downtime_minutes,
      power_factor,
      energy_kwh
    FROM energy_records
  """
  if limit:
    query += f" LIMIT {int(limit)}"

  df = pd.read_sql_query(query, con=engine)
  if df.empty:
    return {'anomaly_count': 0, 'average_efficiency_ml': 0.0}

  for c in df.columns:
    df[c] = pd.to_numeric(df[c], errors='coerce')
    df[c] = df[c].fillna(df[c].median() if not np.isnan(df[c].median()) else 0.0)

  try:
    from ml.predict import _load_anomaly_model, _load_efficiency_model  # noqa: PLC0415

    anomaly_bundle = _load_anomaly_model()
    eff_bundle = _load_efficiency_model()

    # Align DataFrame columns with model feature lists.
    anomaly_features = anomaly_bundle.get('features') or []
    eff_features = eff_bundle.get('features') or []

    if anomaly_features:
      X_anom = df[[c for c in anomaly_features if c in df.columns]].to_numpy(dtype=float)
      anomaly_labels = anomaly_bundle['model'].predict(X_anom)
      anomaly_count = int((anomaly_labels == -1).sum())
    else:
      anomaly_count = 0

    if eff_features:
      X_eff = df[[c for c in eff_features if c in df.columns]].to_numpy(dtype=float)
      eff_preds = eff_bundle['model'].predict(X_eff)
      eff_preds = np.clip(np.asarray(eff_preds, dtype=float), 0.0, 1.0)
      avg_eff = float(np.mean(eff_preds)) if len(eff_preds) else 0.0
    else:
      avg_eff = 0.0

    return {'anomaly_count': anomaly_count, 'average_efficiency_ml': avg_eff}
  except Exception:
    return {'anomaly_count': 0, 'average_efficiency_ml': 0.0}

