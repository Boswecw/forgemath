# ForgeMath - Compiled System Reference

**Designation:** MAT
**Document role:** Canonical compiled technical reference for ForgeMath
**Source:** `doc/system/`
**Build command:** `bash doc/system/BUILD.sh`
**Document version:** 2.1 (2026-08-16) - truth reconciliation and qualification
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
snapshot facts are dated evidence such as current implementation inventory or
qualification results and must name their date and reproduction command.

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

> **System identity — bds family (Boswell Digital Solutions business system, local-systems tier).** ForgeMath is the Forge ecosystem's backend canonical math and governed rule-evaluation authority under `ecosystem/local-systems`.

ForgeMath owns versioned governance registries, canonical evaluation and
lifecycle truth, deterministic runtime-admission evidence, bounded execution,
and truth-preserving projections. It also provides a distinct file-based
Evaluation Spine CLI and optional ForgeLineage emission.

Its authority is intentionally bounded. ForgeMath is not a helper library, a
general policy engine, a symbolic-algebra service, or an arbitrary expression
executor. Human-approved typed contracts and code define the supported math.

The current FastAPI execution surface supports exactly three governed lanes:
`verification_burden`, `recurrence_pressure`, and `exposure_factor`.

---

# Architecture Surfaces

ForgeMath exposes two distinct authority surfaces:

1. The FastAPI service routes governed registry writes and reads, manual
   non-computed ingest, canonical bounded lane execution, lifecycle and
   admission inspection, and projections through SQLAlchemy persistence.
2. The Evaluation Spine CLI reads a calibration-report contract and writes a
   deterministic ForgeMath contract artifact. It does not call the FastAPI
   lane-execution route and does not expand the three registered API lanes.

The lightweight health CLI is a third operational interface, not a math lane.
Its default mode checks only the Evaluation Spine CLI import surface for
Forge_Command. Explicit `--readiness` mode inspects local service readiness
without creating or migrating a database or contacting lineage transport.

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

The HTTP route is separate from the operational CLI health contract.
`python -m app.health_cli` is Forge_Command's lightweight Evaluation Spine
producer probe and does not inspect the database or FastAPI readiness.
`python -m app.health_cli --readiness` explicitly inspects configuration, an
existing database, migration alignment, FastAPI construction, supported-lane
registration, and optional lineage configuration without mutating state.

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

This route supports exactly `verification_burden`, `recurrence_pressure`, and
`exposure_factor`. It does not execute the Evaluation Spine CLI lane contract
or caller-supplied expressions.

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

ForgeMath keeps its canonical math locally owned while exposing explicit,
bounded integration surfaces. Optional integration is not equivalent to no
integration: the Evaluation Spine file evaluation remains usable when lineage
is disabled or unavailable.

### 10.1 Current Integration State

| Service | Current relationship | Notes |
|--------|----------------------|-------|
| DataForge-Local | Optional ForgeLineage destination | When `FORGEMATH_LINEAGE_URL` is set, the Evaluation Spine flow emits ForgeMath-owned evaluation/output nodes and an optional consumed edge; default-off and non-blocking |
| Forge_Command | Health and artifact consumer | Invokes `python -m app.health_cli`; its gate walk may resolve the rich output contract artifact referenced by lineage |
| ForgeLineage | Pinned SDK contract | CI checks out a fixed SDK revision for lineage tests; the transport is never contacted by readiness |
| NeuroForge | None | No runtime AI inference path in this repository |

### 10.2 Evaluation Spine Boundary

`python -m app.evaluation_spine_cli` is a deterministic file-in/file-out
authority. It consumes an eval-calibration report and writes a ForgeMath lane
evaluation reference contract. This is distinct from the FastAPI bounded
execution service and does not add a fourth registered API execution lane.

The emitted `forgemath_output` node remains identity-only. The rich evaluation
result and `proposal_candidate_allowed` gate live in the referenced contract
artifact for Forge_Command to resolve.

### 10.3 Governance Inputs

The repo is grounded by external governing docs, but those documents are not
runtime dependencies. They are operator and design inputs.


---

## 7. Frontend

No frontend implementation exists in the current repository state. Operator
interaction is through documentation, migrations, HTTP routes, and CLI
contracts.

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
| `app/services/execution_service.py` | bounded canonical execution for the three supported lanes, supported-lane contract validation, and active execution lineage control |
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
- bounded execution supports only `verification_burden`, `recurrence_pressure`, and `exposure_factor` in the `canonical_numeric` lane family
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
- arbitrary caller-supplied expressions are never evaluated; supported math remains defined by typed governed contracts and repository code

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

ForgeMath has no runtime AI inference integration. AI involvement is limited to
the governed development workflow described by repository and BDS protocols.

