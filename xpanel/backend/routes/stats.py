from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import psutil
import os
import subprocess
from datetime import datetime

from database import get_db
from models import Admin, User, Inbound, TrafficLog
from schemas import ServerStats, TrafficStats
from routes.auth import get_current_admin

router = APIRouter()


@router.get("/stats/server", response_model=ServerStats)
async def get_server_stats(
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)
    
    # Memory usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    memory_total = memory.total
    
    # Disk usage
    disk = psutil.disk_usage('/')
    disk_usage = disk.percent
    disk_total = disk.total
    
    # System uptime
    uptime = int(psutil.boot_time())
    
    # Check if Xray is running
    xray_running = False
    try:
        result = subprocess.run(['pgrep', '-f', 'xray'], capture_output=True, text=True)
        xray_running = bool(result.stdout.strip())
    except Exception:
        pass
    
    # Get user statistics
    result = await db.execute(select(func.count(User.id)).where(User.admin_id == current_admin.id))
    total_users = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(User.id)).where(
            User.admin_id == current_admin.id,
            User.status == "active"
        )
    )
    active_users = result.scalar() or 0
    
    # Active connections (simplified - would need actual connection tracking)
    active_connections = 0
    
    return ServerStats(
        cpu_usage=cpu_usage,
        memory_usage=memory_usage,
        memory_total=memory_total,
        disk_usage=disk_usage,
        disk_total=disk_total,
        uptime=uptime,
        xray_running=xray_running,
        active_connections=active_connections,
        total_users=total_users,
        active_users=active_users
    )


@router.get("/stats/traffic", response_model=list[TrafficStats])
async def get_traffic_stats(
    skip: int = 0,
    limit: int = 100,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.admin_id == current_admin.id)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    traffic_stats = []
    for user in users:
        traffic_limit_bytes = user.traffic_limit_gb * 1024 * 1024 * 1024 if user.traffic_limit_gb > 0 else 0
        percentage_used = 0
        if traffic_limit_bytes > 0:
            percentage_used = (user.traffic_used_bytes / traffic_limit_bytes) * 100
        
        # Simplified upload/download split (would need actual tracking)
        upload_bytes = user.traffic_used_bytes // 2
        download_bytes = user.traffic_used_bytes - upload_bytes
        
        traffic_stats.append(TrafficStats(
            user_id=user.id,
            username=user.username,
            traffic_used_bytes=user.traffic_used_bytes,
            traffic_limit_bytes=traffic_limit_bytes,
            upload_bytes=upload_bytes,
            download_bytes=download_bytes,
            percentage_used=min(percentage_used, 100)
        ))
    
    return traffic_stats


@router.get("/stats/user/{user_id}")
async def get_user_stats(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.admin_id == current_admin.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    traffic_limit_bytes = user.traffic_limit_gb * 1024 * 1024 * 1024 if user.traffic_limit_gb > 0 else 0
    percentage_used = 0
    if traffic_limit_bytes > 0:
        percentage_used = (user.traffic_used_bytes / traffic_limit_bytes) * 100
    
    return {
        "user_id": user.id,
        "username": user.username,
        "protocol": user.protocol.value,
        "status": user.status,
        "traffic_used_bytes": user.traffic_used_bytes,
        "traffic_used_gb": round(user.traffic_used_bytes / (1024**3), 2),
        "traffic_limit_bytes": traffic_limit_bytes,
        "traffic_limit_gb": user.traffic_limit_gb,
        "percentage_used": min(percentage_used, 100),
        "connection_count": user.connection_count,
        "last_connected": user.last_connected,
        "expiry_date": user.expiry_date,
        "days_remaining": None if not user.expiry_date else max(0, (user.expiry_date - datetime.utcnow()).days)
    }


@router.get("/logs/system")
async def get_system_logs(
    limit: int = 50,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    from models import ServerLog
    
    query = select(ServerLog).order_by(ServerLog.created_at.desc()).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "type": log.log_type,
            "message": log.message,
            "level": log.level,
            "timestamp": log.created_at
        }
        for log in logs
    ]


@router.post("/xray/restart")
async def restart_xray(
    current_admin: Admin = Depends(get_current_admin)
):
    """Restart Xray core service."""
    try:
        # This would typically use systemctl or direct process management
        subprocess.run(['systemctl', 'restart', 'xray'], check=True)
        return {"status": "success", "message": "Xray restarted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to restart Xray: {str(e)}")


@router.get("/xray/status")
async def get_xray_status():
    """Get Xray core status."""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'xray'], capture_output=True, text=True)
        is_active = result.stdout.strip() == "active"
        
        result = subprocess.run(['systemctl', 'status', 'xray'], capture_output=True, text=True)
        status_output = result.stdout
        
        return {
            "active": is_active,
            "status": status_output
        }
    except Exception as e:
        return {
            "active": False,
            "status": f"Error checking status: {str(e)}"
        }
