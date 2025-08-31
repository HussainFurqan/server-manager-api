# app/db.py
import os
import contextlib
from typing import AsyncIterator
from fastapi import FastAPI
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

POOL: AsyncConnectionPool | None = None

def _dsn() -> str:
    # Default to local socket with current user (Homebrew-friendly)
    return os.getenv("DATABASE_URL", "postgresql:///servers_db")

def init_pool() -> AsyncConnectionPool:
    return AsyncConnectionPool(
        conninfo=_dsn(),
        min_size=1,
        max_size=5,
        kwargs={"row_factory": dict_row},
    )

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    global POOL
    POOL = init_pool()
    await POOL.open()
    try:
        yield
    finally:
        await POOL.close()

def get_pool() -> AsyncConnectionPool:
    assert POOL is not None, "DB pool not initialized"
    return POOL