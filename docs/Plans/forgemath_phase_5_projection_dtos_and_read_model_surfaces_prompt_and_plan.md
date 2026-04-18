# ForgeMath Phase 5 — Projection DTOs and Read-Model Surfaces Prompt and Plan

**Date:** April 2, 2026  
**Time Zone:** America/New_York

---

## Intended Use

This document is the governed implementation prompt and bounded build plan for **ForgeMath Phase 5**.

Phase 5 is the next slice after:

- Phase 1 — governance registries / foundation
- Phase 2 — canonical evaluation persistence
- Phase 3 — lifecycle governance
- Phase 4 — deterministic runtime admission and canonical execution admission control

This phase exists to add **projection DTOs and read-model surfaces** without collapsing the canonical authority boundary.

It should be used as:

- a VS Code / Codex implementation prompt
- an implementation review reference
- a bounded scope receipt for repo work

---

## Phase 5 Mission

Implement **projection DTOs and read-model surfaces** for ForgeMath.

This phase should make canonical evaluation truth easier to inspect and consume through governed read models while preserving all prior repo boundaries.

The repo must still remain:

- a backend-only canonical authority service
- append-only in canonical truth posture
- fail-closed for invalid or missing governed bindings
- explicit about runtime, replay, stale, and lifecycle posture

This phase does **not** implement the full math engine, replay workers, stale-state automation, UI, or downstream consumer apps.

---

## Repo State Entering Phase 5

ForgeMath currently has:

- versioned governance registries
- immutable governance object posture
- canonical evaluation persistence
- compatibility tuple persistence and validation posture
- lifecycle governance for replay, stale state, recomputation, and supersession lineage
- deterministic runtime admission truth and runtime inspection surface
- regenerated `SYSTEM.md` reflecting Phase 1–4 repo truth

Do not redo prior phases.
Do not widen scope.
Do not redesign the repo.

---

## Role

You are acting as a **bounded implementation engineer** working inside the ForgeMath repository.

You are extending an already-governed backend authority service.
You are **not** acting as a speculative architect.
You are **not** implementing future phases early.

Your job is to make Phase 5 real, reviewable, and safe.

---

## Doctrine Context

This work is governed by BDS AI implementation doctrine.

You must behave as though these rules are mandatory:

- context is not optional
- implementation must be bounded
- verification is part of execution
- human authority remains final
- completion language must be truthful
- do not imply readiness beyond what is actually implemented and verified
- do not invent semantics beyond repo truth and governing specifications
- preserve append-only lineage posture
- preserve canonical truth boundaries
- projection DTOs are read models only
- read models must not become a backdoor source-of-truth write surface
- fail closed when required bindings are missing or invalid

---

## System / Boundary Context

ForgeMath is a **backend-only canonical authority substrate** for governed lane math in the Forge ecosystem.

It sits upstream of downstream consumers and downstream operator surfaces.

That means:

- canonical truth is owned by persisted governance and evaluation tables
- projection DTOs are derived read models only
- consumers may inspect canonical truth through governed projections, but may not recompute or overwrite canonical values
- read-model convenience must never flatten or erase lifecycle, replay, stale, runtime-admission, or audit posture
- blocked, degraded, audit-only, stale, and superseded states must remain visible where relevant

This repo is in controlled implementation posture.
It is an internal business system component, not a public SaaS surface.

---

## Phase 5 Objective

Phase 5 should create the first governed read-model layer for ForgeMath.

That means implementing:

1. projection DTO definitions
2. read-model composition logic
3. bounded read routes for evaluation inspection
4. explicit projection metadata and source bindings
5. tests proving read-model correctness and truth preservation
6. `SYSTEM.md` updates if repo truth changes

The goal is to make canonical evaluations inspectable through stable surfaces that downstream consumers can rely on **without** granting them authority to redefine canonical truth.

---

## Required Projection Surfaces

Phase 5 should implement these projection/read-model surfaces first:

### 1. `LaneEvaluationSummaryModel`

Purpose:

- concise inspection surface for one evaluation or a collection of evaluations
- consumer-safe summary without hiding authority posture

