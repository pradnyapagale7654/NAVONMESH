from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

from .db import Base


class EnergyRecord(Base):
  __tablename__ = 'energy_records'

  id = Column(Integer, primary_key=True, index=True)
  machine_id = Column(String, index=True)
  machine_model = Column(String)
  rated_capacity_kw = Column(Float)
  contract_demand_kw = Column(Float)
  timestamp = Column(DateTime, index=True)
  shift = Column(String)
  operator_id = Column(String)
  power_kw = Column(Float)
  energy_kwh = Column(Float)
  load_percent = Column(Float)
  power_factor = Column(Float)
  temperature = Column(Float)
  ambient_temperature = Column(Float)
  production_output = Column(Float)
  operating_status = Column(String)
  idle_flag = Column(Boolean)
  electricity_tariff = Column(Float)
  maintenance_cost = Column(Float)
  co2_emission = Column(Float)
  true_anomaly_label = Column(Integer)
  downtime_minutes = Column(Float)

