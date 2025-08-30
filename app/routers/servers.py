# app/routers/servers.py
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg_pool import AsyncConnectionPool
from app.db import get_pool
from app.models import ServerOut, ServerIn, ServerUpdate

router = APIRouter(prefix="/servers", tags=["servers"])

@router.get("", response_model=list[ServerOut], summary="List all servers")
async def list_servers(
    pool: AsyncConnectionPool = Depends(get_pool),
    datacenter_id: int | None = Query(None),
    sort: str | None = Query(None, pattern="^(id|hostname|created_at)$"),
):
    query = """
        SELECT id, hostname, configuration, datacenter_id, created_at, modified_at
        FROM public.server
    """
    params: list = []
    clauses: list[str] = []
    if datacenter_id is not None:
        clauses.append("datacenter_id = %s")
        params.append(datacenter_id)
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += f" ORDER BY {sort or 'id'}"

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

@router.post("", response_model=ServerOut, status_code=201, summary="Create a new server")
async def create_server(payload: ServerIn, pool: AsyncConnectionPool = Depends(get_pool)):
    async with pool.connection() as conn:
        try:
            cur = await conn.execute(
                """
                INSERT INTO public.server (hostname, configuration, datacenter_id)
                VALUES (%s, %s::jsonb, %s)
                RETURNING id, hostname, configuration, datacenter_id, created_at, modified_at
                """,
                (payload.hostname, json.dumps(payload.configuration), payload.datacenter_id),
            )
            row = await cur.fetchone()
            return row
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.put("/{server_id}", response_model=ServerOut, summary="Update a server (partial allowed)")
async def update_server(server_id: int, payload: ServerUpdate, pool: AsyncConnectionPool = Depends(get_pool)):
    # Build dynamic SET clause based on provided fields
    sets: list[str] = []
    params: list = []

    if payload.hostname is not None:
        sets.append("hostname = %s")
        params.append(payload.hostname)

    if payload.configuration is not None:
        sets.append("configuration = %s::jsonb")
        params.append(json.dumps(payload.configuration))

    if payload.datacenter_id is not None:
        sets.append("datacenter_id = %s")
        params.append(payload.datacenter_id)

    if not sets:
        raise HTTPException(status_code=400, detail="No fields to update")

    # always update modified_at
    sets.append("modified_at = (now() AT TIME ZONE 'UTC')")
    params.append(server_id)

    query = f"""
        UPDATE public.server
        SET {", ".join(sets)}
        WHERE id = %s
        RETURNING id, hostname, configuration, datacenter_id, created_at, modified_at
    """

    async with pool.connection() as conn:
        try:
            cur = await conn.execute(query, tuple(params))
            row = await cur.fetchone()
        except Exception as e:
            # e.g., invalid datacenter_id (FK) or unique hostname conflict
            raise HTTPException(status_code=400, detail=str(e))

    if not row:
        raise HTTPException(status_code=404, detail="Server not found")
    return row