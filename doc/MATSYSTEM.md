        # ForgeMath - Compiled System Reference

        **Designation:** MAT
        **Document role:** Canonical compiled technical reference for ForgeMath
        **Source:** `doc/system/`
        **Build command:** `bash doc/system/BUILD.sh`
        **Document version:** 2.0 (2026-06-22) - canonical compliance migration
        **Protocol:** BDS Documentation Protocol v2.0; BDS Repo Documentation System Canonical Compliance Standard

        > **Generated artifact warning:** `doc/MATSYSTEM.md` is assembled output. Edit
        > the source modules under `doc/system/` and rebuild. Hand edits to the
        > compiled artifact are overwritten by the next build.

        Assembly contract:

        - Command: `bash doc/system/BUILD.sh`
        - Validation: `bash doc/system/validate_snapshots.sh` runs during assembly
        - Primary output: `doc/MATSYSTEM.md`

        This `doc/system/` tree is the canonical source of truth for ForgeMath. It uses
        explicit **truth classes**: canonical facts define repo role, authority
        boundaries, contract behavior, runtime behavior, and verification doctrine;
        snapshot facts are dated, audit-derived counts and current implementation
        inventory that may drift between audits.

        | Part | File | Contents |
        | --- | --- | --- |
        | §1 | `00_overview/00-overview.md` | Overview |
| §2 | `00_overview/01-architecture.md` | Architecture |
| §3 | `00_overview/01-overview-philosophy.md` | 1. Overview & Philosophy |
| §4 | `00_overview/02-architecture.md` | 2. Architecture |
| §5 | `00_overview/04-project-structure.md` | 4. Project Structure |
| §6 | `10_service-contract/08-api-layer.md` | 8. API Layer |
| §7 | `10_service-contract/10-ecosystem-integration.md` | 10. Ecosystem Integration |
| §8 | `20_runtime/07-frontend.md` | 7. Frontend |
| §9 | `20_runtime/09-backend.md` | 9. Backend |
| §10 | `20_runtime/11-database-schema.md` | 11. Database Schema |
| §11 | `20_runtime/12-ai-integration.md` | 12. AI Integration |
| §12 | `20_runtime/13-error-handling.md` | 13. Error Handling Contract |
| §13 | `30_dependencies/03-tech-stack.md` | 3. Tech Stack |
| §14 | `30_dependencies/06-design-system.md` | 6. Design System |
| §15 | `40_governance/10-scope.md` | Scope |
| §16 | `40_governance/30-governance.md` | Governance |
| §17 | `40_governance/40-change-control.md` | Change Control |
| §18 | `50_operations/05-configuration.md` | 5. Configuration & Environment |
| §19 | `50_operations/14-testing-infrastructure.md` | 14. Testing Infrastructure |
| §20 | `50_operations/15-handover-migration-notes.md` | 15. Handover / Migration Notes |
| §21 | `99_appendices/20-structure.md` | Structure |
| §22 | `99_appendices/90-appendices.md` | Appendices |

        ## Quick Assembly

        ```bash
        bash doc/system/BUILD.sh
        ```

---

# Overview

**Document version:** 1.0 (bootstrap scaffold)

System identity, role, and boundary with the rest of the Forge ecosystem.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

# Architecture

**Document version:** 1.0 (bootstrap scaffold)

High-level architecture, authority posture, and surface ownership.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

## 1. Overview & Philosophy

ForgeMath is a backend-only canonical authority service for governed lane math.
The current repository state implements Phase 1 through Phase 7:
versioned governance registries, canonical evaluation persistence,
explicit lifecycle governance for replay, stale posture,
recomputation posture, supersession lineage,
deterministic runtime admission control,
governed projection/read-model inspection surfaces,
and a bounded canonical execution substrate for the initial numeric lane wave.
The current repo state also hardens the authority boundary so manual ingest
cannot mint computed canonical truth, derives canonical output hashes from the
persisted artifact bundle, and stores canonical numeric artifacts as decimal
strings instead of floats. Phase 7 adds persistence-level active canonical
execution exclusivity, determinism-sensitive migration metadata,
runtime-recovery inspection posture, and stricter supersession safety checks.

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
- Persistence-level active canonical execution exclusivity backs the service-level guardrail.
- Determinism-sensitive migrations must declare the deterministic artifacts they affect.
- Runtime-admission reads expose recovery posture when canonical runtime bindings degrade.

