import pytest
import asyncio

from src.domain.services.record_match import record_match, RecordMatchError


class DummyPlayerRepo:
    def __init__(self, players):
        self.players = players

    async def get_by_id(self, id):
        return self.players.get(id)

    async def update_with_version(self, id, expected_version, updates):
        doc = self.players.get(id)
        if not doc:
            return None
        if doc.get("version", 1) != expected_version:
            return None
        doc.update(updates)
        doc["version"] = expected_version + 1
        return doc


class DummyLeagueRepo:
    def __init__(self, leagues):
        self.leagues = leagues

    async def get_by_id(self, id):
        return self.leagues.get(id)


class DummyMatchRepo:
    def __init__(self):
        self.matches = {}

    async def get_by_external_id(self, external_id):
        return self.matches.get(external_id)

    async def create(self, data):
        if data.get("external_match_id") and data.get("external_match_id") in self.matches:
            return self.matches[data.get("external_match_id")]
        mid = "m-1"
        doc = {"_id": mid, **data}
        if data.get("external_match_id"):
            self.matches[data.get("external_match_id")] = doc
        return doc


class DummyPublisher:
    async def publish_match_result(self, topic, payload):
        return None


@pytest.mark.asyncio
async def test_record_match_success():
    pa = {"_id": "p1", "elo": 1500, "version": 1, "league_id": "l1"}
    pb = {"_id": "p2", "elo": 1500, "version": 1, "league_id": "l1"}
    players = {"p1": pa, "p2": pb}
    leagues = {"l1": {"_id": "l1", "k_factor": 32}}

    player_repo = DummyPlayerRepo(players)
    league_repo = DummyLeagueRepo(leagues)
    match_repo = DummyMatchRepo()
    publisher = DummyPublisher()

    match = await record_match("p1", "p2", "p1", "l1", "ext-1", player_repo, league_repo, match_repo, publisher)
    assert match.get("external_match_id") == "ext-1"
    # players updated in repo
    assert players["p1"]["version"] == 2
    assert players["p2"]["version"] == 2


@pytest.mark.asyncio
async def test_record_match_idempotent():
    pa = {"_id": "p1", "elo": 1500, "version": 1, "league_id": "l1"}
    pb = {"_id": "p2", "elo": 1500, "version": 1, "league_id": "l1"}
    players = {"p1": pa, "p2": pb}
    leagues = {"l1": {"_id": "l1", "k_factor": 32}}

    player_repo = DummyPlayerRepo(players)
    league_repo = DummyLeagueRepo(leagues)
    match_repo = DummyMatchRepo()
    publisher = DummyPublisher()

    # first call
    m1 = await record_match("p1", "p2", "p1", "l1", "ext-2", player_repo, league_repo, match_repo, publisher)
    # second call should return same stored match and not raise
    m2 = await record_match("p1", "p2", "p1", "l1", "ext-2", player_repo, league_repo, match_repo, publisher)
    assert m1 == m2


@pytest.mark.asyncio
async def test_record_match_players_different_league():
    pa = {"_id": "p1", "elo": 1500, "version": 1, "league_id": "l1"}
    pb = {"_id": "p2", "elo": 1500, "version": 1, "league_id": "l2"}
    players = {"p1": pa, "p2": pb}
    leagues = {"l1": {"_id": "l1", "k_factor": 32}}

    player_repo = DummyPlayerRepo(players)
    league_repo = DummyLeagueRepo(leagues)
    match_repo = DummyMatchRepo()
    publisher = DummyPublisher()

    with pytest.raises(Exception):
        await record_match("p1", "p2", "p1", "l1", None, player_repo, league_repo, match_repo, publisher)
