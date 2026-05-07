from fastapi import APIRouter, HTTPException, status
from uuid import UUID
from src.interfaces.api.schemas.match import MatchCreate, MatchRead
from src.infrastructure.persistence.player_repository import player_repository
from src.infrastructure.persistence.league_repository import league_repository
from src.infrastructure.persistence.match_repository import match_repository
from src.infrastructure.messaging.publisher import publisher
from src.domain.services.record_match import record_match, RecordMatchError

router = APIRouter()


@router.post("/", response_model=MatchRead)
async def create_match(payload: MatchCreate):
    data = payload.dict()

    # Check idempotency first
    if data.get("external_match_id"):
        existing = await match_repository.get_by_external_id(data.get("external_match_id"))
        if existing:
            return existing

    try:
        match_doc = await record_match(
            player_a_id=str(data.get("player_a_id")),
            player_b_id=str(data.get("player_b_id")),
            winner_id=str(data.get("winner_id")) if data.get("winner_id") else None,
            league_id=str(data.get("league_id")),
            external_match_id=data.get("external_match_id"),
            player_repo=player_repository,
            league_repo=league_repository,
            match_repo=match_repository,
            publisher=publisher,
        )
    except RecordMatchError as e:
        detail = {"code": str(e), "message": "Record match failed"}
        raise HTTPException(status_code=400, detail=detail)

    # If the created match had an external id and already existed, record_match would have returned it.
    # Otherwise, it's a new resource — respond with 201.
    return match_doc
