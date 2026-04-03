# ForgeMath — Complete System Reference

> Canonical authority substrate for governed lane math in the Forge ecosystem.
> "Canonical truth before canonical execution."

**Document version:** 1.6 (2026-04-02) — Phase 6 authority and numeric hardening

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
The current repository state implements Phase 1 through Phase 6:
versioned governance registries, canonical evaluation persistence,
explicit lifecycle governance for replay, stale posture,
recomputation posture, supersession lineage,
deterministic runtime admission control,
governed projection/read-model inspection surfaces,
and a bounded canonical execution substrate for the initial numeric lane wave.
The current repo state also hardens the authority boundary so manual ingest
cannot mint computed canonical truth, derives canonical output hashes from the
persisted artifact bundle, and stores canonical numeric artifacts as decimal
strings instead of floats.

### 1.1 Core Principles

- Canonical truth is append-only and versioned.
- Registry and persisted evaluation payloads do not mutate in place.
- Read models are not canonical truth.
- Missing required bindings fail closed.
- Runtime determinism is enforced, not assumed.
- Lifecycle posture is explicit, not inferred by downstream consumers.
- Deterministic runtime admission truth is explicit and persisted.
- Projection DTOs are read models only and do not become canonical truth.
- Canonical execution remains bounded to governed supported lanes and fails closed otherwise.
- Manual ingest remains available only for non-computed historical visibility.
- Canonical numeric artifacts persist in deterministic decimal-string form.
- Active canonical execution truth must be explicitly superseded before replacement.

### 1.2 Current Product Boundary

| Area | Current status |
|------|----------------|
| Governance registries | Implemented |
| Canonical evaluation persistence | Implemented |
| Lifecycle governance | Implemented |
| Runtime profile persistence | Implemented |
| Runtime admission enforcement | Implemented |
| Projection DTO/read-model surfaces | Implemented |
| Bounded lane execution substrate | Implemented |
| Scope registry | Implemented |
| Migration package metadata | Implemented |
| Broad multi-lane orchestration | Not implemented |
| Replay orchestration workers | Not implemented |
| Stale-state automation engine | Not implemented |

---

## 2. Architecture

The implemented architecture is a single FastAPI service backed by
SQLAlchemy models and Alembic migrations, with Phase 1 governance,
Phase 2 evaluation persistence, Phase 3 lifecycle control,
Phase 4 runtime admission control,
Phase 5 read-model composition,
Phase 6 bounded lane execution,
and a post-Phase-6 hardening slice that tightens authority boundaries,
canonical numeric persistence, and active execution lineage in one canonical
service boundary.

### 2.1 High-Level Flow

```text
Client
  -> FastAPI route
  -> route-specific governed service
  -> fail-closed validation, lifecycle derivation, runtime admission derivation,
     projection composition, or bounded execution derivation
  -> SQLAlchemy session
  -> canonical governance/evaluation/lifecycle tables
```

### 2.2 Module Boundaries

| Layer | Files | Responsibility |
|------|-------|----------------|
| API | `app/api/registry_router.py`, `app/api/evaluation_router.py` | Governance, manual non-computed ingest, lifecycle, runtime-admission, projection read, and execution routes |
| Schemas | `app/schemas/governance.py`, `app/schemas/evaluation.py`, `app/schemas/execution.py`, `app/schemas/execution_contracts.py`, `app/schemas/projection.py` | Write DTOs, canonical reads, supported-lane payload contracts, execution contracts, and projection DTOs |
| Services | `app/services/registry_service.py`, `app/services/evaluation_service.py`, `app/services/lifecycle_service.py`, `app/services/runtime_admission_service.py`, `app/services/execution_service.py`, `app/services/projection_service.py` | Fail-closed governed writes, authority-boundary enforcement, canonical artifact hashing, lifecycle validation, runtime admission, bounded lane execution, and projection composition |
| Persistence | `app/models/governance.py`, `app/models/evaluation.py` | Canonical registry, evaluation, lifecycle, and runtime-admission ORM models |
| Migrations | `alembic/versions/20260402_0001_phase1_foundation.py` through `20260402_0005_authority_boundary_and_numeric_hardening.py` | Database schema authority |

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
Phase 1 through Phase 6 remain backend-only, so the design system surface is
limited to JSON contracts, naming consistency, and documentation clarity.

### 6.1 Current UI Posture