### 1.2 Current Product Boundary

| Area | Current status |
|------|----------------|
| Governance registries | Implemented |
| Canonical evaluation persistence | Implemented |
| Lifecycle governance | Implemented |
| Runtime profile persistence | Implemented |
| Runtime admission enforcement | Implemented |
| Runtime recovery posture inspection | Implemented |
| Projection DTO/read-model surfaces | Implemented |
| Bounded lane execution substrate | Implemented |
| Durability and lifecycle-control hardening | Implemented |
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
and two hardening slices that tighten authority boundaries,
canonical numeric persistence, active execution lineage, persistence-level
current-truth exclusivity, determinism-sensitive migration metadata, and
runtime-recovery inspection inside one canonical service boundary.

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
| Services | `app/services/registry_service.py`, `app/services/evaluation_service.py`, `app/services/lifecycle_service.py`, `app/services/runtime_admission_service.py`, `app/services/execution_service.py`, `app/services/projection_service.py` | Fail-closed governed writes, authority-boundary enforcement, canonical artifact hashing, lifecycle validation, runtime admission and recovery, bounded lane execution, and projection composition |
| Persistence | `app/models/governance.py`, `app/models/evaluation.py` | Canonical registry, evaluation, lifecycle, runtime-admission, and durability ORM models |
| Migrations | `alembic/versions/20260402_0001_phase1_foundation.py` through `20260403_0006_phase7_durability_and_control_hardening.py` | Database schema authority |

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

Runtime-admission inspection returns both persisted admission truth and derived
runtime-recovery posture when the bound runtime profile is missing, incomplete,
non-deterministic, or retired.

### 8.7 Projection Routes

| Family | Action | Path |
|-------|--------|------|
| Evaluation summary projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/summary` |
| Evaluation detail projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/detail` |
| Factor inspection projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/factors` |
| Trace inspection projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/trace` |
| Replay diagnostic projection | `GET` | `/lane-evaluations/{lane_evaluation_id}/replay-diagnostics` |

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

## 7. Frontend

No frontend implementation exists in the current Phase 1-7 repo state.
Operator interaction is through documentation, migrations, and HTTP routes.

### 7.1 Deferred Frontend Work

- no SPA or Tauri client
- no projection dashboard
- no route-local visualization of lane outputs

---

## 9. Backend

### 9.1 Service Responsibilities

