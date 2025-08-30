# app/main.py
from fastapi import FastAPI
from app.db import lifespan
from app.routers import dbcheck, servers, health

app = FastAPI(title="Server Manager API", version="0.1.0", lifespan=lifespan)

# Include routers
app.include_router(health.router)
app.include_router(dbcheck.router)
app.include_router(servers.router)
