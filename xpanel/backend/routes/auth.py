from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from typing import Optional
import uuid

from database import get_db
from models import Admin, User, ProtocolType, UserStatus
from schemas import (
    Token, AdminLogin, AdminCreate, AdminUpdate, AdminResponse,
    UserCreate, UserUpdate, UserResponse
)
from config import settings
from utils.security import verify_password, get_password_hash, create_access_token
from utils.xray_generator import generate_user_config, generate_subscription_link

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Admin:
    from jose import JWTError, jwt
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(Admin).where(Admin.username == username))
    admin = result.scalar_one_or_none()
    
    if admin is None:
        raise credentials_exception
    
    return admin


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.username == form_data.username))
    admin = result.scalar_one_or_none()
    
    if not admin or not verify_password(form_data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=access_token_expires
    )
    
    # Update last login
    admin.last_login = datetime.utcnow()
    await db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/admins", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin_data: AdminCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    # Check if username already exists
    result = await db.execute(select(Admin).where(Admin.username == admin_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(admin_data.password)
    new_admin = Admin(
        username=admin_data.username,
        password_hash=hashed_password,
        email=admin_data.email,
        is_super_admin=admin_data.is_super_admin
    )
    
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    
    return new_admin


@router.get("/admins/me", response_model=AdminResponse)
async def get_current_admin_info(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


@router.put("/admins/me", response_model=AdminResponse)
async def update_current_admin(
    admin_data: AdminUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    if admin_data.username:
        # Check if new username is taken
        result = await db.execute(select(Admin).where(Admin.username == admin_data.username))
        existing = result.scalar_one_or_none()
        if existing and existing.id != current_admin.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        current_admin.username = admin_data.username
    
    if admin_data.email:
        current_admin.email = admin_data.email
    
    if admin_data.password:
        current_admin.password_hash = get_password_hash(admin_data.password)
    
    await db.commit()
    await db.refresh(current_admin)
    
    return current_admin


# User Management Routes
@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[str] = None,
    protocol_filter: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    query = select(User).where(User.admin_id == current_admin.id)
    
    if status_filter:
        query = query.where(User.status == status_filter)
    
    if protocol_filter:
        query = query.where(User.protocol == protocol_filter)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()
    
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.admin_id == current_admin.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    # Generate UUID for the user
    user_uuid = str(uuid.uuid4())
    
    # Calculate expiry date if provided
    expiry_date = None
    if user_data.expiry_days:
        expiry_date = datetime.utcnow() + timedelta(days=user_data.expiry_days)
    
    # Generate protocol-specific config
    config = generate_user_config(
        protocol=user_data.protocol.value,
        uuid=user_uuid,
        config=user_data.config or {}
    )
    
    new_user = User(
        admin_id=current_admin.id,
        username=user_data.username,
        uuid=user_uuid,
        protocol=getattr(ProtocolType, user_data.protocol.name),
        traffic_limit_gb=user_data.traffic_limit_gb,
        ip_limit=user_data.ip_limit,
        expiry_date=expiry_date,
        config=config,
        notes=user_data.notes
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.admin_id == current_admin.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user_data.username:
        user.username = user_data.username
    
    if user_data.traffic_limit_gb is not None:
        user.traffic_limit_gb = user_data.traffic_limit_gb
    
    if user_data.ip_limit is not None:
        user.ip_limit = user_data.ip_limit
    
    if user_data.expiry_date:
        user.expiry_date = user_data.expiry_date
    
    if user_data.status:
        user.status = getattr(UserStatus, user_data.status.name)
    
    if user_data.notes:
        user.notes = user_data.notes
    
    if user_data.config:
        user.config = user_data.config
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.admin_id == current_admin.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    await db.delete(user)
    await db.commit()
    
    return None


@router.get("/users/{user_id}/subscription")
async def get_user_subscription(
    user_id: int,
    current_admin: Admin = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).where(User.id == user_id, User.admin_id == current_admin.id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    subscription_url = generate_subscription_link(user, settings.SUBSCRIPTION_HOST or "localhost", settings.SUBSCRIPTION_PORT)
    
    return {
        "user_id": user.id,
        "username": user.username,
        "subscription_url": subscription_url,
        "protocol": user.protocol.value
    }
