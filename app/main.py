# app/main.py
from fastapi import FastAPI
from app.db import lifespan
from app.routers import health, dbcheck, servers

app = FastAPI(
    title="Server Manager API",
    version="0.1.0",
    description=(
        "REST API to manage servers across datacenters.\n\n"
        "- Status: `/health`, `/db-check`\n"
        "- Server(entity): list, get by id, create, update, delete\n"
    ),
    lifespan=lifespan,
)

# Include routers
app.include_router(health.router)
app.include_router(dbcheck.router)
app.include_router(servers.router)

