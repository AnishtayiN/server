from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, timedelta, timezone

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_admin
from ..utils.links import LinkGenerator

router = APIRouter(prefix="/api/clients", tags=["clients"])

@router.get("", response_model=List[schemas.ClientResponse])
def list_all_clients(db: Session = Depends(get_db), _: models.Admin = Depends(get_current_admin)):
    clients = db.query(models.Client).options(joinedload(models.Client.inbound)).all()
    return clients

@router.post("/inbound/{inbound_id}", response_model=schemas.ClientResponse, status_code=201)
def create_client(
    inbound_id: int,
    client: schemas.ClientCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_ib = db.query(models.Inbound).filter(models.Inbound.id == inbound_id).first()
    if not db_ib:
        raise HTTPException(status_code=404, detail="Inbound not found")
    
    if db.query(models.Client).filter(models.Client.email == client.email).first():
        raise HTTPException(status_code=400, detail="Email already exists")
    
    expiry = None
    if client.expiry_days:
        expiry = datetime.now(timezone.utc) + timedelta(days=client.expiry_days)
    
    db_client = models.Client(
        inbound_id=inbound_id,
        email=client.email,
        password=client.password,
        traffic_limit_bytes=client.traffic_limit_gb * 1024**3,
        expiry_time=expiry
    )
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_client(
    client_id: int,
    data: schemas.ClientUpdate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    if data.traffic_limit_gb is not None:
        db_client.traffic_limit_bytes = data.traffic_limit_gb * 1024**3
    if data.expiry_days is not None:
        db_client.expiry_time = datetime.now(timezone.utc) + timedelta(days=data.expiry_days)
    if data.is_active is not None:
        db_client.is_active = data.is_active
    if data.reset_traffic:
        db_client.used_traffic_bytes = 0
    
    db.commit()
    db.refresh(db_client)
    return db_client

@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(db_client)
    db.commit()

@router.get("/{client_id}/links")
def get_client_links(
    client_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_client = db.query(models.Client).options(
        joinedload(models.Client.inbound)
    ).filter(models.Client.id == client_id).first()
    
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    host = "your-server.com"
    link = LinkGenerator.generate_link(db_client, db_client.inbound, host)
    
    return {
        "email": db_client.email,
        "link": link,
        "subscription_id": db_client.subscription_id,
        "subscription_url": f"https://{host}/api/sub/{db_client.subscription_id}",
        "inbound": {
            "protocol": db_client.inbound.protocol,
            "port": db_client.inbound.port,
        }
    }
