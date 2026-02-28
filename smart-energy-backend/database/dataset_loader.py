import logging
import os
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from .db import SessionLocal, engine
from .models import EnergyRecord

logger = logging.getLogger(__name__)


def _get_dataset_path() -> str:
  base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  return os.path.join(base_dir, 'dataset', 'energy_dataset.csv')


def _has_existing_records(db: Session) -> bool:
  return db.query(EnergyRecord).first() is not None


def _to_float(value) -> Optional[float]:
  if pd.isna(value):
    return None
  try:
    return float(value)
  except (TypeError, ValueError):
    return None


def load_dataset_if_empty() -> None:
  """Load CSV dataset into the database if no records exist yet."""
  dataset_path = _get_dataset_path()

  if not os.path.exists(dataset_path):
    logger.warning('Dataset file not found at %s; skipping initial load.', dataset_path)
    return

  db = SessionLocal()
  try:
    if _has_existing_records(db):
      logger.info('Energy records already present in database; skipping dataset load.')
      return

    logger.info('Loading dataset from %s', dataset_path)
    df = pd.read_csv(dataset_path)

    if 'timestamp' in df.columns:
      df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    records = []
    for _, row in df.iterrows():
      record = EnergyRecord(
        machine_id=str(row.get('machine_id')) if not pd.isna(row.get('machine_id')) else None,
        machine_model=str(row.get('machine_model'))
        if not pd.isna(row.get('machine_model'))
        else None,
        rated_capacity_kw=_to_float(row.get('rated_capacity_kw')),
        contract_demand_kw=_to_float(row.get('contract_demand_kw')),
        timestamp=row.get('timestamp'),
        shift=str(row.get('shift')) if not pd.isna(row.get('shift')) else None,
        operator_id=str(row.get('operator_id'))
        if not pd.isna(row.get('operator_id'))
        else None,
        power_kw=_to_float(row.get('power_kw')),
        energy_kwh=_to_float(row.get('energy_kwh')),
        load_percent=_to_float(row.get('load_percent')),
        power_factor=_to_float(row.get('power_factor')),
        temperature=_to_float(row.get('temperature')),
        ambient_temperature=_to_float(row.get('ambient_temperature')),
        production_output=_to_float(row.get('production_output')),
        operating_status=str(row.get('operating_status'))
        if not pd.isna(row.get('operating_status'))
        else None,
        idle_flag=bool(row.get('idle_flag')) if not pd.isna(row.get('idle_flag')) else None,
        electricity_tariff=_to_float(row.get('electricity_tariff')),
        maintenance_cost=_to_float(row.get('maintenance_cost')),
        co2_emission=_to_float(row.get('co2_emission')),
        true_anomaly_label=int(row.get('true_anomaly_label'))
        if not pd.isna(row.get('true_anomaly_label'))
        else None,
        downtime_minutes=_to_float(row.get('downtime_minutes')),
      )
      records.append(record)

    if not records:
      logger.warning('Dataset is empty; no records inserted.')
      return

    db.bulk_save_objects(records)
    db.commit()
    logger.info('Inserted %d energy records into the database.', len(records))
  except Exception as exc:  # noqa: BLE001
    db.rollback()
    logger.exception('Error while loading dataset: %s', exc)
  finally:
    db.close()

