import logging

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import Base, engine
from database.csv_to_db import load_csv_to_db
from ml.train_models import ensure_models_trained
from routes.analysis import router as analysis_router
from routes.dashboard import router as dashboard_router

# Ensure ORM models are imported so Base knows about tables before create_all().
import database.models  # noqa: F401,E402

load_dotenv()

logging.basicConfig(
  level=logging.INFO,
  format='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
)
logger = logging.getLogger('smart-energy-backend')

app = FastAPI(
  title='Smart Energy AI System Backend',
  version='0.1.0',
)

origins = [
  'http://localhost:5173',
  'http://127.0.0.1:5173',
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'],
)

app.include_router(dashboard_router)
app.include_router(analysis_router)


@app.on_event('startup')
async def on_startup() -> None:
  """Backend startup sequence: DB + CSV + ML models."""
  logger.info('Creating database (if not present).')
  # Ensure the SQLite file exists; actual table schema will be inferred from CSV.
  Base.metadata.create_all(bind=engine)

  logger.info('Attempting to load CSV dataset into database.')
  load_csv_to_db()

  logger.info('Ensuring ML models are trained (if missing).')
  ensure_models_trained()


@app.get('/health')
def health_check():
  return {'status': 'ok'}