Must include at minimum:

- `lane_evaluation_id`
- `lane_id`
- `lane_spec_version`
- `evaluation_status`
- `result_status`
- `compatibility_resolution_state`
- `deterministic_admission_state`
- `runtime_profile_id`
- `replay_state`
- `stale_state`
- `recomputation_action`
- `superseded_by_evaluation_id`
- `created_at`
- `projection_schema_version`
- `source_compatibility_tuple_hash`

### 2. `LaneEvaluationDetailModel`

Purpose:

- operator/detail inspection surface for one canonical evaluation
- exposes fuller governed context without becoming raw table leakage

Must include at minimum:

- all summary fields
- `input_bundle_id`
- `trace_bundle_id`
- `trace_tier`
- `runtime_validation_reason_code`
- `runtime_validation_reason_detail`
- `determinism_certificate_ref`
- `bit_exact_eligible`
- `lifecycle_reason_code`
- `lifecycle_reason_detail`
- supersession metadata
- projection metadata

### 3. `LaneFactorInspectionModel`

Purpose:

- governed read surface for factor contribution inspection

Must include at minimum:

- `lane_evaluation_id`
- factor list with:
  - `factor_name`
  - `raw_value`
  - `normalized_value`
  - `weighted_value`
  - `omitted_flag`
  - `omission_reason`
  - `provenance_class`
  - `volatility_class`
- projection metadata

### 4. `LaneTraceInspectionModel`

Purpose:

- governed trace inspection surface

Must include at minimum:

- `trace_bundle_id`
- `lane_evaluation_id`
- `trace_tier`
- trace event rows or summaries
- projection metadata
- source bindings

### 5. `LaneReplayDiagnosticModel`

Purpose:

- explicit replay/readiness posture surface for operator use and downstream consumers

Must include at minimum:

- `lane_evaluation_id`
- `replay_state`
- `stale_state`
- `recomputation_action`
- lifecycle reason fields
- runtime-admission summary
- source bindings
- projection metadata

---

## Projection Contract Rules

These rules are mandatory for this phase.

### Rule 1 — Projection DTOs are read models only

No projection DTO may be written back as canonical source truth.

### Rule 2 — Projection metadata must be explicit

Every projection surface must bind to:

- `projection_schema_version`
- `source_evaluation_id`
- `source_compatibility_tuple_hash`

### Rule 3 — Read models must preserve truth-bearing posture

Read models must not hide or flatten:

- `result_status`
- `replay_state`
- `stale_state`
- `compatibility_resolution_state`
- `deterministic_admission_state`
- supersession visibility
- audit-only posture
- blocked posture

### Rule 4 — Missing source truth fails closed

If the source evaluation is missing or invalid for the requested read model, the route must fail closed.

### Rule 5 — Projection convenience must not fabricate meaning

Do not invent derived semantics not already present in repo truth.

### Rule 6 — Projection DTOs must not leak mutation paths

Phase 5 adds read surfaces only.
No projection write routes should be added.

---

## In-Scope Layers

Implement this phase only through these layers:

1. schema/read DTO additions
2. read-model composition service logic
3. bounded read routes
4. optional projection-record persistence integration only if already supported cleanly by repo truth
5. tests
6. `SYSTEM.md` / modular system doc updates if repo truth changes

---

## Preferred Route Additions

Add bounded inspection routes that follow the current API posture.

Recommended additions:

- `GET /api/v1/forgemath/lane-evaluations/{lane_evaluation_id}/summary`
- `GET /api/v1/forgemath/lane-evaluations/{lane_evaluation_id}/detail`
- `GET /api/v1/forgemath/lane-evaluations/{lane_evaluation_id}/factors`
- `GET /api/v1/forgemath/lane-evaluations/{lane_evaluation_id}/trace`
- `GET /api/v1/forgemath/lane-evaluations/{lane_evaluation_id}/replay-diagnostics`

If the repo already has a better naming convention, preserve repo-local consistency.
Do not widen this into general search/query UI or downstream dashboard concerns.

