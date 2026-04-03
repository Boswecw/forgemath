# ForgeMath — Claude Instructions

## Module Map

| Module | Route / Surface | Primary Files | Authority |
|--------|------------------|---------------|-----------|
| Governance API | `/api/v1/forgemath/governance/*` | `app/api/registry_router.py` | Phase 1 create/list/get for governed registries |
| Registry Services | Internal service layer | `app/services/registry_service.py` | Fail-closed validation, version sequencing, supersession |
| Immutability Guard | SQLAlchemy session hook | `app/services/immutability.py` | Prevents in-place mutation of persisted payloads |
| Governance Models | Canonical persistence layer | `app/models/governance.py` | Versioned canonical truth for Phase 1 tables |
| Schemas | Request/read contract layer | `app/schemas/governance.py` | Separate write models from read models |
| Migrations | Database build surface | `alembic/`, `alembic/versions/20260402_0001_phase1_foundation.py` | Schema authority for Phase 1 |
| Documentation Stack | Canonical repo context | `doc/system/`, `SYSTEM.md`, `docs/` | Repo reality and operator handoff |

## Coding Standards

- Use Python 3.11+ and SQLAlchemy 2-style typed models.
- Preserve append-only lineage for canonical records.
- Never mutate persisted payload fields in place. Only lifecycle closure fields may change.
- Fail closed when required bindings, versions, or deterministic posture are missing.
- Do not implement formula execution or invent formula semantics in this repo phase.
- Keep request/write schemas separate from read models and never let read models become source truth.

## File Conventions

- Runtime code lives under `app/`.
- Alembic migrations live under `alembic/versions/`.
- Tests live under `tests/`.
- Canonical system documentation is authored in `doc/system/` and assembled into root `SYSTEM.md`.
- New domain docs belong in `docs/`.

## Context Loading

```bash
# Core governance foundation
./scripts/context-bundle.sh --preset foundation

# API and failure-contract work
./scripts/context-bundle.sh --preset api --with-specs

# Schema and persistence work
./scripts/context-bundle.sh --preset schema --with-roadmap
```

## Ecosystem Rules

- ForgeMath is a canonical authority subsystem, not a helper library.
- Phase 1 stays local to repo-owned truth. No direct runtime integration with DataForge or other Forge services is implemented yet.
- Projection/read models remain downstream consumers, never canonical writers.
- Compatibility, replay, and engine execution semantics remain deferred unless explicitly added in later phases.

## Testing Expectations

- Run `python -m pytest tests -q` from the repo root.
- Cover route-level contract translation, immutability enforcement, deterministic runtime admission, and version lineage.
- Add migration or schema doc updates whenever canonical tables or route contracts change.

## Change Protocol

- Edit `doc/system/` parts, never root `SYSTEM.md`, then run `doc/system/BUILD.sh`.
- Keep new files inside known repo boundaries and explain why they exist.
- Prefer patches over broad rewrites.
- If code changes architectural truth, update `docs/` and `doc/system/` in the same turn.

