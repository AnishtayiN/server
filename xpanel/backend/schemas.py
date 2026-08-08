from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ProtocolEnum(str, Enum):
    VMESS = "vmess"
    VLESS = "vless"
    TROJAN = "trojan"
    SHADOWSOCKS = "shadowsocks"
    WIREGUARD = "wireguard"
    HYSTERIA = "hysteria"
    HTTP = "http"
    TUNNEL = "tunnel"
    MIXED = "mixed"
    TUN = "tun"


class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"
    TRAFFIC_EXHAUSTED = "traffic_exhausted"


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    email: Optional[EmailStr] = None
    is_super_admin: bool = False


class AdminUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class AdminResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    is_super_admin: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True


# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    protocol: ProtocolEnum
    traffic_limit_gb: int = 0
    ip_limit: int = 0
    expiry_days: Optional[int] = None
    notes: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    traffic_limit_gb: Optional[int] = None
    ip_limit: Optional[int] = None
    expiry_date: Optional[datetime] = None
    status: Optional[UserStatusEnum] = None
    notes: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class UserResponse(BaseModel):
    id: int
    username: str
    uuid: str
    protocol: str
    status: str
    traffic_limit_gb: int
    ip_limit: int
    expiry_date: Optional[datetime]
    traffic_used_bytes: int
    connection_count: int
    last_connected: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Inbound Schemas
class InboundCreate(BaseModel):
    tag: str = Field(..., min_length=1, max_length=50)
    protocol: ProtocolEnum
    port: int = Field(..., ge=1, le=65535)
    listen: str = "0.0.0.0"
    settings: Optional[Dict[str, Any]] = None
    stream_settings: Optional[Dict[str, Any]] = None
    sniffing: Optional[Dict[str, Any]] = None
    total_traffic_gb: int = 0


class InboundUpdate(BaseModel):
    tag: Optional[str] = Field(None, min_length=1, max_length=50)
    port: Optional[int] = Field(None, ge=1, le=65535)
    listen: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    stream_settings: Optional[Dict[str, Any]] = None
    sniffing: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None
    total_traffic_gb: Optional[int] = None


class InboundResponse(BaseModel):
    id: int
    tag: str
    protocol: str
    port: int
    listen: str
    settings: Dict[str, Any]
    stream_settings: Dict[str, Any]
    sniffing: Dict[str, Any]
    enabled: bool
    total_traffic_gb: int
    traffic_used_bytes: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Stats and Monitoring Schemas
class ServerStats(BaseModel):
    cpu_usage: float
    memory_usage: float
    memory_total: int
    disk_usage: float
    disk_total: int
    uptime: int
    xray_running: bool
    active_connections: int
    total_users: int
    active_users: int


class TrafficStats(BaseModel):
    user_id: int
    username: str
    traffic_used_bytes: int
    traffic_limit_bytes: int
    upload_bytes: int
    download_bytes: int
    percentage_used: float


class ConnectionLog(BaseModel):
    id: int
    user_id: int
    username: str
    ip_address: str
    inbound_tag: str
    timestamp: datetime
    bytes_transferred: int


# Subscription Schema
class SubscriptionLink(BaseModel):
    user_id: int
    username: str
    subscription_url: str
    clash_link: Optional[str] = None
    base64_link: Optional[str] = None