---

## Minimum Source Truth Required For Projection Reads

At minimum, projection composition must be grounded in:

- canonical evaluation row
- bound lifecycle truth
- bound runtime-admission truth
- factor rows where applicable
- trace bundle metadata and/or trace rows where applicable
- compatibility tuple hash
- source evaluation visibility state

If required source truth for a specific projection surface does not exist, fail closed rather than fabricate a partial truth surface unless the repo already has an explicit disclosure pattern.

---

## Constraints

You must preserve all of these:

- do not implement the full math engine
- do not implement replay workers or queue processors
- do not implement stale-state automation workers
- do not implement downstream UI or dashboards
- do not invent new lifecycle semantics
- do not invent new runtime-admission semantics
- do not allow projection DTOs to replace canonical truth tables
- do not add mutation routes for projection models
- do not flatten hybrid/gated posture into scalar-only summaries
- do not hide superseded, stale, blocked, degraded, or audit-only posture when relevant
- keep append-only lineage posture intact

---

## Required Validation Posture

At minimum, projection reads must fail closed unless:

- the source evaluation exists
- required source bindings exist
- source evaluation remains visible under governed read posture
- projection schema version is explicit
- source compatibility tuple hash is available
- lifecycle/runtime posture required for that read model can be expressed truthfully

If a projection surface depends on factors or trace detail, and those surfaces are absent, do not silently downgrade into a misleading success response.

---

## Suggested File Layers

Phase 5 will most likely touch files in categories like:

- `app/schemas/evaluation.py`
- `app/schemas/__init__.py`
- `app/services/evaluation_service.py` or a new bounded projection/read-model service
- `app/api/evaluation_router.py`
- tests for projection/read-model routes and invariants
- `doc/system/*`
- `SYSTEM.md`

Only add new files where they improve clarity.
Do not sprawl the slice unnecessarily.

---

## Acceptance Criteria

This phase counts as successful only if:

- projection DTOs are implemented as explicit read models
- the core Phase 5 read-model surfaces exist
- routes expose bounded evaluation inspection views
- projection responses bind to projection metadata and source compatibility truth
- missing required source truth fails closed
- tests cover happy-path and invalid-path projection reads
- `SYSTEM.md` is updated if repo truth changed
- completion language is truthful about what Phase 5 does and does not implement

---

## Out of Scope

Do not implement these in this phase:

- equation execution engine
- lane scoring or formula computation
- replay queue processors or workers
- stale-state automation jobs
- write-back projection mutation paths
- downstream UI/dashboard work
- broader search/filter/reporting system
- cross-service integration work beyond bounded read surfaces already inside this repo

---

## Review Checklist After Implementation

Review the returned files like a repo engineer.

Check for:

1. **Truth separation**
   - projections remain read-only
   - canonical truth still lives in root tables

2. **Boundary discipline**
   - no mutation routes were added for projections
   - no downstream/UI concerns leaked into repo core

3. **Status preservation**
   - summary/detail surfaces still expose lifecycle and runtime posture
   - audit-only / blocked / stale / superseded truth was not hidden

4. **Source binding clarity**
   - projection schema version is explicit
   - source evaluation id and compatibility tuple hash are explicit

5. **Fail-closed behavior**
   - missing evaluation returns proper failure
   - missing factor/trace dependencies do not produce misleading success

6. **Test sufficiency**
   - one happy-path set
   - one missing-source set
   - one missing-dependent-surface set
   - one superseded/stale visibility set if applicable

7. **SYSTEM truth alignment**
   - `SYSTEM.md` reflects the new Phase 5 repo truth accurately

---

## Execution Prompt

Use this prompt for implementation:

