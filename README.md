# Server Manager API

REST API to manage servers across datacenters using **FastAPI** and **PostgreSQL** (no ORM).  
Implements: health check, DB connectivity check, list servers, get by ID, create, update, delete.

## Tech Stack
- FastAPI (ASGI)
- Uvicorn (server)
- psycopg 3 (async, no ORM)
- PostgreSQL (JSONB for `configuration`)

---

## Prerequisites

- Python 3.11+
- PostgreSQL 16+ (local install; Homebrew/Postgres.app are fine)
- `psql` CLI on PATH

---

## Getting Started

### 1) Clone & open
```bash
git clone https://github.com/HussainFurqan/server-manager-api.git
cd server-manager-api
```

### 2) Create venv & install deps
```bash
chmod +x python-env.sh
./python-env.sh
```

### 3) Create DB and load schema + sample data
Create a local DB named `servers_db` and apply the SQL from `sql/`:

```bash
createdb servers_db
psql -d servers_db -f sql/schema.sql
psql -d servers_db -f sql/sample_data.sql
```

> If `psql` isn’t found with Homebrew’s keg-only Postgres, add:  
> `export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"`

### 4) Configure connection (optional)
By default the app uses the local socket:
```
postgresql:///servers_db
```
To override, set `DATABASE_URL`:
```bash
export DATABASE_URL="postgresql://<user>:<pass>@localhost:5432/servers_db"
```

### 5) Run the API
```bash
uvicorn app.main:app --reload --port 18080
```

- Swagger UI: http://127.0.0.1:18080/docs  
- ReDoc: http://127.0.0.1:18080/redoc  
- OpenAPI JSON: http://127.0.0.1:18080/openapi.json

---

## Project Structure

```
app/
  ├─ main.py                  # FastAPI app wiring (routers + lifespan)
  ├─ db.py                    # async connection pool (psycopg_pool)
  ├─ models.py                # Pydantic models (in/out)
  └─ routers/
     ├─ health.py             # /health
     ├─ dbcheck.py            # /db-check
     └─ servers.py            # /servers (CRUD)
sql/
  ├─ schema.sql               # tables from task brief
  └─ sample_data.sql          # example rows + sequence fixups
README.md
requirements.txt
```

---

## Endpoints (Quick Reference)

- `GET /health` – service status  
- `GET /db-check` – DB connectivity test (returns server time)  
- `GET /servers` – list all servers  
  - Optional: `?datacenter_id=1`, `?sort=hostname`  
- `GET /servers/{id}` – one server by ID  
- `POST /servers` – create server  
- `PUT /servers/{id}` – update server (partial allowed)  
- `DELETE /servers/{id}` – delete server (FK may block if linked in `switch_to_server`)

---

## Running Tests Manually (Notebook Option)
- Various examples of CURL commands to manually test all endpoints of the project are implemented in the (api-curl-calls.ipynb) notebook.

---

## Error Handling

- Standard `HTTPException` responses with `{"detail": "...message..."}`:
  - `404` – not found (e.g., `/servers/{id}` missing)
  - `400` – invalid input or DB constraint violations (e.g., bad `datacenter_id`)
  - `503` – `/db-check` if the database is not reachable
- Datetimes are returned as ISO-8601 strings by Pydantic.

---

## Design Decisions

**Why no ORM?**  
The task requires “without an ORM”. Using `psycopg` directly keeps SQL explicit and predictable.

**Async connection pool (`psycopg_pool`)**  
- One shared pool opened via FastAPI `lifespan`, injected with `Depends(get_pool)`.  
- Efficient, simple, and avoids per-request connection overhead.

**JSONB for `configuration`**  
- Matches requirement to use JSON.  
- Stored as `jsonb` so we can query/merge later if needed.  
- `json.dumps()` used for inserts/updates to be explicit.

**Separation of concerns**  
- `db.py` handles connectivity; routers don’t manage connections.  
- `models.py` defines request/response schemas (clean docs, robust validation).  
- Small, focused routers (`health`, `dbcheck`, `servers`).

**Minimal, readable error handling**  
- Raise `HTTPException` with DB error text for 400s.  
- No custom translation of DB messages to avoid hiding details or over-engineering.

**Optional filtering/sorting kept small**  
- `/servers` accepts `datacenter_id` and `sort` (id | hostname | created_at).  
- Enough to show capability without complicating the interface.

**Local PostgreSQL (no Docker)**  
- The brief doesn’t require Docker; using local Postgres keeps the setup straightforward on macOS.  
- SQL scripts (`schema.sql`, `sample_data.sql`) ensure the reviewer can reproduce the DB state.

**Commit history**  
- Work delivered incrementally (small steps: health → db-check → list → get → create → update → delete).  
- This makes the history easy to follow during review.

---

## Notes / Limitations

- No auth, pagination, or advanced JSON operations (out of scope per brief).
- Deleting a server that’s referenced by `switch_to_server` will 400 with a FK error.
