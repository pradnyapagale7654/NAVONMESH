from typing import Dict, List

from sqlalchemy import func
from sqlalchemy.orm import Session

from database.models import EnergyRecord


def get_dashboard_stats(db: Session) -> Dict:
  total_energy = (
    db.query(func.coalesce(func.sum(EnergyRecord.energy_kwh), 0.0)).scalar() or 0.0
  )
  total_cost = (
    db.query(
      func.coalesce(
        func.sum(EnergyRecord.energy_kwh * EnergyRecord.electricity_tariff),
        0.0,
      ),
    ).scalar()
    or 0.0
  )

  efficiency_expr = EnergyRecord.production_output / func.nullif(
    EnergyRecord.energy_kwh,
    0,
  )
  average_efficiency = (
    db.query(func.avg(efficiency_expr)).scalar()
    if db.query(EnergyRecord.id).first()
    else 0.0
  ) or 0.0

  total_anomalies = (
    db.query(func.count())
    .filter(EnergyRecord.true_anomaly_label == 1)
    .scalar()
    or 0
  )

  machine_rows: List = (
    db.query(
      EnergyRecord.machine_id,
      func.coalesce(func.sum(EnergyRecord.energy_kwh), 0.0),
    )
    .group_by(EnergyRecord.machine_id)
    .all()
  )
  shift_rows: List = (
    db.query(
      EnergyRecord.shift,
      func.coalesce(func.sum(EnergyRecord.energy_kwh), 0.0),
    )
    .group_by(EnergyRecord.shift)
    .all()
  )

  machine_energy_distribution = [
    {
      'machine_id': machine_id if machine_id is not None else 'Unknown',
      'total_energy': float(total or 0.0),
    }
    for machine_id, total in machine_rows
  ]

  shift_energy_distribution = [
    {
      'shift': shift if shift is not None else 'Unknown',
      'total_energy': float(total or 0.0),
    }
    for shift, total in shift_rows
  ]

  return {
    'total_energy_consumption': float(total_energy),
    'total_energy_cost': float(total_cost),
    'average_efficiency': float(average_efficiency),
    'total_anomalies': int(total_anomalies),
    'machine_energy_distribution': machine_energy_distribution,
    'shift_energy_distribution': shift_energy_distribution,
  }


def analyze_machine(
  db: Session,
  machine_id: str,
  on_time_hours: float,
  off_time_hours: float,
) -> Dict:
  """Simulate machine analysis using dataset-level statistics."""
  on_time_hours = max(on_time_hours or 0.0, 0.0)
  off_time_hours = max(off_time_hours or 0.0, 0.0)

  total_records = db.query(func.count(EnergyRecord.id)).scalar() or 1
  total_energy = (
    db.query(func.coalesce(func.sum(EnergyRecord.energy_kwh), 0.0)).scalar() or 0.0
  )

  avg_tariff = (
    db.query(func.coalesce(func.avg(EnergyRecord.electricity_tariff), 0.0)).scalar()
    or 0.0
  )

  efficiency_expr = EnergyRecord.production_output / func.nullif(
    EnergyRecord.energy_kwh,
    0,
  )
  average_efficiency = (
    db.query(func.avg(efficiency_expr)).scalar()
    if db.query(EnergyRecord.id).first()
    else 0.0
  ) or 0.0

  anomaly_rate = (
    db.query(func.coalesce(func.avg(EnergyRecord.true_anomaly_label), 0.0)).scalar()
    or 0.0
  )

  machine_avg_energy = (
    db.query(func.avg(EnergyRecord.energy_kwh))
    .filter(EnergyRecord.machine_id == machine_id)
    .scalar()
  )

  if machine_avg_energy is None:
    base_energy_per_record = total_energy / float(total_records or 1)
  else:
    base_energy_per_record = float(machine_avg_energy or 0.0)

  estimated_energy = base_energy_per_record * on_time_hours
  estimated_cost = estimated_energy * avg_tariff
  estimated_efficiency = float(average_efficiency)

  anomaly_probability = float(anomaly_rate)

  if on_time_hours > 20:
    anomaly_probability += 0.15
  if off_time_hours < 4:
    anomaly_probability += 0.1
  if on_time_hours < 8 and off_time_hours >= 8:
    anomaly_probability *= 0.8

  anomaly_probability = max(0.0, min(1.0, anomaly_probability))

  if anomaly_probability > 0.7:
    message = 'High anomaly risk detected based on operating profile.'
  elif anomaly_probability > 0.4:
    message = 'Moderate anomaly risk; monitor machine closely.'
  else:
    message = 'Machine appears to be operating within normal parameters.'

  return {
    'machine_id': machine_id,
    'estimated_energy': float(estimated_energy),
    'estimated_cost': float(estimated_cost),
    'estimated_efficiency': float(estimated_efficiency),
    'anomaly_probability': float(anomaly_probability),
    'message': message,
  }

