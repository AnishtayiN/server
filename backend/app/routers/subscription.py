from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone

from ..database import SessionLocal
from .. import models
from ..utils.links import LinkGenerator
from ..utils.subscription import SubscriptionBuilder

router = APIRouter(prefix="/api/sub", tags=["subscription"])

@router.get("/{sub_id}")
async def get_subscription(sub_id: str, request: Request):
    db = SessionLocal()
    try:
        db_client = db.query(models.Client).options(
            joinedload(models.Client.inbound)
        ).filter(
            models.Client.subscription_id == sub_id,
            models.Client.is_active == True
        ).first()
        
        if not db_client:
            raise HTTPException(404, "Subscription not found")
        
        if db_client.expiry_time:
            if db_client.expiry_time < datetime.now(timezone.utc):
                raise HTTPException(410, "Subscription expired")
        
        if db_client.traffic_limit_bytes > 0:
            if db_client.used_traffic_bytes >= db_client.traffic_limit_bytes:
                raise HTTPException(403, "Traffic limit exceeded")
        
        host = request.headers.get("host", "localhost")
        link = LinkGenerator.generate_link(db_client, db_client.inbound, host)
        
        if not link:
            raise HTTPException(500, "Cannot generate link")
        
        clients_data = [{
            "client": db_client,
            "inbound": db_client.inbound,
            "link": link,
            "host": host
        }]
        
        user_agent = request.headers.get("user-agent", "").lower()
        
        if "clash" in user_agent:
            content = SubscriptionBuilder.build_clash(clients_data)
            return PlainTextResponse(content, media_type="text/yaml")
        elif "sing-box" in user_agent or "hiddify" in user_agent:
            content = SubscriptionBuilder.build_singbox(clients_data)
            return PlainTextResponse(content, media_type="application/json")
        else:
            content = SubscriptionBuilder.build_v2ray(clients_data)
            return PlainTextResponse(content, media_type="text/plain")
            
    finally:
        db.close()

@router.get("/{sub_id}/info")
async def subscription_info(sub_id: str):
    db = SessionLocal()
    try:
        db_client = db.query(models.Client).filter(
            models.Client.subscription_id == sub_id
        ).first()
        
        if not db_client:
            raise HTTPException(404)
        
        return {
            "username": db_client.email,
            "used_traffic": db_client.used_traffic_bytes,
            "total_traffic": db_client.traffic_limit_bytes,
            "expire": db_client.expiry_time.isoformat() if db_client.expiry_time else None,
            "status": "active" if db_client.is_active else "inactive"
        }
    finally:
        db.close()