| Surface | Status |
|--------|--------|
| In-repo frontend | Not implemented |
| Operator API responses | Implemented as JSON read DTOs |
| External UI consumers | Deferred to downstream services |

---

## 7. Frontend

No frontend implementation exists in the current Phase 1-6 repo state.
Operator interaction is through documentation, migrations, and HTTP routes.

### 7.1 Deferred Frontend Work

- no SPA or Tauri client
- no projection dashboard
- no route-local visualization of lane outputs

---

## 8. API Layer

Implemented routes live under `/api/v1/forgemath/governance` and `/api/v1/forgemath`.

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

### 8.3 Evaluation Routes

| Family | Create | List | Get |
|-------|--------|------|-----|
| Input bundles | `POST /input-bundles` | `GET /input-bundles` | `GET /input-bundles/{input_bundle_id}` |
| Lane evaluations | `POST /lane-evaluations` | `GET /lane-evaluations` | `GET /lane-evaluations/{lane_evaluation_id}` |
| Replay queue events | `POST /replay-queue-events` | `GET /replay-queue-events` | `GET /replay-queue-events/{replay_event_id}` |
| Incident records | `POST /incidents` | `GET /incidents` | `GET /incidents/{incident_id}` |

`POST /lane-evaluations` is now restricted to governed manual ingest for
non-computed historical records. Canonical computed truth is expected to enter
through `POST /lane-executions`.

### 8.4 Execution Routes

| Family | Action | Path |
|-------|--------|------|
| Bounded canonical execution | `POST` | `/lane-executions` |

### 8.5 Lifecycle Routes

| Family | Action | Path |
|-------|--------|------|
| Lifecycle inspection | `GET` | `/lane-evaluations/{lane_evaluation_id}/lifecycle` |
| Lifecycle transition | `POST` | `/lane-evaluations/{lane_evaluation_id}/lifecycle-transitions` |
| Lineage inspection | `GET` | `/lane-evaluations/{lane_evaluation_id}/lineage` |

### 8.6 Runtime Admission Routes

| Family | Action | Path |
|-------|--------|------|
| Runtime admission inspection | `GET` | `/lane-evaluations/{lane_evaluation_id}/runtime-admission` |

### 8.7 Projection Routes

