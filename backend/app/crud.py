from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from . import models, schemas

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[models.Admin]:
    return db.query(models.Admin).offset(skip).limit(limit).all()

def get_user_by_username(db: Session, username: str) -> Optional[models.Admin]:
    return db.query(models.Admin).filter(models.Admin.username == username).first()

def create_admin(db: Session, user: schemas.UserCreate) -> models.Admin:
    from .auth import hash_password
    db_admin = models.Admin(
        username=user.username,
        hashed_password=hash_password(user.password)
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def delete_admin(db: Session, admin_id: int) -> bool:
    db_admin = db.query(models.Admin).filter(models.Admin.id == admin_id).first()
    if not db_admin:
        return False
    db.delete(db_admin)
    db.commit()
    return True

def get_system_stats(db: Session) -> schemas.SystemStats:
    total_admins = db.query(models.Admin).count()
    active_admins = db.query(models.Admin).filter(models.Admin.is_active == True).count()
    total_inbounds = db.query(models.Inbound).count()
    
    total_traffic = sum(c.traffic_limit_bytes for c in db.query(models.Client).all())
    used_traffic = sum(c.used_traffic_bytes for c in db.query(models.Client).all())

    return schemas.SystemStats(
        total_users=total_admins,
        active_users=active_admins,
        total_inbounds=total_inbounds,
        total_traffic_bytes=total_traffic,
        used_traffic_bytes=used_traffic,
        cpu_percent=0.0,
        memory_percent=0.0,
        uptime_seconds=0.0
    )
