# app/routers/dbcheck.py
from fastapi import APIRouter, Depends, HTTPException
from psycopg_pool import AsyncConnectionPool
from app.db import get_pool

router = APIRouter(tags=["status"])

@router.get(
    "/db-check",
    summary="Database connectivity check",
    responses={
        200: {"description": "Database reachable"},
        503: {"description": "Database not reachable"},
    },
)
async def db_check(pool: AsyncConnectionPool = Depends(get_pool)):
    try:
        async with pool.connection() as conn:
            cur = await conn.execute("SELECT now() AS db_time;")
            row = await cur.fetchone()
        return {"ok": True, "db_time": row["db_time"]}
    except Exception:
        raise HTTPException(status_code=503, detail="Database not reachable")

