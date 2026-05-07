from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class PlayerBase(BaseModel):
    id_external: Optional[str] = None
    name: str
    league_id: UUID
    elo: Optional[float] = None


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    name: Optional[str] = None
    elo: Optional[float] = None
    metadata: Optional[dict] = None


class PlayerRead(PlayerBase):
    id: UUID = Field(..., alias="_id")
    version: int = 1
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
