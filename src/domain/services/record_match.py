from typing import Optional, Dict, Any
import asyncio
from src.application.ports.repository import PlayerRepository, LeagueRepository, MatchRepository
from src.application.ports.messaging import EventPublisher
from src.domain.services.elo import calculate_elo
from src.application.settings import settings


class RecordMatchError(Exception):
    pass


async def record_match(
    player_a_id: str,
    player_b_id: str,
    winner_id: Optional[str],
    league_id: str,
    external_match_id: Optional[str],
    player_repo: PlayerRepository,
    league_repo: LeagueRepository,
    match_repo: MatchRepository,
    publisher: EventPublisher,
) -> Dict[str, Any]:
    # Idempotency: if external_match_id provided and exists, return existing
    if external_match_id:
        existing = await match_repo.get_by_external_id(external_match_id)
        if existing:
            return existing

    # Validate league
    league = await league_repo.get_by_id(league_id)
    if not league:
        raise RecordMatchError("LEAGUE_NOT_FOUND")
    k = float(league.get("k_factor", settings.DEFAULT_K_FACTOR))

    # Load players
    pa = await player_repo.get_by_id(player_a_id)
    pb = await player_repo.get_by_id(player_b_id)
    if not pa or not pb:
        raise RecordMatchError("PLAYER_NOT_FOUND")

    # Ensure players belong to league
    if str(pa.get("league_id")) != str(league_id) or str(pb.get("league_id")) != str(league_id):
        raise RecordMatchError("PLAYERS_LEAGUE_MISMATCH")

    # Determine results
    if winner_id is None:
        result_a = 0.5
    elif str(winner_id) == str(player_a_id):
        result_a = 1.0
    elif str(winner_id) == str(player_b_id):
        result_a = 0.0
    else:
        raise RecordMatchError("INVALID_WINNER")

    elo_a_before = float(pa.get("elo", settings.DEFAULT_ELO))
    elo_b_before = float(pb.get("elo", settings.DEFAULT_ELO))

    new_a, new_b = calculate_elo(elo_a_before, elo_b_before, k=k, result_a=result_a)

    elo_before = {player_a_id: elo_a_before, player_b_id: elo_b_before}
    elo_after = {player_a_id: new_a, player_b_id: new_b}

    match_data = {
        "external_match_id": external_match_id,
        "league_id": league_id,
        "player_a_id": player_a_id,
        "player_b_id": player_b_id,
        "winner_id": winner_id,
        "elo_before": elo_before,
        "elo_after": elo_after,
    }

    # Persist match (handle Duplicate external_match_id inside repo)
    match_doc = await match_repo.create(match_data)

    # Update players with optimistic locking and retry
    max_attempts = int(getattr(settings, "MAX_RETRY_ATTEMPTS", 3))
    backoff_ms = int(getattr(settings, "RETRY_BACKOFF_MS", 100))

    async def update_player_with_retry(player_doc, new_elo):
        attempts = 0
        while attempts < max_attempts:
            current_version = int(player_doc.get("version", 1))
            updates = {"elo": float(new_elo)}
            updated = await player_repo.update_with_version(player_doc.get("_id"), current_version, updates)
            if updated:
                return updated
            attempts += 1
            await asyncio.sleep((backoff_ms * (2 ** (attempts - 1))) / 1000.0)
            # reload player_doc
            player_doc = await player_repo.get_by_id(player_doc.get("_id"))
        raise RecordMatchError("VERSION_CONFLICT")

    updated_pa = await update_player_with_retry(pa, new_a)
    updated_pb = await update_player_with_retry(pb, new_b)

    # Publish event (best-effort)
    try:
        await publisher.publish_match_result(settings.TOPIC_MATCH_RESULT, {
            "matchId": match_doc.get("_id"),
            "externalMatchId": external_match_id,
            "leagueId": league_id,
            "playerA": {"id": player_a_id, "eloBefore": elo_a_before, "eloAfter": new_a},
            "playerB": {"id": player_b_id, "eloBefore": elo_b_before, "eloAfter": new_b},
            "winnerId": winner_id,
        })
    except Exception:
        # log and continue; event publishing shouldn't block main flow here
        pass

    # return persisted match document
    return match_doc
