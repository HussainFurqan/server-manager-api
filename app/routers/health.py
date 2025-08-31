# app/routers/health.py
from fastapi import APIRouter

router = APIRouter(tags=["status"])

@router.get("/health", summary="Service status check")
async def health():
    return {"status": "ok"}