```text
You are acting as a bounded implementation engineer working inside the ForgeMath repository.

You are continuing an already-started governed implementation.

ForgeMath Phase 1 through Phase 4 are already implemented:
- Phase 1: governance registries / foundation
- Phase 2: canonical evaluation persistence
- Phase 3: lifecycle governance
- Phase 4: deterministic runtime admission and canonical execution admission control

Do not redo completed work.
Do not widen scope.
Do not redesign the repo.

Your mission is to implement ForgeMath Phase 5: projection DTOs and read-model surfaces.

ROLE
You are a bounded implementation engineer, not a speculative architect.
Your job is to extend the current repo safely and explicitly.

DOCTRINE CONTEXT
This work is governed by BDS AI implementation doctrine.
You must behave as though these rules are mandatory:
- context is not optional
- implementation must be bounded
- verification is part of execution
- human authority remains final
- completion language must be truthful
- do not imply readiness, safety, or completeness beyond what is actually implemented and verified
- do not invent missing semantics when governing specs already define the allowed vocabulary
- preserve authority boundaries and append-only lineage posture
- projection DTOs are read models only
- read models must not become a backdoor source-of-truth write surface
- fail closed when required bindings or source truth are missing

MISSION CONTEXT
The repo already has the following implemented or established:
- versioned governance registries
- canonical evaluation persistence
- lifecycle governance for replay, stale posture, recomputation posture, and supersession lineage
- deterministic runtime admission truth and runtime inspection
- regenerated SYSTEM.md reflecting Phase 1–4 truth

This slice must now implement:
- projection DTO definitions
- read-model composition logic
- bounded read routes for evaluation inspection
- explicit projection metadata and source bindings
- tests for read-model correctness and fail-closed behavior
- SYSTEM.md updates if repo truth changes

SYSTEM / BOUNDARY CONTEXT
ForgeMath is a backend-only canonical authority substrate.
It sits upstream of downstream consumers.
That means:
- canonical truth remains in persisted governance and evaluation tables
- projection DTOs are derived read models only
- consumers may inspect canonical truth through projections but may not recompute or overwrite canonical values
- read-model convenience must not flatten lifecycle, replay, stale, runtime-admission, or audit posture
- blocked, degraded, audit-only, stale, and superseded truth must remain visible where relevant

This repo is in controlled implementation posture.
It is an internal business system component, not a public SaaS surface.

SPECIFICATION CONTEXT
This slice must establish the governed projection/read-model layer, but it must not yet implement the math engine, replay workers, stale-state automation, UI, or downstream integrations.

The governing doctrine or specification requires:
- projection DTOs are read models only
- every projection surface must bind to projection_schema_version, source_evaluation_id, and source_compatibility_tuple_hash
- read models must preserve result_status, replay_state, stale_state, compatibility_resolution_state, deterministic_admission_state, and supersession visibility
- missing source truth must fail closed
- projection routes are inspection surfaces only, not mutation surfaces

Use these projection surfaces exactly:
- LaneEvaluationSummaryModel
- LaneEvaluationDetailModel
- LaneFactorInspectionModel
- LaneTraceInspectionModel
- LaneReplayDiagnosticModel

TASK
Implement this slice only through these layers:
1. schema/read DTO additions
2. read-model composition service logic
3. bounded read routes
4. tests
5. SYSTEM.md and modular system docs if repo truth changes

MINIMUM FIELD / CONTRACT REQUIREMENTS

1. LaneEvaluationSummaryModel
Support at minimum:
- lane_evaluation_id
- lane_id
- lane_spec_version
- evaluation_status
- result_status
- compatibility_resolution_state
- deterministic_admission_state
- runtime_profile_id
- replay_state
- stale_state
- recomputation_action
- superseded_by_evaluation_id
- created_at
- projection_schema_version
- source_compatibility_tuple_hash

2. LaneEvaluationDetailModel
Support at minimum:
- all summary fields
- input_bundle_id
- trace_bundle_id
- trace_tier
- runtime_validation_reason_code
- runtime_validation_reason_detail
- determinism_certificate_ref
- bit_exact_eligible
- lifecycle_reason_code
- lifecycle_reason_detail
- supersession metadata
- projection metadata

3. LaneFactorInspectionModel
Support at minimum:
- lane_evaluation_id
- factor list with factor_name, raw_value, normalized_value, weighted_value, omitted_flag, omission_reason, provenance_class, volatility_class
- projection metadata

4. LaneTraceInspectionModel
Support at minimum:
- trace_bundle_id
- lane_evaluation_id
- trace_tier
- trace event rows or summaries
- projection metadata
- source bindings

5. LaneReplayDiagnosticModel
Support at minimum:
- lane_evaluation_id
- replay_state
- stale_state
- recomputation_action
- lifecycle reason fields
- runtime-admission summary
- source bindings
- projection metadata

CONSTRAINTS
You must preserve all of these:
- do not implement the full math engine
- do not implement replay workers or queue processors
- do not implement stale-state automation workers
- do not implement downstream UI or dashboards
- do not invent new lifecycle semantics
- do not invent new runtime-admission semantics
- do not allow projection DTOs to replace canonical truth tables
- do not add mutation routes for projection models
- do not flatten hybrid or gated posture into scalar-only summaries
- do not hide superseded, stale, blocked, degraded, or audit-only posture when relevant
- keep append-only lineage posture intact

REQUIRED VALIDATION POSTURE
At minimum, projection reads must fail closed unless:
- the source evaluation exists
- required source bindings exist
- source evaluation remains visible under governed read posture
- projection_schema_version is explicit
- source_compatibility_tuple_hash is available
- lifecycle/runtime posture required for that read model can be expressed truthfully

If a projection surface depends on factors or trace detail, and those surfaces are absent, do not silently downgrade into a misleading success response.

OUTPUT FORMAT
Return your work in bounded implementation form.

For every changed file:
1. exact path
2. why the file exists
3. full implementation content

Then provide:
- what was created
- what invariants are enforced
- what tests were added
- what remains for the next phase
- exact commands to run for validation

Do not give vague summaries instead of concrete repo work.

ACCEPTANCE CRITERIA
This slice counts as successful only if:
- projection DTOs are implemented as explicit read models
- the core Phase 5 read-model surfaces exist
- routes expose bounded evaluation inspection views
- projection responses bind to projection metadata and source compatibility truth
- missing required source truth fails closed
- tests cover happy-path and invalid-path projection reads
- SYSTEM.md is updated if repo truth changed
- completion language is truthful about what this slice does and does not yet implement

OUT OF SCOPE
Do not implement these in this session:
- equation execution engine
- lane scoring or formula computation
- replay workers and queue processors
- stale-state automation jobs
- write-back projection mutation paths
- downstream UI/dashboard work
- broader search/filter/reporting system
- cross-service integration work beyond bounded read surfaces already inside this repo

READ THESE FIRST BEFORE CHANGING CODE
1. BDS AI implementation doctrine materials already in context
2. SYSTEM.md
3. current Phase 4 implementation receipt / summary
4. forge_math_canonical_equation_stack_top_level_overview.md
5. forge_math_lane_governance_persistence_replay_and_runtime_contract_v_1_initial.md
6. forge_math_persistence_compatibility_and_replay_plan.md
7. forge_math_enterprise_readiness_hardening_addendum.md

FINAL REMINDER
This is a bounded build slice.
The goal is not to make ForgeMath done.
The goal is to make ForgeMath’s Phase 5 projection/read-model layer real, governed, testable, and safe to review.
```

---

## Planned Validation Commands

Use or adapt these after implementation:

```bash
cd /home/charlie/Forge/ecosystem/ForgeMath
python3 -m compileall app tests
/home/charlie/Forge/ecosystem/DataForge/.venv/bin/python -m pytest tests -q
FORGEMATH_DATABASE_URL=sqlite:///./phase5_verify.db /home/charlie/Forge/ecosystem/DataForge/.venv/bin/alembic upgrade head
./doc/system/BUILD.sh
```

If Phase 5 touches Postgres-specific behavior or query posture, add a live Postgres validation pass during review.

---

## Intended Next Step After Phase 5

After Phase 5 is accepted, the likely next slice is:

- **Phase 6: deeper migration/security/workload hardening or initial execution-engine substrate**, depending on repo readiness and your chosen sequence.

That decision should be made after Phase 5 code review lands.