| Family | Action | Path |
|-------|--------|------|
| Evaluation summary projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/summary` |
| Evaluation detail projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/detail` |
| Factor inspection projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/factors` |
| Trace inspection projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/trace` |
| Replay diagnostic projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/replay-diagnostics` |

---

## 9. Backend

### 9.1 Service Responsibilities

| File | Responsibility |
|------|----------------|
| `app/services/registry_service.py` | create/list/get logic, version sequencing, supersession closure |
| `app/services/evaluation_service.py` | canonical evaluation persistence, manual-ingest boundary enforcement, canonical artifact hashing, trace, replay queue, and incident persistence |
| `app/services/lifecycle_service.py` | replay/stale/recomputation validation, supersession lifecycle control, lineage reads |
| `app/services/runtime_admission_service.py` | deterministic runtime validation, runtime certificate derivation, runtime admission inspection |
| `app/services/execution_service.py` | bounded canonical execution for supported Phase 6 lanes, supported-lane contract validation, and active execution lineage control |
| `app/services/projection_service.py` | governed projection/read-model composition over canonical truth |
| `app/services/immutability.py` | session-level protection against payload mutation |
| `app/models/governance.py` | versioned governance tables |
| `app/models/evaluation.py` | canonical evaluation, lifecycle, and runtime-admission tables |
| `app/database.py` | engine and session factory |

### 9.2 Backend Invariants

- first version must be `1`
- later versions must be sequential
- superseding an active version requires `retired_reason`
- canonical evaluations require frozen input, runtime profile, and full compatibility binding
- canonical evaluations persist explicit deterministic runtime admission truth
- canonical admission fails closed when runtime profile fields are incomplete
- canonical admission fails closed when runtime profile is retired or non-deterministic
- manual ingest may not persist computed canonical truth, caller-supplied output bundles, or caller-supplied output hashes
- canonical execution mode is server-owned on the execution route and may not be caller-supplied
- raw_output_hash is derived from the persisted canonical output/factor/trace artifact bundle
- trace bundle hashing excludes storage ids so identical reruns preserve stable canonical artifact hashes
- parameter, threshold, and policy bindings must match the evaluation lane when those records declare a lane binding
- optional prior and decay compatibility bindings must resolve when present
- canonical numeric output/factor values persist as deterministic decimal strings rather than floats
- output field names and factor names are unique per evaluation
- output and factor DTOs fail closed when computed rows are semantically incomplete
- bounded execution supports only governed Phase 6 lanes and canonical_numeric lane family
- bounded execution fails closed when variable, parameter, threshold, policy, runtime, or input bindings are missing or inactive
- bounded execution fails closed when supported parameter payloads or threshold topologies violate the bounded execution contract
- bounded execution persists through the existing evaluation service and does not bypass canonical truth tables
- bounded execution emits inspectable factor rows and tier_1_full trace events for supported lanes
- bounded execution fails closed when an active canonical execution already exists for the same execution context unless explicit supersession is declared
- repeat execution over the same governed context preserves stable output, factor, trace, and raw-output hashing when lineage supersession is explicit
- projection routes are read-only and derive metadata from canonical compatibility bindings
- projection composition fails closed when source evaluation or source trace truth is missing
- replay posture fails closed when required bindings are missing
- stale posture may not be downgraded or silently reset to fresh
- supersession preserves visibility and records append-only lifecycle events
- only governed lifecycle fields may change after persisted evaluation creation
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

The repo currently ships five schema migrations:

- `20260402_0001_phase1_foundation`
- `20260402_0002_phase2_evaluation_foundation`
- `20260402_0003_phase3_lifecycle_governance`
- `20260402_0004_phase4_runtime_admission`
- `20260402_0005_authority_boundary_and_numeric_hardening`

Phase 5 adds no new persistence tables.
Projection DTOs are composed from existing canonical evaluation, lifecycle,
runtime-admission, factor, and trace tables.
Phase 6 also adds no new persistence tables.
Bounded execution writes continue to land in the existing canonical evaluation,
output, factor, and trace tables.

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
| `forgemath_input_bundles` | Frozen admissible input bundles | `input_bundle_id`, `deterministic_input_hash`, `scope_id` | canonical evaluations require frozen bundle linkage |
| `forgemath_lane_evaluations` | Root canonical evaluation truth | `lane_evaluation_id`, `lane_id`, `compatibility_tuple_hash`, lifecycle columns | append-only evaluation truth with governed lifecycle fields |
| `forgemath_lane_output_values` | Output payload layers | `lane_evaluation_id`, `output_field_name`, `output_posture`, `numeric_value` | unique per evaluation/output field, numeric artifacts stored as decimal text |
| `forgemath_lane_factor_values` | Factor contribution layers | `lane_evaluation_id`, `factor_name` | unique per evaluation/factor name, numeric artifacts stored as decimal text |
| `forgemath_trace_bundles` | Trace bundle metadata | `trace_bundle_id`, `lane_evaluation_id`, `trace_tier` | canonical trace posture linked to each evaluation |
| `forgemath_trace_events` | Trace step rows | `trace_bundle_id`, `trace_step_order` | append-only trace sequence per bundle |
| `forgemath_replay_queue_events` | Replay control surface | `replay_event_id`, linkage refs, priority/budget classes | operational control queue metadata only |
| `forgemath_incident_records` | Governance incidents | `incident_id`, `incident_class`, `related_lane_evaluation_id` | canonical incident registry for lifecycle/control failures |
| `forgemath_evaluation_lifecycle_events` | Lifecycle transition audit trail | `event_id`, `lane_evaluation_id`, prior/new lifecycle values | append-only lifecycle history per evaluation |
| `forgemath_runtime_admission_events` | Deterministic runtime admission audit trail | `event_id`, `lane_evaluation_id`, `runtime_profile_id`, `admission_outcome` | append-only runtime admission history per evaluation |

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

Evaluation lifecycle rows additionally expose:

- `replay_state`
- `stale_state`
- `recomputation_action`
- `superseded_by_evaluation_id`
- `supersession_reason`
- `supersession_timestamp`
- `supersession_class`
- `lifecycle_reason_code`
- `lifecycle_reason_detail`

Evaluation runtime admission truth additionally exposes:

- `deterministic_admission_state`
- `runtime_validation_reason_code`
- `runtime_validation_reason_detail`
- `determinism_certificate_ref`
- `bit_exact_eligible`

Phase `20260402_0005` further hardens the evaluation payload tables by:

- converting output and factor numeric columns from `FLOAT` to deterministic text storage
- enforcing unique `output_field_name` values per evaluation
- enforcing unique `factor_name` values per evaluation

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

### 13.3 Lifecycle Failure Posture

- invalid replay-safe claims fail with `400`
- invalid stale-state downgrades fail with `400`
- lineage conflicts or duplicate supersession links fail with `409`
- missing lifecycle inspection targets fail with `404`

### 13.4 Runtime Admission Failure Posture

- non-deterministic runtime profiles fail canonical admission with `400`
- incomplete runtime profiles fail canonical admission with `400`
- retired runtime profiles fail canonical admission with `400`
- missing evaluation targets for runtime inspection fail with `404`

### 13.5 Projection Failure Posture

- missing source evaluations fail projection reads with `404`
- missing source trace bundles fail trace projection reads with `404`
- missing projection schema bindings fail projection composition with `400`

### 13.6 Execution Failure Posture

- unsupported Phase 6 lanes fail execution with `400`
- missing required input variables fail execution with `400`
- missing governance bindings fail execution with `404`
- runtime profiles outside the supported deterministic Phase 6 substrate fail execution with `400`
- invalid supported-lane parameter semantics or threshold topology fail execution with `400`
- duplicate active canonical execution context without explicit supersession fails with `400`

### 13.7 Authority-Boundary Failure Posture

- manual ingest attempts to persist computed canonical truth fail request validation with `422`
- caller-supplied `execution_mode` on the execution route fails request validation with `422`
- caller-supplied raw_output_hash values that do not match the persisted artifact bundle fail with `400`
- incomplete optional prior/decay compatibility bindings fail request validation with `422`
- cross-lane parameter, threshold, or policy bindings fail with `400`

---

## 14. Testing Infrastructure

### 14.1 Current Test Coverage

| Test file | Coverage |
|----------|----------|
| `tests/test_phase1_api.py` | Route-function contract coverage and HTTP error translation |
| `tests/test_phase1_invariants.py` | Immutability, supersession lineage, compatibility tuple hash stability |
| `tests/test_phase2_api.py` | Canonical evaluation write/read coverage, optional compatibility-binding validation, and fail-closed artifact-shape checks |
| `tests/test_phase2_invariants.py` | Frozen input bundle immutability checks |
| `tests/test_phase3_lifecycle.py` | Lifecycle inspection, stale/replay transitions, and lineage visibility |
| `tests/test_phase4_runtime_admission.py` | Deterministic runtime admission persistence, inspection, and fail-closed invalid profile checks |
| `tests/test_phase5_projections.py` | Projection metadata, truth-preserving summary/detail/factor/trace/replay reads, and fail-closed missing-source checks |
| `tests/test_phase6_execution.py` | Supported lane execution happy paths, repeatability/hash-stability checks, and fail-closed missing-binding, missing-input, unsupported-lane, invalid-parameter, invalid-threshold, and runtime-profile execution checks |
| `tests/test_http_contracts.py` | Real HTTP route checks for manual-ingest boundary, execution route behavior, and caller-supplied execution-mode rejection when the environment allows localhost binding |
| `tests/test_postgres_invariants.py` | Postgres-backed migration/schema invariant checks when `FORGEMATH_POSTGRES_TEST_URL` is supplied |

### 14.2 Execution

```bash
python -m pytest tests -q
FORGEMATH_DATABASE_URL=sqlite:///./hardening_verify.db alembic upgrade head
```

### 14.3 Test Boundary

The current suite validates Phase 1 through Phase 6 write logic and invariants.
It also validates the hardening slice for:

- manual-ingest boundary restriction
- derived raw-output hashing
- lane-affinity binding checks
- optional prior/decay compatibility binding enforcement
- computed output/factor payload shape enforcement
- deterministic decimal-string artifact persistence
- active canonical execution conflict handling
- repeatability and hash stability across explicit superseding reruns

HTTP route checks and Postgres-backed invariant checks are present but may skip in
restricted environments that block localhost binding or do not provide a Postgres URL.

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

- compatibility resolution engine beyond bounded validation and persisted binding checks
- runtime admission evolution beyond bounded deterministic validation and persisted evidence
- replay workers and queue processors
- stale-state automation engine
- execution expansion beyond the bounded Phase 6 lane wave
- hybrid gate execution and broader multi-lane orchestration
- persisted projection records or downstream projection distribution surfaces
- stronger database-level current-truth constraints if future execution expansion needs protection beyond the current service-level guardrails
