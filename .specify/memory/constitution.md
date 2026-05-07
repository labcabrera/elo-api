# Proyecto ELO Api Constitution
<!--
Sync Impact Report
- Version change: [CONSTITUTION_VERSION] -> 0.1.0
- Modified principles: placeholders replaced with concrete principles for code quality, API design,
	architecture, observability, and testing/CI.
- Added sections: Additional Constraints, Development Workflow.
- Removed sections: none.
- Templates requiring updates:
	- .specify/templates/plan-template.md: ⚠ pending (needs Constitution Check details aligned)
	- .specify/templates/spec-template.md: ⚠ pending
	- .specify/templates/tasks-template.md: ⚠ pending
	- .specify/templates/checklist-template.md: ⚠ pending
- Follow-up TODOs: Update templates to reference and enforce these principles; set ratification date.
-->

## Core Principles

### Maintainable and Readable Code (NON-NEGOTIABLE)
All source code MUST follow Clean Code principles: clear naming, small functions, type
annotations (Python 3.11+), and modular structure. Code MUST be documented, covered by
automated tests, and pass configured linters and formatters before merging.

### API Design and Documentation
APIs MUST be RESTful and use camelCase for request/response fields. All public endpoints
MUST be documented with OpenAPI; generated code and documentation MUST be in English. API
contracts (paths, schemas, status codes) are the source of truth for integration tests.

### Architecture and Separation of Concerns
The codebase MUST follow a clean architecture: packages `domain`, `application`,
`infrastructure`, and `interfaces`. Layers may only depend inward; no cyclic dependencies.
Use dependency inversion to keep domain logic framework-agnostic and independently testable.

### Reliability and Observability
Services MUST expose health and readiness endpoints, structured logging, and basic metrics.
Error handling MUST be consistent and provide safe, machine-readable error payloads. Integrate
retry/backoff where appropriate and document failure modes for external systems (MongoDB,
Kafka).

### Testing and Continuous Integration
Adopt test-first practices: unit tests for domain logic, integration tests for service contracts,
and contract tests for public APIs. CI gates MUST run linters, type checks, unit and integration
tests; merging to main is blocked until CI passes.

## Additional Constraints

- Language/runtime: Python 3.11+ (use modern language features and type hints).
- Frameworks & services: FastAPI for HTTP APIs, MongoDB for primary storage, Kafka for eventing.
- Process manager & packaging: use the declared project process manager `uv` and keep
	dependencies in `pyproject.toml` as the single source of truth for builds and deployments.
- Deployment readiness: container-friendly configuration, environment-variable driven config,
	and explicit secrets handling (do not store secrets in source).

## Development Workflow

- Repository layout MUST follow the clean architecture packages above and include `tests/unit`,
	`tests/integration`, and `tests/contract` directories for respective test types.
- Pull requests: include description, related issue, and checklist verifying constitution gates
	(linters, type checks, tests, OpenAPI compatibility where relevant). PRs require at least
	two approvals from maintainers for non-trivial changes and green CI.
- Branching: feature branches prefixed with `feature/` or issue number; release branches when
	preparing production releases. Commit messages SHOULD follow conventional commits.
- Code quality: enforce `pytest`, `ruff`/`flake8`, `black`, and `mypy` in CI; failures block merges.

## Governance

1. Constitution supersedes local conventions; any deviation requires an explicit exception
	 documented in the PR and approved by maintainers.
2. Amendments: propose changes via a PR that references an issue describing rationale,
	 migration steps, and tests. Amendments require at least two maintainer approvals and
	 passing CI. Major changes (breaking governance or principle removals) MUST include a
	 migration plan and a public changelog entry.
3. Versioning: the constitution uses semantic versioning `MAJOR.MINOR.PATCH`:
	 - MAJOR: incompatible governance or principle removals/renames.
	 - MINOR: addition of principles or materially expanded guidance.
	 - PATCH: clarifications, typo fixes, or non‑semantic refinements.
4. Compliance: All implementation plans and feature PRs MUST include a short "Constitution
	 Compliance" checklist linking to this file and indicating how the change aligns with
	 the principles above.

**Version**: 0.1.0 | **Ratified**: TODO(RATIFICATION_DATE): set when constitution adopted | **Last Amended**: 2026-05-07

