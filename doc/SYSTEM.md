# ForgeMath — Complete System Reference

> Canonical authority substrate for governed lane math in the Forge ecosystem.
> "Canonical truth before canonical execution."

**Document version:** 1.0 (2026-04-02) — Initial Phase 1 foundation

---

## Table of Contents

1. [Overview & Philosophy](#1-overview--philosophy)
2. [Architecture](#2-architecture)
3. [Tech Stack](#3-tech-stack)
4. [Project Structure](#4-project-structure)
5. [Configuration & Environment](#5-configuration--environment)
6. [Design System](#6-design-system)
7. [Frontend](#7-frontend)
8. [API Layer](#8-api-layer)
9. [Backend](#9-backend)
10. [Ecosystem Integration](#10-ecosystem-integration)
11. [Database Schema](#11-database-schema)
12. [AI Integration](#12-ai-integration)
13. [Error Handling Contract](#13-error-handling-contract)
14. [Testing Infrastructure](#14-testing-infrastructure)
15. [Handover / Migration Notes](#15-handover--migration-notes)


---

## 1. Overview & Philosophy

ForgeMath is a backend-only canonical authority service for governed lane math.
The current repository state implements Phase 1 only: vocabulary freezing,
versioned registry truth, deterministic runtime profile admission, scope
declaration, and migration metadata.

### 1.1 Core Principles

- Canonical truth is append-only and versioned.
- Registry payloads do not mutate in place.
- Read models are not canonical truth.
- Missing required bindings fail closed.
- Runtime determinism is enforced, not assumed.
- Formula execution is deferred until the substrate is stable.

### 1.2 Current Product Boundary

| Area | Current status |
|------|----------------|
| Governance registries | Implemented |
| Runtime profile persistence | Implemented |
| Scope registry | Implemented |
| Migration package metadata | Implemented |
| Lane execution | Not implemented |
| Evaluation persistence | Not implemented |
| Replay orchestration | Not implemented |


---

## 2. Architecture

The implemented Phase 1 architecture is a single FastAPI service backed by
SQLAlchemy models and Alembic migrations.

### 2.1 High-Level Flow

```text
Client
  -> FastAPI route
  -> registry service
  -> validation + version sequencing
  -> SQLAlchemy session
  -> canonical Phase 1 tables
```

### 2.2 Module Boundaries

| Layer | Files | Responsibility |
|------|-------|----------------|
| API | `app/api/registry_router.py` | Route contract and HTTP error translation |
| Schemas | `app/schemas/governance.py` | Request DTOs, read DTOs, compatibility tuple freeze |
| Services | `app/services/registry_service.py` | Fail-closed creation logic and supersession sequencing |
| Persistence | `app/models/governance.py` | Canonical Phase 1 ORM models |
| Migrations | `alembic/versions/20260402_0001_phase1_foundation.py` | Database schema authority |


---

## 3. Tech Stack

### 3.1 Runtime Dependencies

| Layer | Dependency | Version |
|------|------------|---------|
| API | FastAPI | `0.109.0` |
| ASGI server | Uvicorn | `0.27.0` |
| ORM | SQLAlchemy | `2.0.36` |
| Migrations | Alembic | `1.13.1` |
| Validation | Pydantic | `>=2.10.0` |
| Database driver | psycopg2-binary | `2.9.10` |
| Environment loading | python-dotenv | `1.0.0` |

### 3.2 Test Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | `7.4.3` | Repo test runner |
| httpx | `0.26.0` | FastAPI-compatible request tooling and dependency surface |


---

## 4. Project Structure

### 4.1 Directory Map

```text
ForgeMath/
├── alembic/
│   └── versions/
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   └── services/
├── doc/
│   └── system/
├── docs/
├── scripts/
└── tests/
```

### 4.2 File Conventions

| Pattern | Meaning |
|--------|---------|
| `app/models/*.py` | Canonical table ownership |
| `app/schemas/*.py` | Request/read contract types |
| `app/services/*.py` | Business rules and invariants |
| `doc/system/*.md` | Modular SYSTEM source files |
| `docs/*.md` | Architecture, roadmap, and module specs |


---

## 5. Configuration & Environment

### 5.1 Environment Variables

| Variable | Type | Default | Read by |
|---------|------|---------|---------|
| `FORGEMATH_DATABASE_URL` | string | `sqlite:///./forgemath.db` | `app/config.py`, `app/database.py`, `alembic/env.py` |
| `FORGEMATH_HOST` | string | `127.0.0.1` | `app/config.py` |
| `FORGEMATH_PORT` | integer | `8011` | `app/config.py` |

### 5.2 Validation Rules

- database URL must not be empty
- host must not be empty
- port must be between `1` and `65535`


---

## 6. Design System

ForgeMath currently has no end-user UI inside this repo.
Phase 1 is a backend-only canonical service, so the design system surface is
limited to JSON contracts, naming consistency, and documentation clarity.

### 6.1 Current UI Posture

| Surface | Status |
|--------|--------|
| In-repo frontend | Not implemented |
| Operator API responses | Implemented as JSON read DTOs |
| External UI consumers | Deferred to downstream services |


---

## 7. Frontend

No frontend implementation exists in Phase 1.
Operator interaction is through documentation, migrations, and HTTP routes.

### 7.1 Deferred Frontend Work

- no SPA or Tauri client
- no projection dashboard
- no route-local visualization of lane outputs


---

## 8. API Layer

All implemented routes live under `/api/v1/forgemath/governance`.

### 8.1 Health Route

| Method | Path | Purpose |
|-------|------|---------|
| `GET` | `/health` | Service health and phase marker |

### 8.2 Governance Routes

| Family | Create | List | Get version |
|-------|--------|------|-------------|
| Lane specs | `POST /lane-specs` | `GET /lane-specs` | `GET /lane-specs/{lane_id}/versions/{version}` |
| Variable registries | `POST /variable-registries` | `GET /variable-registries` | `GET /variable-registries/{variable_registry_id}/versions/{version}` |
| Parameter sets | `POST /parameter-sets` | `GET /parameter-sets` | `GET /parameter-sets/{parameter_set_id}/versions/{version}` |
| Threshold sets | `POST /threshold-sets` | `GET /threshold-sets` | `GET /threshold-sets/{threshold_set_id}/versions/{version}` |
| Policy bundles | `POST /policy-bundles` | `GET /policy-bundles` | `GET /policy-bundles/{policy_bundle_id}/versions/{version}` |
| Runtime profiles | `POST /runtime-profiles` | `GET /runtime-profiles` | `GET /runtime-profiles/{runtime_profile_id}/versions/{version}` |
| Scopes | `POST /scopes` | `GET /scopes` | `GET /scopes/{scope_id}/versions/{version}` |
| Migration packages | `POST /migration-packages` | `GET /migration-packages` | `GET /migration-packages/{migration_id}/versions/{version}` |


---

## 9. Backend

### 9.1 Service Responsibilities

| File | Responsibility |
|------|----------------|
| `app/services/registry_service.py` | create/list/get logic, version sequencing, supersession closure |
| `app/services/immutability.py` | session-level protection against payload mutation |
| `app/models/governance.py` | versioned canonical tables |
| `app/database.py` | engine and session factory |

### 9.2 Backend Invariants

- first version must be `1`
- later versions must be sequential
- superseding an active version requires `retired_reason`
- only lifecycle closure fields may change after persistence
- canonical runtime profiles reject non-deterministic admission


---

## 10. Ecosystem Integration

Phase 1 intentionally avoids direct runtime coupling to other Forge services.

### 10.1 Current Integration State

| Service | Current relationship | Notes |
|--------|----------------------|-------|
| DataForge | None at runtime | Future consumer/integration target only |
| Forge Command | None at runtime | Policy or operator tooling deferred |
| NeuroForge | None | No AI execution path in repo runtime |

### 10.2 Governance Inputs

The repo is grounded by external governing docs, but those documents are not
runtime dependencies. They are operator and design inputs.


---

## 11. Database Schema

Phase 1 ships one initial migration: `20260402_0001_phase1_foundation`.

### 11.1 Canonical Tables

| Table | Purpose | Key columns | Invariants |
|------|---------|-------------|------------|
| `forgemath_lane_specs` | Lane contract versions | `lane_id`, `version`, `lane_family`, `trace_tier`, `payload_hash` | unique per `lane_id + version`, payload immutable |
| `forgemath_variable_registry` | Variable vocabulary snapshots | `variable_registry_id`, `version`, `payload_hash` | unique per registry/version |
| `forgemath_parameter_sets` | Immutable parameter bindings | `parameter_set_id`, `version`, `lane_id`, `payload_hash` | sequential supersession only |
| `forgemath_threshold_sets` | Immutable threshold bindings | `threshold_set_id`, `version`, `lane_id`, `payload_hash` | sequential supersession only |
| `forgemath_policy_bundles` | Policy bundle versions | `policy_bundle_id`, `version`, `policy_kind`, `payload_hash` | controlled policy-kind vocabulary |
| `forgemath_runtime_profiles` | Deterministic runtime bindings | `runtime_profile_id`, `version`, rounding and serialization fields | canonical writes reject non-deterministic profiles |
| `forgemath_scope_registry` | Scope declarations | `scope_id`, `version`, `scope_class`, `display_name` | local/cloud/hybrid vocabulary |
| `forgemath_migration_packages` | Migration metadata | `migration_id`, `version`, source/target versions, approval state | controlled migration and approval vocabulary |

### 11.2 Common Columns

Every governed table includes:

- `id`
- `version`
- `payload_hash`
- `effective_from`
- `superseded_at`
- `superseded_by_id`
- `retired_reason`
- `created_at`
- `created_by`


---

## 12. AI Integration

ForgeMath has no runtime AI integration in Phase 1.
AI involvement is limited to the governed development workflow described by BDS
documentation and AI-assisted development protocols.

### 12.1 Current AI Posture

| Area | Status |
|------|--------|
| Runtime inference | Not implemented |
| Provider routing | Not implemented |
| AI-assisted development | Active, bounded by repo docs and BDS doctrine |


---

## 13. Error Handling Contract

### 13.1 HTTP Status Mapping

| Status | Trigger |
|-------|---------|
| `201` | Successful create |
| `400` | Validation failure in governed service logic |
| `404` | Requested governed version not found |
| `409` | Duplicate or conflicting governed version |
| `422` | FastAPI request-body validation failure |

### 13.2 Error Translation

Route handlers translate governed service exceptions into explicit HTTP failures.
No route silently degrades a missing or incompatible binding into a success path.


---

## 14. Testing Infrastructure

### 14.1 Current Test Coverage

| Test file | Coverage |
|----------|----------|
| `tests/test_phase1_api.py` | Route-function contract coverage and HTTP error translation |
| `tests/test_phase1_invariants.py` | Immutability, supersession lineage, compatibility tuple hash stability |

### 14.2 Execution

```bash
python -m pytest tests -q
```

### 14.3 Test Boundary

The current suite validates Phase 1 write logic and invariants.
It does not yet cover migration application on a live Postgres instance or any evaluation/replay logic because those phases are not implemented.


---

## 15. Handover / Migration Notes

### 15.1 Governing Inputs

The repo is grounded by these documents:

- `bds_ai_assisted_development_operations_protocol.md`
- `BDS_DOCUMENTATION_PROTOCOL_v1.md`
- `vscode_forgemath_initial_implementation_prompt_and_plan.md`
- `forge_math_canonical_equation_stack_top_level_overview.md`
- `forge_math_canonical_equation_specification_v_1_initial.md`
- `forge_math_lane_governance_persistence_replay_and_runtime_contract_v_1_initial.md`

### 15.2 Deferred Work

- evaluation tables
- compatibility resolution engine
- replay and stale state machines
- execution engine
- downstream projection surfaces

