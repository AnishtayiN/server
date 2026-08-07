from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import psutil
import time

from ..database import get_db
from .. import models, crud, schemas
from ..auth import get_current_admin

router = APIRouter(prefix="/api/system", tags=["system"])

START_TIME = time.time()

@router.get("/stats", response_model=schemas.SystemStats)
def get_stats(
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    stats = crud.get_system_stats(db)
    stats.cpu_percent = psutil.cpu_percent(interval=0.5)
    stats.memory_percent = psutil.virtual_memory().percent
    stats.uptime_seconds = time.time() - START_TIME
    return stats

@router.get("/health")
def health_check():
    return {"status": "ok"}
