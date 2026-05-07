# Research & Decisions — ELO Rating Service

**Feature**: 001-elo-rating-service
**Date**: 2026-05-07

This document records concrete design decisions and recommended parameter values to resolve open clarifications in the specification.

## Defaults and configuration

- `DEFAULT_ELO`: 1500
- `DEFAULT_K_FACTOR`: 32
- `DEDUP_TTL`: 30d (default time-to-live for dedupe records, configurable via `DEDUP_TTL` env var)
- `MAX_RETRY_ATTEMPTS`: 3 (retry attempts for version-conflict retries)
- `RETRY_BACKOFF_MS`: 100 (base backoff in milliseconds, exponential)
- `IDEMPOTENCY_BEHAVIOR`: return existing resource with `200 OK` when `external_match_id` previously processed
- `EVENT_SCHEMA_FORMAT`: JSON Schema (recommended) — use Schema Registry for evolution; Avro may be adopted later if required.

Environment variables (examples):

- `MONGO_URI` — connection string
- `KAFKA_BOOTSTRAP_SERVERS` — comma-separated brokers
- `KAFKA_SCHEMA_REGISTRY` — schema registry URL (optional)
- `DEFAULT_K_FACTOR` — numeric
- `DEFAULT_ELO` — numeric
- `DEDUP_TTL` — duration (e.g., `30d`)
- `MAX_RETRY_ATTEMPTS`, `RETRY_BACKOFF_MS`
- `TOPIC_MATCH_RESULT` — default: `match.result.v1`
- `TOPIC_PLAYER_UPDATED` — default: `player.updated.v1`

## Idempotency (external_match_id)

- Behavior: If a request contains `external_match_id`, the service must ensure the request is idempotent.
  - On first submission: create `Match` record, compute & persist ELO changes, publish events, and return `201 Created` with resource.
  - On duplicate submission (same `external_match_id`): return the existing `Match` resource with `200 OK` and do not re-run ELO calculation or publish events again.

- Implementation notes:
  - Create a unique index on `matches.external_match_id` (sparse/partial if optional) to enforce uniqueness at DB level.
  - Use the `matches` collection as the dedupe store; no separate dedupe service required initially.
  - Optionally record a dedupe timestamp to allow purging via TTL index (`DEDUP_TTL`).

## Concurrency and consistency

- Strategy: Optimistic locking with a `version` integer field on `Player` documents.
  - Read player documents with `version` value.
  - When updating `elo`, issue atomic update conditional on `version` (e.g., `updateOne({_id, version: current}, {$set: {elo: new, version: current+1}})`).
  - If the update result indicates no documents modified (version conflict), retry up to `MAX_RETRY_ATTEMPTS` with exponential backoff starting at `RETRY_BACKOFF_MS`.
  - If retries exhausted, return `409 Conflict` with a meaningful error payload and a hint to retry client-side if applicable.

- When Mongo transactions are available (replica set), prefer a transaction to update multiple documents (e.g., writing `match` and updating two `player` documents together). Transactions reduce window for inconsistencies but are not strictly required if optimistic locking + retries are implemented.

## Data model & indexes (implementation hints)

- `players` collection:
  - fields: `_id` (UUID), `league_id` (UUID), `id_external` (optional), `name`, `elo` (float), `version` (int), `created_at`, `updated_at`, `metadata`
  - indexes:
    - `{league_id:1, id_external:1}` unique (enforce id_external per league)
    - `{_id:1}` primary

- `matches` collection:
  - fields: `_id` (UUID), `external_match_id` (optional), `league_id` (UUID), `player_a_id`, `player_b_id`, `winner_id` (nullable), `elo_before`, `elo_after`, `timestamp`, `created_at`
  - indexes:
    - `{external_match_id:1}` unique sparse
    - `{league_id:1, timestamp:-1}` for recent queries

- `leagues` collection:
  - fields: `_id` (UUID), `name`, `k_factor`, `created_at`, `updated_at`

## RSQL: allowed fields and examples

- Allowed fields for RSQL filters (initial scope):
  - `players`: `id`, `id_external`, `name`, `elo`, `league_id`, `created_at`
  - `leagues`: `id`, `name`, `k_factor`, `created_at`
  - `matches`: `id`, `external_match_id`, `league_id`, `player_a_id`, `player_b_id`, `winner_id`, `timestamp`

- Operators supported: `==, !=, =gt=, =lt=, =ge=, =le=, =in=, =out=` (translate to Mongo query operators)

- Examples:
  - `q=name=="Alice";league_id=="<uuid>"`
  - `q=elo=gt=1400;elo=lt=1600`

## Event schemas (minimal examples — JSON Schema)

- `match.result.v1` (simplified):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MatchResultV1",
  "type": "object",
  "properties": {
    "matchId": {"type":"string","format":"uuid"},
    "externalMatchId": {"type":["string","null"]},
    "leagueId": {"type":"string","format":"uuid"},
    "playerA": {"type":"object","properties":{"id":{"type":"string","format":"uuid"},"eloBefore":{"type":"number"},"eloAfter":{"type":"number"}},"required":["id","eloBefore","eloAfter"]},
    "playerB": {"type":"object","properties":{"id":{"type":"string","format":"uuid"},"eloBefore":{"type":"number"},"eloAfter":{"type":"number"}},"required":["id","eloBefore","eloAfter"]},
    "winnerId": {"type":["string","null"]},
    "timestamp": {"type":"string","format":"date-time"}
  },
  "required":["matchId","leagueId","playerA","playerB","timestamp"]
}
```

- `player.updated.v1` (simplified):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "PlayerUpdatedV1",
  "type": "object",
  "properties": {
    "playerId": {"type":"string","format":"uuid"},
    "leagueId": {"type":"string","format":"uuid"},
    "eloBefore": {"type":"number"},
    "eloAfter": {"type":"number"},
    "timestamp": {"type":"string","format":"date-time"}
  },
  "required":["playerId","leagueId","eloBefore","eloAfter","timestamp"]
}
```

## Observability / Ops

- Metrics to expose (Prometheus):
  - `elo_matches_processed_total{result="success|failure"}`
  - `elo_match_processing_duration_seconds` (histogram)
  - `elo_player_updates_total`

- Logging: structured JSON logs with `trace_id`/`request_id` from incoming header `X-Request-Id` (generate if absent). Log levels configured via env variable `LOG_LEVEL`.

- Tracing: recommend OpenTelemetry instrumentation (optional for Phase 1).

## Error handling

- Generic 4xx error object: `{ code: string, message: string, details?: object }` with documented codes, e.g. `PLAYER_NOT_FOUND`, `DUPLICATE_MATCH`, `VERSION_CONFLICT`.

## id_external semantics

- `id_external` is optional. If provided, it must be unique within the same `league_id`. Enforce with unique index on `{league_id, id_external}`.

## Implementation checklist (short)

- [ ] Add DB indexes for dedupe and id_external uniqueness.
- [ ] Implement optimistic locking helpers and retry logic.
- [ ] Implement JSON Schema files under `specs/001-elo-rating-service/contracts/` and wire to Kafka producer.
- [ ] Implement RSQL translator with whitelisted fields.
- [ ] Add Prometheus metrics instrumentation.

## Open questions (deferred)

- Consider Avro + Confluent Schema Registry if consumers require strict schema evolution guarantees.
- Decide whether to return `201` for duplicate submissions with same `external_match_id` (current recommendation: return existing with `200 OK`).
