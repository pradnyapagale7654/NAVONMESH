import os
from typing import Any, Dict

from dotenv import load_dotenv

try:
  # The Groq SDK will be available after installing `groq` from requirements.txt.
  from groq import Groq  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
  Groq = None  # type: ignore[assignment]

load_dotenv()


def generate_recommendation(prediction_data: Dict[str, Any]) -> str:
  """Generate AI recommendation text using Groq.

  Expects GROQ_API_KEY in environment. If not configured, returns a safe fallback string.
  """
  api_key = os.getenv('GROQ_API_KEY')
  model_name = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')

  if Groq is None or not api_key:
    return 'Groq is not configured (missing GROQ_API_KEY).'

  anomaly_status = prediction_data.get('anomaly_status', 'Normal')
  efficiency_score = prediction_data.get('efficiency_score', 0)
  energy_wasted = prediction_data.get('energy_wasted', 0)
  predicted_cost = prediction_data.get('predicted_cost', 0)
  machine_id = prediction_data.get('machine_id', 'Unknown')

  prompt = (
    f"Machine ID: {machine_id}. "
    f"Anomaly status: {anomaly_status}. "
    f"Efficiency score: {efficiency_score}. "
    f"Energy wasted (kWh): {energy_wasted}. "
    f"Predicted energy cost (INR): {predicted_cost}. "
    "Suggest practical steps to reduce energy consumption and improve efficiency in manufacturing machines. "
    "Provide a concise recommendation (3-6 bullet points) with actionable maintenance/operations suggestions."
  )

  try:
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
      model=model_name,
      messages=[
        {
          'role': 'system',
          'content': 'You are an industrial energy optimization assistant for manufacturing plants.',
        },
        {'role': 'user', 'content': prompt},
      ],
      temperature=0.2,
      max_tokens=220,
    )
    content = response.choices[0].message.content
    return (content or '').strip() or 'No recommendation generated.'
  except Exception:
    return 'Groq recommendation service is currently unavailable.'

