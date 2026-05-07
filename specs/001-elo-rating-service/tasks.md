# Tasks: ELO Rating Service (001-elo-rating-service)

## Phase 1 — Setup

- [ ] T001 Initialize Python project and tooling: create `pyproject.toml`, `tox.ini`, `setup.cfg`, and basic repo layout in `src/` and `tests/` (root files)
- [ ] T002 [P] Add development dependencies in `pyproject.toml`: `fastapi`, `uvicorn`, `pydantic`, `motor`, `aiokafka`, `python-dotenv`, `pytest`, `httpx`, `pytest-mock` (pyproject.toml)
- [ ] T003 Create `.env.example` with placeholder variables (`MONGO_URI`, `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_SCHEMA_REGISTRY`, `APP_ENV`, `DEFAULT_K_FACTOR`) (/.env.example)
- [ ] T004 Scaffold FastAPI app with entrypoint `src/interfaces/api/main.py` and add `/health` endpoint (src/interfaces/api/main.py)

## Phase 2 — Foundational (blocking prerequisites)

- [ ] T005 Implement settings module to load env vars using `python-dotenv` and pydantic `BaseSettings` (src/application/settings.py)
- [ ] T006 Define hexagonal ports for repositories and messaging (src/application/ports/repository.py, src/application/ports/messaging.py)
- [ ] T007 Create domain models skeletons: `Player`, `League`, `Match` (src/domain/models/player.py, src/domain/models/league.py, src/domain/models/match.py)
- [ ] T008 Implement basic MongoDB adapter interface and connection util using `motor` (src/infrastructure/persistence/mongo.py)
- [ ] T009 Implement Kafka producer adapter skeleton and configuration (src/infrastructure/messaging/producer.py)
- [ ] T010 Add project logging configuration and structured JSON logger (src/application/logging.py)

## Phase 3 — User Story: Manage players [US1]

- [ ] T011 [US1] [P] Implement `Player` repository port methods: create, get_by_id, update, delete, list with filters (src/application/ports/repository.py)
- [ ] T012 [US1] Implement Mongo adapter for `Player` repository (src/infrastructure/persistence/player_repository.py)
- [ ] T013 [US1] Add Pydantic schemas for Player API requests/responses (src/interfaces/api/schemas/player.py)
- [ ] T014 [US1] Implement FastAPI routers for `players` CRUD and wire to application services (src/interfaces/api/routers/players.py)
- [ ] T015 [US1] Write unit tests for domain `Player` model behaviors and `Player` use-cases mocking repository (tests/unit/domain/test_player.py)

## Phase 4 — User Story: Manage leagues [US2]

- [ ] T016 [US2] [P] Implement `League` repository port methods and Mongo adapter (src/infrastructure/persistence/league_repository.py)
- [ ] T017 [US2] Add Pydantic schemas for League (src/interfaces/api/schemas/league.py)
- [ ] T018 [US2] Implement FastAPI routers for `leagues` CRUD (src/interfaces/api/routers/leagues.py)
- [ ] T019 [US2] Write unit tests for league creation/update behaviors and `k_factor` default when missing (tests/unit/domain/test_league.py)

## Phase 5 — User Story: Register match & ELO calc [US3]

- [ ] T020 [US3] Implement `calculate_elo()` deterministic function and unit tests (src/domain/services/elo.py, tests/unit/domain/test_elo.py)
- [ ] T021 [US3] Implement `RecordMatch` use-case orchestrating repo reads, elo calc, writes, and event publish (src/domain/services/record_match.py)
- [ ] T022 [US3] Persist match records in Mongo with `elo_before` and `elo_after` snapshots (src/infrastructure/persistence/match_repository.py)
- [ ] T023 [US3] Implement Kafka event schema and publishing `match.result.v1` in producer adapter (src/infrastructure/messaging/producer.py)
- [ ] T024 [US3] Implement `/matches` endpoint with request schema and validation; wire to `RecordMatch` (src/interfaces/api/routers/matches.py)
- [ ] T025 [US3] Add idempotency handling for `external_match_id` (dedupe key) and tests for duplicate submission behavior (tests/unit/application/test_record_match_idempotency.py)

## Phase 6 — Cross-cutting & Queries

- [ ] T026 Implement generic 4xx error object and FastAPI exception handlers (src/interfaces/api/errors.py)
- [ ] T027 Implement RSQL -> Mongo filter translator and integrate into list endpoints (`q`, `page`, `size`) (src/application/rsql/translator.py)
- [ ] T028 Add paging helpers and standard response envelope for list endpoints (src/interfaces/api/pagination.py)

## Phase 7 — Tests, CI & Docs

- [ ] T029 [P] Write unit tests for all domain services (elo, record_match) and ensure high coverage for critical logic (tests/unit/...)
- [ ] T030 Add integration tests mocking Mongo and Kafka using fixtures and `httpx.AsyncClient` to exercise endpoints (tests/integration/...)
- [ ] T031 Setup CI workflow with lint, format, and pytest (/.github/workflows/ci.yml)
- [ ] T032 Ensure OpenAPI docs exposed and add README quickstart with env setup and run instructions (specs/001-elo-rating-service/quickstart.md, README.adoc)

## Phase 8 — Polish & Ops

- [ ] T033 Add Prometheus metrics and instrument match processing latency and success/failure counters (src/infrastructure/observability/metrics.py)
- [ ] T034 Add graceful shutdown and Kafka consumer/producer lifecycle management (src/infrastructure/messaging/consumer.py)
- [ ] T035 Create Dockerfile and development docker-compose with Mongo + Kafka for local testing (Dockerfile, docker-compose.yml)

## Dependencies

- Player and League domain tasks must be implemented before `RecordMatch` (T011/T012/T016/T017 → T020..T025).
- RSQL translator (T027) can be implemented in parallel with repository adapters (P) but must be stable before final API polish.

## Parallel execution examples

- Implement `players` CRUD (T011-T015) in parallel with `leagues` CRUD (T016-T019) and RSQL translator (T027).
- While domain services (T020,T021) are developed, write unit tests (T029) and OpenAPI docs (T032) in parallel.
