# Implementation Plan: 001-elo-rating-service

**Branch**: `feature/001-elo-rating-service` | **Date**: 2026-05-07 | **Spec**: [spec.md](spec.md#L1)  
**Input**: Feature specification from `/specs/001-elo-rating-service/spec.md`

## Summary

Implement an ELO-rating REST API using FastAPI (Python 3.11+), MongoDB for persistence, and Kafka for events. The service will follow hexagonal architecture (domain, application, infrastructure, interfaces), provide CRUD for `players` and `leagues`, an endpoint to register match results which recalculates ELO within league context, support RSQL queries for listings, expose `/health`, and publish `match.result.v1` and `player.updated.v1` events to Kafka. Configuration via `.env` and tests with `pytest` using mocks for infra.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, pydantic, motor (async MongoDB driver), aiokafka (or confluent-kafka-python async wrapper), python-dotenv, pytest, httpx (test client), rsql-parser (or custom RSQL translator)  
**Storage**: MongoDB (document model: players, leagues, matches, audit)  
**Testing**: pytest for unit tests; use pytest-mock and unittest.mock for adapter mocks  
**Target Platform**: Linux server (containerized)  
**Project Type**: Web service / HTTP API  
**Performance Goals**: Provide sub-500ms median latency for typical queries in dev infra; document production targets in Phase 1  
**Constraints**: Use async stack for I/O; ELO calculations must be deterministic and idempotent; players and matches must include UUID ids  
**Scale/Scope**: Initial scope: single service handling matches for one league namespace; design for horizontality later

## Constitution Check

GATE: Project constitution requires Clean Code, Python 3.11+, OpenAPI docs, hexagonal architecture and English code+docs. Implementation choices in this plan adhere to those constraints. Re-evaluate after design artifacts are generated.

## Project Structure

### Documentation (this feature)

```text
specs/001-elo-rating-service/
├── spec.md
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output: event schemas, API contracts
└── tasks.md             # Phase 2 output (generated later)
```

### Source Code (repository root)

```text
src/
├── domain/
│   ├── models/          # domain entities: Player, League, Match
│   └── services/        # core use-cases: RecordMatch, CalculateElo
├── application/
│   └── ports/            # interfaces for repositories, event publishers
├── infrastructure/
│   ├── persistence/      # MongoDB adapters
│   └── messaging/        # Kafka producers/consumers
├── interfaces/
│   └── api/              # FastAPI routers, schemas (pydantic)
tests/
├── unit/
├── integration/
└── contract/
```

**Structure Decision**: Use the above hexagonal layout. Keep domain logic free of framework code; adapters implement persistence/messaging. FastAPI app code lives in `interfaces/api` with minimal glue to application services.

## Phase 0: Research & Clarifications (deliverable: `research.md`)

1. Confirm defaults and basic rules (default Elo start value, default `k_factor`=32 — already chosen).  
2. Define idempotency policy for match registration (`external_match_id` uniqueness, dedupe window).  
3. Define concurrency control for rating updates (optimistic locking via match document or player version).  
4. Select Kafka schema format (JSON Schema or Avro) and registry approach.  
5. Select RSQL parser/translator library or document translation rules.  
6. Define minimal observability metrics and error codes mapping.

## Phase 1: Design & Contracts (deliverables: `data-model.md`, `contracts/`, `quickstart.md`)

1. Design domain models: `Player`, `League`, `Match` with required fields and constraints (make `league_id` mandatory on `Player` and `Match`).  
2. Draft API contracts (Pydantic schemas) for CRUD endpoints and `POST /matches`.  
3. Draft event schemas for `match.result.v1` and `player.updated.v1` (JSON Schema or Avro).  
4. Define repository port interfaces and messaging port interfaces.  
5. Create quickstart: env variables, run instructions, local Mongo/Kafka dev guidance.  
6. Re-run constitution check and update structure if needed.

## Phase 2: Implementation (deliverables: code + tests)

1. Scaffold project structure and basic FastAPI app with `/health` endpoint.  
2. Implement domain services: `calculate_elo()` and `RecordMatch` use-case with unit tests.  
3. Implement repository adapters (Mongo) with integration contract tests (mocked for unit tests).  
4. Implement Kafka producer adapter and publish `match.result.v1` on successful match processing.  
5. Implement API endpoints: players, leagues, matches; wire application services.  
6. Implement RSQL-based listing middleware/translator for queries.  
7. Add generic error object and error handlers for 4xx.  
8. Add configuration via `.env` and settings module.  
9. Add CI pipeline tasks for linting, unit tests, and static checks.

## Phase 3: Validation & Harden (deliverables: docs + tests)

1. Create contract tests for event schemas and API responses.  
2. Add observability: metrics (Prometheus), structured logs, and request tracing.  
3. Load-test critical endpoints and document performance baseline.  
4. Prepare deployment artifacts (Dockerfile, Kubernetes manifest sketch).

## Acceptance Criteria (from spec)

- CRUD endpoints for `players` and `leagues` implemented and tested.  
- `POST /matches` recalculates ELO deterministically and is idempotent per `external_match_id`.  
- Events published to Kafka with versioned topics and schemas.  
- OpenAPI docs available and accurate.  
- Unit tests cover domain logic; adapters are mockable in tests.

## Next Steps (immediate)

1. Generate `research.md` resolving the open items listed in Phase 0.  
2. Produce `data-model.md` and `contracts/` (event schemas + API pydantic schemas).  
3. Run `/speckit.tasks` to create `tasks.md` for implementation work.  

