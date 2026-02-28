from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from services.energy_service import get_dashboard_stats
from services.ml_service import get_dashboard_ml_insights

router = APIRouter(prefix='/api', tags=['dashboard'])


@router.get('/dashboard')
def read_dashboard(db: Session = Depends(get_db)):
  """Return aggregated dashboard statistics for the frontend."""
  stats = get_dashboard_stats(db)
  ml = get_dashboard_ml_insights()

  # Requirement: average_efficiency and anomaly_count should be model-based.
  stats['average_efficiency_true'] = stats.get('average_efficiency', 0.0)
  ml_eff = float(ml.get('average_efficiency_ml', 0.0))
  if ml_eff > 0:
    stats['average_efficiency'] = ml_eff
  stats['anomaly_count'] = int(ml.get('anomaly_count', 0))

  return stats

