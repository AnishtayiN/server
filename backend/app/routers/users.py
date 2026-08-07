from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import models, schemas, crud, auth

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=List[schemas.UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    return crud.get_users(db, skip=skip, limit=limit)

@router.post("", response_model=schemas.UserResponse, status_code=201)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(auth.get_current_admin)
):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return crud.create_admin(db, user)

@router.delete("/{admin_id}", status_code=204)
def delete_user(
    admin_id: int,
    db: Session = Depends(get_db),
    current: models.Admin = Depends(auth.get_current_admin)
):
    if current.id == admin_id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    if not crud.delete_admin(db, admin_id):
        raise HTTPException(status_code=404, detail="User not found")
