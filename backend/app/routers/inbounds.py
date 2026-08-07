from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas
from ..auth import get_current_admin

router = APIRouter(prefix="/api/inbounds", tags=["inbounds"])

@router.get("", response_model=List[schemas.InboundResponse])
def list_inbounds(db: Session = Depends(get_db), current_admin: models.Admin = Depends(get_current_admin)):
    inbounds = db.query(models.Inbound).all()
    result = []
    for ib in inbounds:
        resp = schemas.InboundResponse.model_validate(ib)
        resp.clients_count = len(ib.clients)
        result.append(resp)
    return result

@router.post("", response_model=schemas.InboundResponse, status_code=201)
def create_inbound(
    inbound: schemas.InboundCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    if db.query(models.Inbound).filter(models.Inbound.tag == inbound.tag).first():
        raise HTTPException(status_code=400, detail="Inbound tag already exists")
    
    if db.query(models.Inbound).filter(models.Inbound.port == inbound.port).first():
        raise HTTPException(status_code=400, detail="Port already in use")
    
    db_inbound = models.Inbound(**inbound.model_dump())
    db.add(db_inbound)
    db.commit()
    db.refresh(db_inbound)
    return db_inbound

@router.put("/{inbound_id}", response_model=schemas.InboundResponse)
def update_inbound(
    inbound_id: int,
    data: schemas.InboundUpdate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_ib = db.query(models.Inbound).filter(models.Inbound.id == inbound_id).first()
    if not db_ib:
        raise HTTPException(status_code=404, detail="Inbound not found")
    
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(db_ib, key, value)
    
    db.commit()
    db.refresh(db_ib)
    return db_ib

@router.delete("/{inbound_id}", status_code=204)
def delete_inbound(
    inbound_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_ib = db.query(models.Inbound).filter(models.Inbound.id == inbound_id).first()
    if not db_ib:
        raise HTTPException(status_code=404, detail="Inbound not found")
    db.delete(db_ib)
    db.commit()

@router.get("/{inbound_id}/clients", response_model=List[schemas.ClientResponse])
def list_clients(
    inbound_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(get_current_admin)
):
    db_ib = db.query(models.Inbound).filter(models.Inbound.id == inbound_id).first()
    if not db_ib:
        raise HTTPException(status_code=404, detail="Inbound not found")
    return db_ib.clients
