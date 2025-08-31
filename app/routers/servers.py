# app/routers/servers.py
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg_pool import AsyncConnectionPool
from app.db import get_pool
from app.models import ServerOut, ServerIn, ServerUpdate

router = APIRouter(prefix="/servers", tags=["servers"])

@router.get(
    "",
    response_model=list[ServerOut],
    summary="List all servers",
    description="Returns all servers. Optional filtering by datacenter and sorting.",
    responses={200: {"description": "List of servers"}},
)
async def list_servers(
    pool: AsyncConnectionPool = Depends(get_pool),
    datacenter_id: int | None = Query(None, description="Filter by datacenter id"),
    sort: str | None = Query(None, pattern="^(id|hostname|created_at)$", description="Sort field"),
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

@router.get(
    "/{server_id}",
    response_model=ServerOut,
    summary="Get one server by ID",
    responses={
        200: {"description": "One server"},
        404: {"description": "Server not found"},
    },
)
async def get_server(server_id: int, pool: AsyncConnectionPool = Depends(get_pool)):
    async with pool.connection() as conn:
        cur = await conn.execute(
            """
            SELECT id, hostname, configuration, datacenter_id, created_at, modified_at
            FROM public.server
            WHERE id = %s;
            """,
            (server_id,),
        )
        row = await cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Server not found")
    return row

@router.post(
    "",
    response_model=ServerOut,
    status_code=201,
    summary="Create a new server",
    responses={
        201: {"description": "Server created"},
        400: {"description": "Invalid input (e.g., bad datacenter_id, malformed JSON)"},
    },
)
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
            # Pass through simple DB error text as required
            raise HTTPException(status_code=400, detail=str(e))

@router.put(
    "/{server_id}",
    response_model=ServerOut,
    summary="Update an existing server",
    responses={
        200: {"description": "Server updated"},
        400: {"description": "Invalid input (e.g., bad datacenter_id, malformed JSON)"},
        404: {"description": "Server not found"},
    },
)
async def update_server(server_id: int, payload: ServerUpdate, pool: AsyncConnectionPool = Depends(get_pool)):
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
            raise HTTPException(status_code=400, detail=str(e))

    if not row:
        raise HTTPException(status_code=404, detail="Server not found")
    return row

@router.delete(
    "/{server_id}",
    summary="Delete a server by ID",
    responses={
        200: {"description": "Server deleted"},
        400: {"description": "Delete blocked by foreign key constraint"},
        404: {"description": "Server not found"},
    },
)
async def delete_server(server_id: int, pool: AsyncConnectionPool = Depends(get_pool)):
    async with pool.connection() as conn:
        try:
            cur = await conn.execute(
                "DELETE FROM public.server WHERE id = %s RETURNING id;",
                (server_id,),
            )
            row = await cur.fetchone()
        except Exception as e:
            # e.g., FK constraint from switch_to_server
            raise HTTPException(status_code=400, detail=str(e))

    if not row:
        raise HTTPException(status_code=404, detail="Server not found")
    return {"deleted_id": row["id"]}
