# app/routers/dbcheck.py
from fastapi import APIRouter, Depends
from psycopg_pool import AsyncConnectionPool
from app.db import get_pool

router = APIRouter(tags=["debug"])

@router.get("/db-check", summary="Check DB connectivity")
async def db_check(pool: AsyncConnectionPool = Depends(get_pool)):
    async with pool.connection() as conn:
        cur = await conn.execute("SELECT now() AS db_time;")
        row = await cur.fetchone()
    return {"ok": True, "db_time": row["db_time"]}
