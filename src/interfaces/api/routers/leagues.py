from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from src.interfaces.api.schemas.league import LeagueCreate, LeagueRead, LeagueUpdate
from src.infrastructure.persistence.league_repository import league_repository

router = APIRouter()


@router.post("/", response_model=LeagueRead, status_code=status.HTTP_201_CREATED)
async def create_league(payload: LeagueCreate):
    data = payload.dict()
    doc = await league_repository.create(data)
    return doc


@router.get("/{league_id}", response_model=LeagueRead)
async def get_league(league_id: UUID):
    doc = await league_repository.get_by_id(str(league_id))
    if not doc:
        raise HTTPException(status_code=404, detail={"code": "LEAGUE_NOT_FOUND", "message": "League not found"})
    return doc


@router.get("/", response_model=list[LeagueRead])
async def list_leagues():
    docs = await league_repository.list()
    return docs


@router.put("/{league_id}", response_model=LeagueRead)
async def update_league(league_id: UUID, payload: LeagueUpdate):
    updates = {k: v for k, v in payload.dict().items() if v is not None}
    doc = await league_repository.update(str(league_id), updates)
    if not doc:
        raise HTTPException(status_code=404, detail={"code": "LEAGUE_NOT_FOUND", "message": "League not found"})
    return doc


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_league(league_id: UUID):
    await league_repository.delete(str(league_id))
    return None
