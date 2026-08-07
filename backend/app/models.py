from sqlalchemy import Column, Integer, String, Boolean, DateTime, BigInteger, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from .database import Base

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Inbound(Base):
    __tablename__ = "inbounds"
    
    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String(50), unique=True, nullable=False, index=True)
    protocol = Column(String(20), nullable=False)
    port = Column(Integer, nullable=False)
    network = Column(String(20), default="tcp")
    security = Column(String(20), default="tls")
    sni = Column(String(255), nullable=True)
    flow = Column(String(50), nullable=True)
    settings = Column(JSON, default=dict)
    stream_settings = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    clients = relationship("Client", back_populates="inbound", cascade="all, delete-orphan")

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    inbound_id = Column(Integer, ForeignKey("inbounds.id"), nullable=False)
    email = Column(String(100), unique=True, nullable=False, index=True)
    uuid_str = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    subscription_id = Column(String(32), unique=True, default=lambda: uuid.uuid4().hex)
    
    vmess_id = Column(String(36), nullable=True)
    alter_id = Column(Integer, default=0)
    password = Column(String(255), nullable=True)
    cipher = Column(String(50), nullable=True)
    
    traffic_limit_bytes = Column(BigInteger, default=0)
    used_traffic_bytes = Column(BigInteger, default=0)
    expiry_time = Column(DateTime, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    inbound = relationship("Inbound", back_populates="clients")

class NodeConfig(Base):
    __tablename__ = "node_config"
    
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
