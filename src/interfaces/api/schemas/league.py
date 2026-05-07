from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


class LeagueBase(BaseModel):
    name: str
    k_factor: Optional[float] = None


class LeagueCreate(LeagueBase):
    pass


class LeagueUpdate(BaseModel):
    name: Optional[str] = None
    k_factor: Optional[float] = None


class LeagueRead(LeagueBase):
    id: UUID = Field(..., alias="_id")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
