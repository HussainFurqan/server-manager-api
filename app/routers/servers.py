# app/routers/servers.py
from fastapi import APIRouter, Depends, HTTPException
from psycopg_pool import AsyncConnectionPool
from app.db import get_pool
from app.models import ServerOut
from fastapi import Query

router = APIRouter(prefix="/servers", tags=["servers"])

@router.get("", response_model=list[ServerOut])
async def list_servers(
    pool: AsyncConnectionPool = Depends(get_pool),
    datacenter_id: int | None = Query(None),
    sort: str | None = Query(None, pattern="^(id|hostname|created_at)$")
):
    query = """
        SELECT id, hostname, configuration, datacenter_id, created_at, modified_at
        FROM public.server
    """
    params = []
    if datacenter_id is not None:
        query += " WHERE datacenter_id = %s"
        params.append(datacenter_id)
    if sort:
        query += f" ORDER BY {sort}"
    else:
        query += " ORDER BY id"

    async with pool.connection() as conn:
        cur = await conn.execute(query, tuple(params))
        rows = await cur.fetchall()
    return rows


@router.get("/{server_id}", response_model=ServerOut, summary="Get one server by ID")
async def get_server(server_id: int, pool: AsyncConnectionPool = Depends(get_pool)):
    async with pool.connection() as conn:
        cur = await conn.execute("""
            SELECT id, hostname, configuration, datacenter_id, created_at, modified_at
            FROM public.server
            WHERE id = %s;
        """, (server_id,))
        row = await cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Server not found")
    return row
