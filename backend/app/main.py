from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, SessionLocal, Base
from .routers import auth, users, system, inbounds, clients, subscription
from .auth import init_default_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        init_default_admin(db)
    finally:
        db.close()
    yield

app = FastAPI(title="AnishtayiN Panel API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(system.router)
app.include_router(inbounds.router)
app.include_router(clients.router)
app.include_router(subscription.router)

@app.get("/api/health")
def root():
    return {"message": "AnishtayiN API is running"}