| File | Responsibility |
|------|----------------|
| `app/services/registry_service.py` | create/list/get logic, version sequencing, supersession closure, and determinism-sensitive migration package persistence |
| `app/services/evaluation_service.py` | canonical evaluation persistence, manual-ingest boundary enforcement, canonical artifact hashing, persistence-level active execution exclusivity, trace, replay queue, and incident persistence |
| `app/services/lifecycle_service.py` | replay/stale/recomputation validation, supersession lifecycle control, lineage reads, and cycle/temporal-order hardening |
| `app/services/runtime_admission_service.py` | deterministic runtime validation, runtime certificate derivation, runtime admission inspection, and runtime-recovery posture derivation |
| `app/services/execution_service.py` | bounded canonical execution for supported Phase 6 lanes, supported-lane contract validation, and active execution lineage control |
| `app/services/projection_service.py` | governed projection/read-model composition over canonical truth |
| `app/services/immutability.py` | session-level protection against payload mutation |
| `app/lineage/emitter.py` | ForgeLineage producer: emits `forgemath_evaluation` + `forgemath_output` (+ optional `consumed` edge from the upstream eval-cal node) to DataForge-Local |
| `app/lineage/spine_emit.py` | opt-in, non-blocking lineage emission for the Evaluation Spine run; discovers the upstream `eval_cal_record` and drives the emitter |
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
- persistence-level unique active canonical execution keys reject duplicate live current-truth inserts for the same governed execution context
- governed canonical supersession may only target prior governed canonical execution lineage records
- repeat execution over the same governed context preserves stable output, factor, trace, and raw-output hashing when lineage supersession is explicit
- projection routes are read-only and derive metadata from canonical compatibility bindings
- projection composition fails closed when source evaluation or source trace truth is missing
- replay posture fails closed when required bindings are missing
- stale posture may not be downgraded or silently reset to fresh
- supersession preserves visibility and records append-only lifecycle events
- lifecycle supersession transitions fail closed when temporal ordering is reversed or a lineage cycle would be created
- only governed lifecycle fields may change after persisted evaluation creation
- canonical runtime profiles reject non-deterministic admission
- runtime-admission inspection derives operator-visible recovery posture and action when the bound runtime profile is degraded
- determinism-sensitive migration packages must declare affected deterministic artifacts and bounded migration posture
- Evaluation Spine lineage emission (`app/lineage/spine_emit.py`, on `evaluate_calibration_report_file`) is **opt-in and non-blocking**: it emits only when `FORGEMATH_LINEAGE_URL` is set, and any emission failure is logged while the evaluation still completes. It emits only ForgeMath's own lineage (`forgemath_evaluation`/`forgemath_output` + a `consumed` edge to the discovered upstream `eval_cal_record`); the `non_recalculation` posture of the output payload is unchanged — no downstream recomputation of upstream authority
- The **`forgemath_output` lineage node payload is identity-only** (the canonical `forgemath_output.v1` schema is `additionalProperties:false`: `output_id`/`lane_evaluation_id`/`payload_hash`/`produced_at`/`schema_version`). The rich evaluation result — **including the `proposal_candidate_allowed` gate** — lives in the output **contract artifact**, referenced from the node via `artifact_ref` (`ArtifactRef.v1`: `artifact_id` = the contract path, `payload_hash` = its sha256). A downstream consumer (ForgeCommand's gate-walk) resolves the gate **from the artifact**, never from the node payload — keeping lineage nodes as pure identity and decisions in artifacts

---

## 11. Database Schema

The repo currently ships six schema migrations:

- `20260402_0001_phase1_foundation`
- `20260402_0002_phase2_evaluation_foundation`
- `20260402_0003_phase3_lifecycle_governance`
- `20260402_0004_phase4_runtime_admission`
- `20260402_0005_authority_boundary_and_numeric_hardening`
- `20260403_0006_phase7_durability_and_control_hardening`

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
| `forgemath_migration_packages` | Migration metadata | `migration_id`, `version`, source/target versions, approval state, determinism-sensitive artifacts | controlled migration, approval, and determinism-sensitive artifact vocabulary |
| `forgemath_input_bundles` | Frozen admissible input bundles | `input_bundle_id`, `deterministic_input_hash`, `scope_id` | canonical evaluations require frozen bundle linkage |
| `forgemath_lane_evaluations` | Root canonical evaluation truth | `lane_evaluation_id`, `lane_id`, `compatibility_tuple_hash`, lifecycle columns, `active_canonical_execution_key` | append-only evaluation truth with governed lifecycle fields and unique live canonical execution context |
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

Migration package rows additionally expose:

- `determinism_sensitive_artifacts`

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
- `active_canonical_execution_key`

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

Phase `20260403_0006` further hardens durability and control posture by:

- enforcing unique `active_canonical_execution_key` values across live canonical execution contexts
- backfilling active canonical execution keys for existing governed computed lineage roots
- adding `determinism_sensitive_artifacts` to migration package metadata

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
- temporally reversed supersession transitions fail with `400`
- lineage conflicts or duplicate supersession links fail with `409`
- lineage cycles fail with `409`
- missing lifecycle inspection targets fail with `404`

### 13.4 Runtime Admission Failure Posture

- non-deterministic runtime profiles fail canonical admission with `400`
- incomplete runtime profiles fail canonical admission with `400`
- retired runtime profiles fail canonical admission with `400`
- missing evaluation targets for runtime inspection fail with `404`
- runtime inspection exposes degraded recovery posture instead of silently reporting healthy canonical runtime bindings

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
- duplicate active canonical execution context without explicit supersession fails with `409`

### 13.7 Authority-Boundary Failure Posture

- manual ingest attempts to persist computed canonical truth fail request validation with `422`
- caller-supplied `execution_mode` on the execution route fails request validation with `422`
- caller-supplied raw_output_hash values that do not match the persisted artifact bundle fail with `400`
- incomplete optional prior/decay compatibility bindings fail request validation with `422`
- cross-lane parameter, threshold, or policy bindings fail with `400`
- determinism-sensitive migration packages with missing affected deterministic artifacts fail request validation with `422`
- determinism-sensitive migration packages may not claim `hard_compatible` post-migration posture

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

## 6. Design System

ForgeMath currently has no end-user UI inside this repo.
Phase 1 through Phase 7 remain backend-only, so the design system surface is
limited to JSON contracts, naming consistency, and documentation clarity.

### 6.1 Current UI Posture

| Surface | Status |
|--------|--------|
| In-repo frontend | Not implemented |
| Operator API responses | Implemented as JSON read DTOs |
| External UI consumers | Deferred to downstream services |

---

# Scope

**Document version:** 1.0 (bootstrap scaffold)

Scope and authority boundary of this documentation system.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

# Governance

**Document version:** 1.0 (bootstrap scaffold)

Ownership, review, and change-authority boundaries.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

# Change Control

**Document version:** 1.0 (bootstrap scaffold)

Change-control workflow, proposal lifecycle, and audit.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

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
| `tests/test_phase6_execution.py` | Supported lane execution happy paths, repeatability/hash-stability checks, and fail-closed missing-binding, missing-input, unsupported-lane, invalid-parameter, invalid-threshold, runtime-profile, and variable-registry insufficient-coverage execution checks |
| `tests/test_phase7_hardening.py` | Persistence-level active canonical execution exclusivity, determinism-sensitive migration package validation, runtime-recovery inspection, and supersession hardening checks |
| `tests/test_golden_vectors.py` | Per-factor raw/normalized/weighted value pinning for verification_burden; trace summary format stability (_decimal_to_str edge cases); _clamp_unit saturation at unit ceiling via exposure_factor with saturating coefficient inputs |
| `tests/test_http_contracts.py` | Real HTTP route checks for manual-ingest boundary, execution route behavior, and caller-supplied execution-mode rejection when the environment allows localhost binding |
| `tests/test_postgres_invariants.py` | Postgres-backed migration/schema invariant checks when `FORGEMATH_POSTGRES_TEST_URL` is supplied |

### 14.2 Execution

```bash
python -m pytest tests -q
FORGEMATH_DATABASE_URL=sqlite:///./hardening_verify.db alembic upgrade head
```

### 14.3 Test Boundary

The current suite validates Phase 1 through Phase 7 write logic and invariants.
It also validates the hardening slices for:

- manual-ingest boundary restriction
- derived raw-output hashing
- lane-affinity binding checks
- optional prior/decay compatibility binding enforcement
- computed output/factor payload shape enforcement
- deterministic decimal-string artifact persistence
- active canonical execution conflict handling
- repeatability and hash stability across explicit superseding reruns
- persistence-level active canonical execution uniqueness
- determinism-sensitive migration package metadata rules
- runtime-profile recovery posture derivation on inspection
- supersession temporal-order and cycle protection
- per-factor golden-vector pinning (raw, normalized, weighted values)
- trace summary format stability (_decimal_to_str output for known inputs)
- _clamp_unit saturation at 1.0 when exposure_factor arithmetic exceeds unit ceiling
- variable registry insufficient coverage rejection (registry present, variables missing)
- stale_input_invalidated positive transition path with input_bundle_invalidated evidence
- stale_upstream_changed positive transition path when upstream registry is superseded

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

### 15.2 Completed Hardening (Gap-Closure Pass, 2026-04-04)

Gap-closure hardening pass completed against `forge_math_lane_governance_persistence_replay_and_runtime_contract_v_1_initial.md`. Six gaps were identified and closed:

| Gap | Resolution |
|-----|------------|
| No per-factor golden-vector pinning | `tests/test_golden_vectors.py`: pins raw/normalized/weighted per factor for verification_burden |
| No trace summary format stability test | `tests/test_golden_vectors.py`: pins _decimal_to_str output for known edge values |
| No _clamp_unit > 1.0 path exercised | `tests/test_golden_vectors.py`: exposure_factor with alpha_pub=1.0 + severity="critical" → score 1.25 → clamped 1.0 |
| No variable registry coverage check test | `tests/test_phase6_execution.py`: registry exists but payload.variables insufficient → 400 |
| No stale_input_invalidated positive path | `tests/test_phase3_lifecycle.py`: successful transition with input_bundle_invalidated=True |
| No stale_upstream_changed positive path | `tests/test_phase3_lifecycle.py`: successful transition after variable registry supersession |

**Baseline:** 57 passing tests. **After this hardening pass:** 63 passing tests.

The 4 failures in `test_http_contracts.py` are **not** a DataForge dependency: that module starts a uvicorn subprocess through a hardcoded `PYTHON_BIN` interpreter path, so it fails on any host where that path is absent. They are environment/harness failures, not governance regressions.

**Current suite (2026-06-08):** `python -m pytest tests -q --ignore=tests/lineage` → 72 passing, 1 skipped, 4 failing (the `test_http_contracts.py` cases above). A bare `python -m pytest tests -q` currently aborts during collection because `tests/lineage/` imports the external `forge_lineage_sdk`, which is not in `requirements.txt`.

**Remaining open gap from contract audit:** `forgemath_projection_records` table (contract §11) is not implemented — projections are ephemeral read models in `projection_service.py`. This is architecturally intentional for the current phase and documented as deferred.

### 15.3 Deferred Work

- `forgemath_projection_records` persistence table (contract §11) — projections currently ephemeral
- compatibility resolution engine beyond bounded validation and persisted binding checks
- runtime admission evolution beyond bounded deterministic validation and persisted evidence
- replay workers and queue processors
- stale-state automation engine
- execution expansion beyond the bounded Phase 6 lane wave
- hybrid gate execution and broader multi-lane orchestration
- broader database-level exclusion or partitioning strategies if future execution expansion outgrows the current unique active execution key
- `doc/system/` documentation-scheme consolidation — two chapter numbering schemes currently coexist (the granular content chapters `01-overview-philosophy.md` … `15-handover-migration-notes.md` and the Forge Documentation Protocol v1 skeleton chapters `00-overview.md`, `01-architecture.md`, `10-scope.md`, `20-structure.md`, `30-governance.md`, `40-change-control.md`, `90-appendices.md`). `BUILD.sh` assembles the granular content chapters; consolidating onto one scheme is deferred
- test-harness portability — `tests/test_http_contracts.py` hardcodes `PYTHON_BIN`, and `tests/lineage/` depends on the un-vendored `forge_lineage_sdk`; both should be made environment-independent (e.g. `sys.executable` / guarded optional import)

---

# Structure

**Document version:** 1.0 (bootstrap scaffold)

Module/chapter layout and cross-reference rules.

> This chapter is a registry-generated bootstrap scaffold for a
> `documentation` class documentation system. Replace this placeholder with
> real authored content. Registry will not invent repo truth that is not
> already present in the repo.

---

# Appendices

**Document version:** 1.0 (carry-forward)

Appendices, glossary, and cross-references.

## Unmapped legacy chapters

The following legacy chapters were carried forward but could not be
deterministically mapped to a class-aware slot. Review and place them by
hand:

- `ForgeMath — Complete System Reference`
