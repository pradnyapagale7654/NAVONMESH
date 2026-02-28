from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.db import get_db
from services.groq_service import generate_recommendation
from services.ml_service import run_full_analysis

router = APIRouter(prefix='/api', tags=['analysis'])


class MachineAnalysisRequest(BaseModel):
  machine_id: str = Field(..., description='Identifier of the machine to analyze.')
  on_time_hours: float = Field(..., ge=0, description='Planned on time in hours.')
  off_time_hours: float = Field(..., ge=0, description='Planned off time in hours.')


@router.post('/analyze')
def analyze_machine(payload: MachineAnalysisRequest, db: Session = Depends(get_db)):
  """Run ML-powered analysis and return Groq recommendations."""
  prediction = run_full_analysis(
    machine_id=payload.machine_id,
    on_time_hours=payload.on_time_hours,
    off_time_hours=payload.off_time_hours,
    db=db,
  )

  ai_text = generate_recommendation(prediction)

  return {
    'machine_id': prediction['machine_id'],
    'anomaly_status': prediction['anomaly_status'],
    'anomaly_score': prediction['anomaly_score'],
    'predicted_cost': prediction['predicted_cost'],
    'efficiency_score': prediction['efficiency_score'],
    'energy_wasted': prediction['energy_wasted'],
    'ai_recommendation': ai_text,
  }

