from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas, auth

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(models.Admin).filter(
        models.Admin.username == request.username
    ).first()

    if not admin or not auth.verify_password(request.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not admin.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    token = auth.create_access_token(data={"sub": admin.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def get_me(current_admin: models.Admin = Depends(auth.get_current_admin)):
    return {"username": current_admin.username, "id": current_admin.id}