### 12.1 Current AI Posture

| Area | Status |
|------|--------|
| Runtime inference | Not implemented |
| Provider routing | Not implemented |
| AI-assisted development | Active, bounded by `AGENTS.md`, canonical docs, tests, and BDS doctrine |


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

- lanes outside `verification_burden`, `recurrence_pressure`, and `exposure_factor` fail execution with `400`
- missing required input variables fail execution with `400`
- missing governance bindings fail execution with `404`
- runtime profiles outside the supported deterministic execution substrate fail execution with `400`
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
| httpx | `0.27.2` | FastAPI-compatible request tooling and dependency surface |

`pydantic` and `jsonschema` use bounded ranges rather than exact full-lock
resolution. CI's clean dependency installation tests the resolved set, but a
reproducible lock or constraints-file decision remains a separate dependency
governance follow-up.


---

## 6. Design System

ForgeMath currently has no end-user UI inside this repo.
The repository remains backend-only, so the design system surface is limited
to JSON contracts, naming consistency, and documentation clarity.

### 6.1 Current UI Posture

| Surface | Status |
|--------|--------|
| In-repo frontend | Not implemented |
| Operator API responses | Implemented as JSON read DTOs |
| External UI consumers | Deferred to downstream services |

---

# Scope

In scope are the ForgeMath-owned governance registries, canonical evaluation
records, lifecycle and runtime-admission evidence, read projections, bounded
execution for the three registered lanes, the Evaluation Spine CLI contract,
and ForgeMath-owned lineage emission.

Out of scope are arbitrary expression execution, new lanes without separate
governance approval, changes to canonical formulas or numerical semantics,
downstream recomputation of upstream authority, deployment, external-service
configuration, and changes to DataForge-Local or Forge_Command.

---

# Governance

Governed payload truth is append-only and versioned. Supersession closes prior
truth while preserving history; only explicit lifecycle fields may change in
place. Missing or incompatible bindings, retired or non-deterministic runtime
profiles, and cross-lane relationships fail closed.

Computed canonical truth enters through the governed execution service.
Manual evaluation ingest is limited to non-computed historical or audit
records. Projections remain derived read models and never become source truth.

Formula, weight, threshold, rounding, quantization, and supported-lane changes
require explicit mathematical governance and updated golden evidence. Caller-
supplied expressions are prohibited.

---

# Change Control

Changes must remain bounded, preserve fail-closed authority, and update code,
contracts, tests, migrations, and canonical documentation together when those
surfaces are affected. Applied Alembic migrations are immutable; schema changes
receive a new migration.

A pull request records compatibility impact, migration and complete-suite
evidence, health output, documentation assembly and drift evidence, confirmed
mathematical-semantics posture, deferred external operations, and rollback
instructions. Merge and deployment require separate authority.

---

## 5. Configuration & Environment

### 5.1 Environment Variables

| Variable | Type | Default | Read by |
|---------|------|---------|---------|
| `FORGEMATH_DATABASE_URL` | string | `sqlite:///./forgemath.db` | `app/config.py`, `app/database.py`, `alembic/env.py` |
| `FORGEMATH_HOST` | string | `127.0.0.1` | `app/config.py` |
| `FORGEMATH_PORT` | integer | `8011` | `app/config.py` |
| `FORGEMATH_LINEAGE_URL` | URL | unset (disabled) | `app/lineage/spine_emit.py`, readiness configuration check |
| `FORGEMATH_LINEAGE_TOKEN` | string | unset | `app/lineage/spine_emit.py`, readiness configuration check |

### 5.2 Validation Rules

- database URL must not be empty
- host must not be empty
- port must be between `1` and `65535`
- a configured lineage URL must be an absolute HTTP(S) URL
- a lineage token without a lineage URL is a degraded configuration

### 5.3 Health Modes

- `python -m app.health_cli` checks only Evaluation Spine authority and contract
  imports. Database, migrations, FastAPI construction, lane registration, and
  lineage transport are explicitly reported as not checked.
- `python -m app.health_cli --readiness` validates configuration, connects to an
  existing configured database, compares its Alembic revision with repository
  heads, constructs FastAPI, verifies the exact supported lane set, and checks
  optional lineage URL and SDK availability when enabled. It never creates a database, applies a
  migration, sends lineage, mutates truth, or contacts an unconfigured service.


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
| `tests/test_property_invariants.py` | Hypothesis-generated decimal serialization, formula bounds and monotonicity, replay posture, lifecycle severity, and stateful append-only supersession-chain invariants |
| `tests/test_http_contracts.py` | Real HTTP route checks for manual-ingest boundary, execution route behavior, and caller-supplied execution-mode rejection when the environment allows localhost binding |
| `tests/test_postgres_invariants.py` | Postgres-backed migration/schema invariant checks when `FORGEMATH_POSTGRES_TEST_URL` is supplied |
| `tests/test_evaluation_spine_phase05.py` | Evaluation Spine contract validation, deterministic decimal scoring, file runner, and fail-closed input behavior |
| `tests/lineage/` | ForgeLineage emission, identity-only node posture, upstream discovery, non-blocking failure, and default-off behavior against the pinned SDK |
| `tests/test_health_cli.py` | Lightweight health contract, real version reporting, degraded imports, and optional-lineage readiness posture |

