import logging
import os

import pandas as pd
from sqlalchemy import inspect, text

from .db import engine

logger = logging.getLogger(__name__)


def _get_dataset_path() -> str:
  base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
  return os.path.join(base_dir, 'dataset', 'energy_dataset.csv')


def load_csv_to_db() -> None:
  """Create SQLite database and import CSV into `energy_records` table.

  - Detects all columns dynamically from the CSV.
  - Creates the table if it does not exist.
  - Skips import when the table already contains records.
  """
  dataset_path = _get_dataset_path()

  if not os.path.exists(dataset_path):
    msg = 'Please place energy_dataset.csv inside dataset folder'
    logger.error(msg)
    print(msg)
    return

  inspector = inspect(engine)
  table_exists = inspector.has_table('energy_records')

  if table_exists:
    # Check if table already has rows; if so, avoid duplicate loading.
    with engine.connect() as conn:
      count = conn.execute(text('SELECT COUNT(*) FROM energy_records')).scalar() or 0
    if count > 0:
      logger.info('energy_records already contains %s rows; skipping CSV import.', count)
      return

  logger.info('Loading CSV dataset from %s', dataset_path)
  df = pd.read_csv(dataset_path)

  if df.empty:
    logger.warning('CSV dataset is empty; no rows imported.')
    return

  # Let pandas / SQLite infer the schema directly from the CSV columns.
  # If the table already exists but is empty, replace it so the schema matches the CSV exactly.
  if_exists_mode = 'replace' if table_exists else 'fail'

  df.to_sql('energy_records', engine, if_exists=if_exists_mode, index=False)

  logger.info('Database created and dataset imported successfully.')
  print('Database created and dataset imported successfully')

