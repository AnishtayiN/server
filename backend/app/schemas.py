from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

# ============ Inbound Schemas ============
class InboundCreate(BaseModel):
    tag: str = Field(..., min_length=2, max_length=50)
    protocol: str = Field(..., pattern="^(vless|vmess|trojan|shadowsocks)$")
    port: int = Field(..., gt=0, lt=65536)
    network: str = Field(default="tcp", pattern="^(tcp|ws|grpc|http)$")
    security: str = Field(default="tls", pattern="^(tls|reality|none)$")
    sni: Optional[str] = None
    flow: Optional[str] = None
    settings: Optional[Dict[str, Any]] = {}
    stream_settings: Optional[Dict[str, Any]] = {}

class InboundUpdate(BaseModel):
    port: Optional[int] = None
    network: Optional[str] = None
    security: Optional[str] = None
    sni: Optional[str] = None
    flow: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    stream_settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class InboundResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tag: str
    protocol: str
    port: int
    network: str
    security: str
    sni: Optional[str] = None
    flow: Optional[str] = None
    settings: Dict[str, Any]
    stream_settings: Dict[str, Any]
    is_active: bool
    created_at: datetime
    clients_count: Optional[int] = 0

# ============ Client Schemas ============
class ClientCreate(BaseModel):
    email: str = Field(..., min_length=2, max_length=100)
    traffic_limit_gb: int = Field(default=0, ge=0)
    expiry_days: Optional[int] = Field(default=None, ge=1)
    password: Optional[str] = None

class ClientUpdate(BaseModel):
    traffic_limit_gb: Optional[int] = None
    expiry_days: Optional[int] = None
    is_active: Optional[bool] = None
    reset_traffic: Optional[bool] = False

class ClientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    inbound_id: int
    email: str
    uuid_str: str
    subscription_id: str
    password: Optional[str] = None
    traffic_limit_bytes: int
    used_traffic_bytes: int
    expiry_time: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    inbound: Optional[InboundResponse] = None

# ============ User (Admin) Schemas ============
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    is_active: bool
    created_at: datetime

# ============ System Schemas ============
class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_inbounds: int
    total_traffic_bytes: int
    used_traffic_bytes: int
    cpu_percent: float
    memory_percent: float
    uptime_seconds: float
