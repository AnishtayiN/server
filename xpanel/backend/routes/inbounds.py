from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models import Admin, Inbound, ProtocolType
from schemas import InboundCreate, InboundUpdate, InboundResponse
from routes.auth import get_current_admin

router = APIRouter()


@router.get("/inbounds", response_model=List[InboundResponse])
async def list_inbounds(
    skip: int = 0,
    limit: int = 100,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(Inbound).where(Inbound.admin_id == current_admin.id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    inbounds = result.scalars().all()
    
    return inbounds


@router.get("/inbounds/{inbound_id}", response_model=InboundResponse)
async def get_inbound(
    inbound_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Inbound).where(Inbound.id == inbound_id, Inbound.admin_id == current_admin.id)
    )
    inbound = result.scalar_one_or_none()
    
    if not inbound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inbound not found"
        )
    
    return inbound


@router.post("/inbounds", response_model=InboundResponse, status_code=status.HTTP_201_CREATED)
async def create_inbound(
    inbound_data: InboundCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    # Check if tag already exists
    result = await db.execute(select(Inbound).where(Inbound.tag == inbound_data.tag))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inbound tag already exists"
        )
    
    new_inbound = Inbound(
        admin_id=current_admin.id,
        tag=inbound_data.tag,
        protocol=getattr(ProtocolType, inbound_data.protocol.name),
        port=inbound_data.port,
        listen=inbound_data.listen,
        settings=inbound_data.settings or {},
        stream_settings=inbound_data.stream_settings or {},
        sniffing=inbound_data.sniffing or {"enabled": True, "destOverride": ["http", "tls"]},
        total_traffic_gb=inbound_data.total_traffic_gb
    )
    
    db.add(new_inbound)
    await db.commit()
    await db.refresh(new_inbound)
    
    return new_inbound


@router.put("/inbounds/{inbound_id}", response_model=InboundResponse)
async def update_inbound(
    inbound_id: int,
    inbound_data: InboundUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Inbound).where(Inbound.id == inbound_id, Inbound.admin_id == current_admin.id)
    )
    inbound = result.scalar_one_or_none()
    
    if not inbound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inbound not found"
        )
    
    if inbound_data.tag:
        # Check if new tag is taken
        result = await db.execute(select(Inbound).where(Inbound.tag == inbound_data.tag))
        existing = result.scalar_one_or_none()
        if existing and existing.id != inbound.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inbound tag already exists"
            )
        inbound.tag = inbound_data.tag
    
    if inbound_data.port:
        inbound.port = inbound_data.port
    
    if inbound_data.listen:
        inbound.listen = inbound_data.listen
    
    if inbound_data.settings is not None:
        inbound.settings = inbound_data.settings
    
    if inbound_data.stream_settings is not None:
        inbound.stream_settings = inbound_data.stream_settings
    
    if inbound_data.sniffing is not None:
        inbound.sniffing = inbound_data.sniffing
    
    if inbound_data.enabled is not None:
        inbound.enabled = inbound_data.enabled
    
    if inbound_data.total_traffic_gb is not None:
        inbound.total_traffic_gb = inbound_data.total_traffic_gb
    
    await db.commit()
    await db.refresh(inbound)
    
    return inbound


@router.delete("/inbounds/{inbound_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inbound(
    inbound_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Inbound).where(Inbound.id == inbound_id, Inbound.admin_id == current_admin.id)
    )
    inbound = result.scalar_one_or_none()
    
    if not inbound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inbound not found"
        )
    
    await db.delete(inbound)
    await db.commit()
    
    return None


@router.post("/inbounds/{inbound_id}/toggle", response_model=InboundResponse)
async def toggle_inbound(
    inbound_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Inbound).where(Inbound.id == inbound_id, Inbound.admin_id == current_admin.id)
    )
    inbound = result.scalar_one_or_none()
    
    if not inbound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inbound not found"
        )
    
    inbound.enabled = not inbound.enabled
    await db.commit()
    await db.refresh(inbound)
    
    return inbound
