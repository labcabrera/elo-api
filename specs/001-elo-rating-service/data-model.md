# Data Model — ELO Rating Service

This document defines domain entities, field types, Mongo index recommendations, example documents, and mapping to API/Pydantic schemas.

## ERD (ASCII)

Players───< Matches >───Players
   │                      │
   └── belongs_to         └── stored as snapshot (elo_before/elo_after)
   |
   └── belongs_to League

## Entities

- Player
  - _id: UUID (primary key)
  - id_external: string | null (unique per league)
  - league_id: UUID (required)
  - name: string
  - elo: number (float, default 1500)
  - version: integer (optimistic lock, default 1)
  - metadata: object (free-form)
  - created_at: date-time
  - updated_at: date-time

- League
  - _id: UUID (primary key)
  - name: string
  - k_factor: number (float, default 32)
  - metadata: object
  - created_at: date-time
  - updated_at: date-time

- Match
  - _id: UUID (primary key)
  - external_match_id: string | null (optional dedupe key)
  - league_id: UUID (required)
  - player_a_id: UUID
  - player_b_id: UUID
  - winner_id: UUID | null
  - score: object | null
  - timestamp: date-time
  - elo_before: object { playerId: elo }
  - elo_after: object { playerId: elo }
  - created_at: date-time

## Mongo Index Recommendations

- `players` collection
  - Primary: `{ _id: 1 }`
  - Unique per-league external id: `{ league_id: 1, id_external: 1 }` (unique, sparse/partial to allow null)
  - Query support: `{ league_id: 1, elo: -1 }` for leaderboards

- `leagues` collection
  - Primary: `{ _id: 1 }`

- `matches` collection
  - Primary: `{ _id: 1 }`
  - Dedupe/index: `{ external_match_id: 1 }` (unique, sparse) — enforces idempotency when provided
  - Recent queries: `{ league_id: 1, timestamp: -1 }`

Example index creation (Mongo shell):

```js
db.players.createIndex({ league_id: 1, id_external: 1 }, { unique: true, partialFilterExpression: { id_external: { $exists: true } } })
db.players.createIndex({ league_id: 1, elo: -1 })
db.matches.createIndex({ external_match_id: 1 }, { unique: true, sparse: true })
db.matches.createIndex({ league_id: 1, timestamp: -1 })
```

## Pydantic / API Schema Mapping (overview)

- PlayerCreate
  - `id_external?: str`, `name: str`, `league_id: UUID`, `elo?: float` (default 1500)

- PlayerRead
  - `id: UUID`, `id_external?: str`, `name: str`, `league_id: UUID`, `elo: float`, `created_at`, `updated_at`

- LeagueCreate / LeagueRead
  - `name: str`, `k_factor?: float` (default 32)

- MatchCreate
  - `playerAId: UUID`, `playerBId: UUID`, `winnerId?: UUID | null`, `leagueId: UUID`, `externalMatchId?: string`, `timestamp?: date-time`

- MatchRead
  - `id`, `externalMatchId`, `leagueId`, `playerA`, `playerB`, `winnerId`, `eloBefore`, `eloAfter`, `timestamp`

## Sample Documents

Player (Mongo):

```json
{
  "_id": "11111111-1111-1111-1111-111111111111",
  "id_external": "ext-42",
  "league_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "name": "Alice",
  "elo": 1520.5,
  "version": 3,
  "metadata": {},
  "created_at": "2026-05-07T12:00:00Z",
  "updated_at": "2026-05-07T12:01:00Z"
}
```

Match (Mongo):

```json
{
  "_id": "22222222-2222-2222-2222-222222222222",
  "external_match_id": "match-20260507-0001",
  "league_id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "player_a_id": "11111111-1111-1111-1111-111111111111",
  "player_b_id": "33333333-3333-3333-3333-333333333333",
  "winner_id": "11111111-1111-1111-1111-111111111111",
  "elo_before": { "11111111-1111-1111-1111-111111111111": 1520.5, "33333333-3333-3333-3333-333333333333": 1480.0 },
  "elo_after": { "11111111-1111-1111-1111-111111111111": 1532.5, "33333333-3333-3333-3333-333333333333": 1468.0 },
  "timestamp": "2026-05-07T12:05:00Z",
  "created_at": "2026-05-07T12:05:00Z"
}
```

## Consistency & Concurrency Patterns

- Use optimistic locking on `players.version` when updating `elo`:
  - Read current `elo` and `version`, compute new `elo`, then `updateOne({ _id, version: current }, { $set: { elo: new, version: current+1 } })`.
  - On zero matched documents (version conflict), retry up to `MAX_RETRY_ATTEMPTS` with exponential backoff.
- When available, use MongoDB multi-document transactions (replica set) to atomically write `match` and update both `players` documents.

## Dedupe / Idempotency

- Enforce unique `external_match_id` (sparse unique index) on `matches` collection.
- Behavior: on duplicate insert attempt return existing record (200) and do not publish events again.
- Optionally maintain `dedupe_created_at` and a TTL index if purging dedupe entries is desired (configured via `DEDUP_TTL`).

## RSQL / Querying

- Whitelisted fields for RSQL queries (translate to Mongo filters):
  - players: `id`, `id_external`, `name`, `elo`, `league_id`, `created_at`
  - leagues: `id`, `name`, `k_factor`, `created_at`
  - matches: `id`, `external_match_id`, `league_id`, `player_a_id`, `player_b_id`, `winner_id`, `timestamp`

## Denormalization & Read Patterns

- Keep `elo` on `players` as source-of-truth. `matches` store `elo_before`/`elo_after` snapshots for history and auditing.
- Consider caching leaderboards per league (materialized collection or Redis) if read performance requires it.

## Implementation Mapping (tasks)

- T007,T011,T012: implement `Player` model and repository according to schema above.
- T016,T017: implement `League` model and repository.
- T022: implement `Match` persistence including unique index on `external_match_id`.
- T020,T021: implement ELO calculation and use optimistic locking/transactions per above.

---

If you want, I can now scaffold the repository packages and add the Pydantic schema files under `src/interfaces/api/schemas/` to match this model. Which next step do you want? (scaffold code / add schemas / run index creation examples)
