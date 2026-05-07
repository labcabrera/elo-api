from __future__ import annotations
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Dict, Any


class MatchBase(BaseModel):
    league_id: UUID
    player_a_id: UUID
    player_b_id: UUID
    winner_id: Optional[UUID] = None
    external_match_id: Optional[str] = None


class MatchCreate(MatchBase):
    pass


class MatchRead(MatchBase):
    id: UUID = Field(..., alias="_id")
    elo_before: Optional[Dict[str, float]] = None
    elo_after: Optional[Dict[str, float]] = None
    created_at: Optional[str] = None

    class Config:
        allow_population_by_field_name = True