### 14.2 Execution

```bash
FORGEMATH_DATABASE_URL=sqlite:///./qualification.sqlite3 alembic upgrade head
PYTHONPATH=.ci/forge_lineage/sdk python -m pytest tests -q
python -m app.health_cli
FORGEMATH_DATABASE_URL=sqlite:///./qualification.sqlite3 python -m app.health_cli --readiness
bash doc/system/BUILD.sh
bash doc/system/validate_snapshots.sh
git diff --exit-code -- doc/MATSYSTEM.md
```

CI checks out the ForgeLineage SDK at the revision pinned in
`.github/workflows/ci.yml` before running the complete suite. Test database
paths use the host temporary directory so the same suite runs on Windows and
POSIX hosts.

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
- property-generated decimal serialization round trips without exponent notation
- property-generated formula inputs preserve canonical bounds, determinism, and monotonicity
- property-generated replay postures preserve compatibility and audit-result restrictions
- property-generated lifecycle sequences never reduce stale-state severity
- stateful supersession sequences preserve one active canonical truth and an acyclic append-only lineage chain

HTTP route checks and Postgres-backed invariant checks are present but may skip in
restricted environments that block localhost binding or do not provide a Postgres URL.
The Postgres skip is explicit and reproducible: supply
`FORGEMATH_POSTGRES_TEST_URL` to enable it. CI does not silently ignore any
other test failure.

Exact pass counts are qualification evidence, not canonical facts. Reproduce
the current inventory with the complete command above; PRs record the observed
result and environment at review time instead of preserving stale counts here.

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

### 15.2 Qualification Posture

The authoritative verification path is `.github/workflows/ci.yml` plus the
commands in §14. CI installs dependencies, applies every migration to a clean
temporary SQLite database, runs the complete suite with the pinned
ForgeLineage SDK, validates both health modes, assembles and validates canonical
documentation, and fails on generated-document drift.

Test counts are dated evidence rather than system truth. Re-run the complete
command and record the observed pass/skip result in the pull request. The only
documented environment-dependent tests are localhost HTTP tests when socket
binding is prohibited and the Postgres schema invariant when
`FORGEMATH_POSTGRES_TEST_URL` is absent.

The `forgemath_projection_records` table described by an earlier contract is
not implemented. Current projections are intentional ephemeral read models in
`projection_service.py` and do not own truth.

### 15.3 Deferred Work

- `forgemath_projection_records` persistence table (contract §11) — projections currently ephemeral
- compatibility resolution engine beyond bounded validation and persisted binding checks
- runtime admission evolution beyond bounded deterministic validation and persisted evidence
- replay workers and queue processors
- stale-state automation engine
- execution expansion beyond `verification_burden`, `recurrence_pressure`, and `exposure_factor`
- hybrid gate execution and broader multi-lane orchestration
- broader database-level exclusion or partitioning strategies if future execution expansion outgrows the current unique active execution key
- a locked or constraints-based resolution for the currently ranged Pydantic and JSON Schema dependencies
- operational deployment evidence, branch-protection policy, and external-service readiness, which remain outside this repository change

---

# Structure

`doc/system/` is the authored modular source tree. `BUILD.sh` concatenates
`_index.md` and every two-digit chapter in stable path order, validates the
assembled snapshot, and writes `doc/MATSYSTEM.md`. The assembled document is a
generated review artifact and must have no hand-authored drift.

Root `AGENTS.md` defines repository working rules. `CLAUDE.md` is a concise
agent-specific companion, `README.md` is an operator entry point, and `docs/`
contains design references or historical context.

---

# Appendices

## Terms

- **Canonical truth:** governed persisted records that own evaluation or
  registry authority.
- **Evaluation Spine CLI:** the file-in/file-out calibration authority, distinct
  from the FastAPI lane-execution service.
- **ForgeLineage emission:** default-off, opt-in publication of ForgeMath-owned
  lineage through the pinned SDK.
- **Readiness:** non-destructive inspection of configured local service
  dependencies; it never creates or migrates a database or sends lineage.
