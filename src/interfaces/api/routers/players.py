from fastapi import APIRouter, HTTPException, status
from typing import Dict
from uuid import UUID
from src.interfaces.api.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate
from src.application.settings import settings
from src.infrastructure.persistence.player_repository import player_repository

router = APIRouter()


@router.post("/", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
async def create_player(payload: PlayerCreate):
    data = payload.dict()
    if data.get("elo") is None:
        data["elo"] = settings.DEFAULT_ELO
    # ensure league_id stored as string
    data["league_id"] = str(data["league_id"]) if data.get("league_id") else None
    doc = await player_repository.create(data)
    return doc


@router.get("/{player_id}", response_model=PlayerRead)
async def get_player(player_id: UUID):
    doc = await player_repository.get_by_id(str(player_id))
    if not doc:
        raise HTTPException(status_code=404, detail={"code": "PLAYER_NOT_FOUND", "message": "Player not found"})
    return doc


@router.get("/", response_model=list[PlayerRead])
async def list_players():
    docs = await player_repository.list()
    return docs


@router.put("/{player_id}", response_model=PlayerRead)
async def update_player(player_id: UUID, payload: PlayerUpdate):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    if not updates:
        return await player_repository.get_by_id(str(player_id))
    doc = await player_repository.update(str(player_id), updates)
    if not doc:
        raise HTTPException(status_code=404, detail={"code": "PLAYER_NOT_FOUND", "message": "Player not found"})
    return doc


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: UUID):
    await player_repository.delete(str(player_id))
    return None
