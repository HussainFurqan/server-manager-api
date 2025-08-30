# app/models.py
from typing import Any
from datetime import datetime
from pydantic import BaseModel

class ServerOut(BaseModel):
    id: int
    hostname: str
    configuration: dict[str, Any]
    datacenter_id: int
    created_at: datetime
    modified_at: datetime
