# app/models.py
from typing import Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ServerOut(BaseModel):
    id: int
    hostname: str
    configuration: dict[str, Any]
    datacenter_id: int
    created_at: datetime
    modified_at: datetime

class ServerIn(BaseModel):
    hostname: str = Field(examples=["api1.local.lan"])
    datacenter_id: int = Field(examples=[1])
    configuration: dict[str, Any] = Field(default_factory=dict, examples=[{"user_limit": 20}])

class ServerUpdate(BaseModel):
    hostname: Optional[str] = Field(default=None, examples=["api1.local.lan"])
    datacenter_id: Optional[int] = Field(default=None, examples=[2])
    configuration: Optional[dict[str, Any]] = Field(default=None, examples=[{"user_limit": 25}])