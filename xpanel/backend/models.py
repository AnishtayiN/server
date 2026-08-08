from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from database import Base


class ProtocolType(str, enum.Enum):
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


class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"
    TRAFFIC_EXHAUSTED = "traffic_exhausted"


class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    is_super_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    users = relationship("User", back_populates="admin", cascade="all, delete-orphan")
    inbounds = relationship("Inbound", back_populates="admin", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    username = Column(String(50), index=True, nullable=False)
    uuid = Column(String(36), unique=True, index=True, nullable=False)
    protocol = Column(SQLEnum(ProtocolType), nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    
    # Limits
    traffic_limit_gb = Column(BigInteger, default=0)  # 0 means unlimited
    ip_limit = Column(Integer, default=0)  # 0 means unlimited
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    
    # Usage tracking
    traffic_used_bytes = Column(BigInteger, default=0)
    connection_count = Column(Integer, default=0)
    last_connected = Column(DateTime(timezone=True), nullable=True)
    
    # Configuration
    config = Column(JSON, default=dict)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    admin = relationship("Admin", back_populates="users")


class Inbound(Base):
    __tablename__ = "inbounds"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=False)
    tag = Column(String(50), unique=True, index=True, nullable=False)
    protocol = Column(SQLEnum(ProtocolType), nullable=False)
    port = Column(Integer, nullable=False)
    listen = Column(String(50), default="0.0.0.0")
    
    # Configuration
    settings = Column(JSON, default=dict)
    stream_settings = Column(JSON, default=dict)
    sniffing = Column(JSON, default={"enabled": True, "destOverride": ["http", "tls"]})
    
    # Status
    enabled = Column(Boolean, default=True)
    total_traffic_gb = Column(BigInteger, default=0)  # 0 means unlimited
    traffic_used_bytes = Column(BigInteger, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    admin = relationship("Admin", back_populates="inbounds")


class ServerLog(Base):
    __tablename__ = "server_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_type = Column(String(50), index=True)
    message = Column(Text)
    level = Column(String(20), default="INFO")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TrafficLog(Base):
    __tablename__ = "traffic_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    inbound_id = Column(Integer, ForeignKey("inbounds.id"), index=True)
    traffic_bytes = Column(BigInteger)
    direction = Column(String(10))  # 'upload' or 'download'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    inbound = relationship("Inbound")
