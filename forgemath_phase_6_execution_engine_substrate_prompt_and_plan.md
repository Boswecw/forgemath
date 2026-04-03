# ForgeMath Phase 6 — Initial Execution Engine Substrate Prompt and Plan

**Date:** April 2, 2026  
**Time Zone:** America/New_York

---

## Intended Use

This document is the governed implementation prompt and bounded build plan for **ForgeMath Phase 6**.

Phase 6 follows:

- Phase 1 — governance registries / foundation
- Phase 2 — canonical evaluation persistence
- Phase 3 — lifecycle governance
- Phase 4 — deterministic runtime admission and canonical execution admission control
- Phase 5 — projection DTOs and read-model surfaces

This phase exists to add the **initial execution-engine substrate** for canonical lane execution without jumping ahead into replay workers, stale-state automation, downstream UI, or broad distribution concerns.

It should be used as:

- a VS Code / Codex implementation prompt
- an implementation review reference
- a bounded scope receipt for repo work

---

## Phase 6 Mission

Implement the **initial execution-engine substrate** for ForgeMath.

This phase should establish the first governed execution path that can take an already-admitted canonical input bundle and bindings, run a bounded canonical lane computation, and persist the resulting evaluation truth through the existing authority surface.

The repo must still remain:

- a backend-only canonical authority service
- append-only in canonical truth posture
- fail-closed for invalid or missing governed bindings
- explicit about runtime, replay, stale, lifecycle, and runtime-admission posture
- bounded to initial execution capability only

This phase does **not** implement replay workers, stale-state automation jobs, downstream UI, public integrations, or full multi-lane orchestration.

---

## Repo State Entering Phase 6

ForgeMath currently has:

- versioned governance registries
- immutable governance object posture
- canonical evaluation persistence
- compatibility tuple persistence and validation posture
- lifecycle governance for replay, stale state, recomputation, and supersession lineage
- deterministic runtime admission truth and runtime inspection surface
- projection DTOs and bounded read-model routes
- regenerated `SYSTEM.md` reflecting Phase 1–5 repo truth

Do not redo prior phases.
Do not widen scope.
Do not redesign the repo.

---

## Role

You are acting as a **bounded implementation engineer** working inside the ForgeMath repository.

You are extending an already-governed backend authority service.
You are **not** acting as a speculative architect.
You are **not** implementing future phases early.

Your job is to make Phase 6 real, reviewable, and safe.

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
- canonical execution must remain governed and fail closed
- execution convenience must not bypass compatibility, runtime-admission, or lifecycle truth
- read models remain read models only
- fail closed when required bindings are missing or invalid

---

## System / Boundary Context

ForgeMath is a **backend-only canonical authority substrate** for governed lane math in the Forge ecosystem.

It sits upstream of downstream consumers and operator surfaces.

That means:

- canonical truth is owned by persisted governance and evaluation tables
- execution must produce canonical truth only through governed repo paths
- execution must bind to lane specs, immutable registries, runtime profile truth, frozen input bundles, and compatibility truth
- downstream consumers may inspect results, but may not define canonical math independently
- execution substrate convenience must not flatten blocked, degraded, audit-only, stale, or superseded posture

This repo is in controlled implementation posture.
It is an internal business system component, not a public SaaS surface.

---

## Phase 6 Objective

Phase 6 should create the **first bounded execution-engine substrate** for ForgeMath.

That means implementing:

1. an execution request contract for bounded canonical execution
2. execution orchestration/service logic for an initial lane wave
3. deterministic factor extraction / normalization / output derivation for the allowed initial lanes
4. persistence through existing canonical evaluation/output/factor/trace tables
5. bounded execution routes
6. tests proving execution correctness and fail-closed governance behavior
7. `SYSTEM.md` updates if repo truth changes

The goal is to make the first canonical lane computations real **without** opening the door to uncontrolled orchestration or premature multi-phase complexity.

---

## Initial Lane Scope

Phase 6 should implement only the **first bounded lane wave**.

Recommended initial execution lanes:

- `verification_burden`
- `recurrence_pressure`
- `exposure_factor`

Optional only if repo structure stays clean and tests remain strong:

- `priority_score`

Do **not** implement `reviewability` as a full hybrid gate execution lane in this phase unless the repo already has an unmistakably safe pattern for that posture.
That lane is more governance-sensitive and can wait if needed.

Do **not** implement the full second wave yet:

- `control_effectiveness`
- `governance_velocity`
- `residual_governance_risk`
- `improvement_yield`

---

## Required Execution Surfaces

Phase 6 should add or formalize these surfaces first:

### 1. Execution request DTO(s)

Purpose:

- bounded canonical execution request surface
- explicit binding to existing governed objects

Must include at minimum:

- `lane_id`
- `lane_spec_version`
- `variable_registry_id` / version binding as already required by repo posture
- `parameter_set_id` / version
- `threshold_set_id` / version where required
- `policy_bundle_id` / version where required
- `runtime_profile_id` / version
- `input_bundle_id`
- `execution_mode`
- `created_by` or equivalent operator/source actor field if repo patterns require it

### 2. Execution result persistence path

Purpose:

- run canonical execution only after required governed checks pass
- persist evaluation, factor, output, and trace truth through canonical tables

### 3. Execution service logic

Purpose:

- resolve required governed objects
- validate execution admissibility
- compute bounded lane output deterministically
- derive factor rows and output rows
- create a canonical evaluation record via governed service logic

### 4. Bounded execution route(s)

Purpose:

- allow operator/API-triggered canonical execution through explicit repo routes

Recommended route shape:

- `POST /api/v1/forgemath/lane-executions`
- optional `GET /api/v1/forgemath/lane-executions/{id}` only if repo uses a distinct execution-receipt surface cleanly

If reusing existing evaluation creation routes is cleaner, preserve repo-local consistency, but do not blur direct persistence DTOs with execution DTOs.

---

## Governing Execution Rules

These rules are mandatory for this phase.

### Rule 1 — Execution must remain compatibility-bound

No canonical execution may occur unless the required compatibility tuple resolves under existing repo truth.

### Rule 2 — Execution must remain runtime-bound

No canonical execution may occur unless deterministic runtime admission is valid for the requested runtime profile.

### Rule 3 — Execution must remain input-bound

No canonical execution may occur without a frozen admissible input bundle.

### Rule 4 — Execution must remain lane-spec-bound

No canonical execution may occur unless the requested lane spec is active, version-bound, and matches the requested lane.

### Rule 5 — Execution must remain deterministic

Factor extraction order, normalization order, weighting order, and output derivation must be stable and explicit.

### Rule 6 — Execution must emit canonical persistence truth

Successful execution must persist:

- root evaluation row
- output rows
- factor rows
- trace bundle metadata
- trace rows if required by the chosen trace tier

### Rule 7 — Execution must fail closed

Missing or invalid bindings, inadmissible runtime posture, unsupported lanes, or missing required input values must fail closed.

### Rule 8 — This phase is substrate, not orchestration

No replay engine, mass recompute engine, or background queue orchestration should be added in this phase.

---

## Expected Equation / Rule Posture

Use the existing ForgeMath equation specifications already carried in project context as the governing math contract.

Do not invent alternate formulas.
Do not substitute approximate semantics.
Do not widen lane meaning.

For the initial implemented lanes, the service should do only what is already authorized by the canonical equation stack and its admitted variables.

---

## In-Scope Layers

Implement this phase only through these layers:

1. execution request/response schema additions
2. bounded execution service logic
3. factor/output/trace derivation logic for initial lanes
4. bounded execution route(s)
5. tests
6. `SYSTEM.md` / modular system doc updates if repo truth changes

Use new files only where they improve clarity.
Avoid unnecessary sprawl.

---

## Minimum Execution Validation Requirements

At minimum, canonical execution must fail closed unless:

- the requested lane spec exists and is active
- the requested parameter set exists, is version-bound, and matches the lane
- the requested threshold set exists when the lane requires it
- the requested policy bundle exists when required
- the runtime profile exists and remains canonically admissible
- the input bundle exists and is frozen/admissible
- the compatibility tuple hash can be resolved truthfully
- all required input variables for the lane are present
- the lane is in the supported Phase 6 execution set

If any required input value is missing, do not silently degrade into guessed values.
Block or mark governed degraded posture only if that posture is already explicitly supported by existing repo truth for that lane.

---

## Trace Expectations

Phase 6 should honor the existing trace posture doctrine.

At minimum:

- the initial lanes must produce trace bundle metadata
- factor derivation should remain inspectable
- blocked execution attempts should not create fake successful evaluation rows
- if a lane’s trace requirements cannot be satisfied truthfully, execution must fail closed or remain out of scope

Keep this slice pragmatic. Do not overbuild full trace richness if the repo is not ready, but do not underbuild trace posture to the point that execution truth becomes opaque.

---

## Constraints

You must preserve all of these:

- do not implement replay workers or queue processors
- do not implement stale-state automation workers
- do not implement downstream UI or dashboards
- do not invent new lifecycle semantics
- do not invent new runtime-admission semantics
- do not invent alternate lane formulas
- do not implement the full lane family set if that broadens risk too much
- do not allow execution DTOs to bypass governed persistence logic
- do not mutate prior evaluations in place
- do not hide blocked, degraded, stale, audit-only, or superseded posture when relevant
- keep append-only lineage posture intact

---

## Suggested File Layers

Phase 6 will most likely touch files in categories like:

- `app/schemas/evaluation.py` and/or a new execution schema file
- `app/schemas/__init__.py`
- `app/services/evaluation_service.py`
- `app/services/runtime_admission_service.py` if small integration updates are required
- a new bounded execution service file if cleaner
- `app/api/evaluation_router.py` or a new bounded execution router if cleaner
- tests for execution happy-path and invalid-path behavior
- `doc/system/*`
- `SYSTEM.md`

If execution receipts or execution-request records require new persistence support, add a migration **only if clearly necessary**. Do not invent new tables just because execution exists.

---

## Acceptance Criteria

This phase counts as successful only if:

- at least the first bounded lane wave can execute canonically through governed service logic
- execution is compatibility-bound, runtime-bound, and input-bound
- successful execution persists canonical evaluation/output/factor/trace truth through existing governed tables
- missing required bindings or inputs fail closed
- unsupported lanes fail closed
- tests cover happy-path and invalid-path execution
- `SYSTEM.md` is updated if repo truth changed
- completion language is truthful about what Phase 6 does and does not implement

---

## Out of Scope

Do not implement these in this phase:

- replay queue processors or replay workers
- stale-state automation jobs
- downstream UI/dashboard work
- public integration surfaces
- full hybrid reviewability execution if it complicates the slice beyond safe substrate work
- broad batch execution/orchestration engine
- mass recomputation engine
- cross-service distribution work

---

## Review Checklist After Implementation

Review the returned files like a repo engineer.

Check for:

1. **Execution boundary discipline**
   - execution enters through bounded governed routes
   - execution does not bypass compatibility/runtime/input checks

2. **Truth preservation**
   - canonical results still land in governed tables
   - projections remain read-only downstream surfaces

3. **Formula discipline**
   - implemented lanes match the governed equation docs
   - no invented semantics or silent approximations

4. **Determinism discipline**
   - factor and output derivation order is stable
   - runtime-admission truth remains aligned with execution behavior

5. **Fail-closed posture**
   - missing bindings block execution
   - unsupported lanes block execution
   - missing required input values block execution

6. **Trace / factor sufficiency**
   - factor rows exist and are inspectable
   - trace bundle posture is truthfully represented

7. **Test sufficiency**
   - one happy-path per implemented lane family or lane type
   - missing-binding failure case
   - unsupported-lane failure case
   - missing-input failure case
   - runtime-inadmissible failure case

8. **SYSTEM truth alignment**
   - `SYSTEM.md` reflects the new Phase 6 repo truth accurately

---

## Execution Prompt

Use this prompt for implementation:

```text
You are acting as a bounded implementation engineer working inside the ForgeMath repository.

You are continuing an already-started governed implementation.

ForgeMath Phase 1 through Phase 5 are already implemented:
- Phase 1: governance registries / foundation
- Phase 2: canonical evaluation persistence
- Phase 3: lifecycle governance
- Phase 4: deterministic runtime admission and canonical execution admission control
- Phase 5: projection DTOs and read-model surfaces

Do not redo completed work.
Do not widen scope.
Do not redesign the repo.

Your mission is to implement ForgeMath Phase 6: initial execution-engine substrate.

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
- canonical execution must remain governed and fail closed
- execution convenience must not bypass compatibility, runtime-admission, or lifecycle truth
- read models remain read models only
- fail closed when required bindings, source truth, or required input values are missing

MISSION CONTEXT
The repo already has the following implemented or established:
- versioned governance registries
- canonical evaluation persistence
- lifecycle governance for replay, stale posture, recomputation posture, and supersession lineage
- deterministic runtime admission truth and runtime inspection
- projection DTOs and bounded read-model routes
- regenerated SYSTEM.md reflecting Phase 1–5 truth

This slice must now implement:
- bounded execution request/response DTOs
- governed execution service logic for the initial lane wave
- deterministic factor/output/trace derivation for supported lanes
- bounded execution route(s)
- tests for execution correctness and fail-closed behavior
- SYSTEM.md updates if repo truth changes

SYSTEM / BOUNDARY CONTEXT
ForgeMath is a backend-only canonical authority substrate.
It sits upstream of downstream consumers.
That means:
- canonical truth remains in persisted governance and evaluation tables
- execution must produce canonical truth only through governed repo paths
- execution must bind to lane specs, immutable registries, runtime profile truth, frozen input bundles, and compatibility truth
- downstream consumers may inspect results, but may not define canonical math independently
- execution convenience must not flatten blocked, degraded, audit-only, stale, or superseded posture

This repo is in controlled implementation posture.
It is an internal business system component, not a public SaaS surface.

SPECIFICATION CONTEXT
This slice must establish the initial execution-engine substrate, but it must not yet implement replay workers, stale-state automation, downstream UI, public integrations, or broad multi-lane orchestration.

Use the existing governed equation documents already in repo context as the canonical math contract.
Do not invent alternate formulas.

The governing doctrine or specification requires:
- execution must remain compatibility-bound
- execution must remain runtime-bound
- execution must remain input-bound
- supported execution lanes in this phase are limited to the initial bounded wave
- successful execution must persist evaluation/output/factor/trace truth through governed tables
- missing required bindings or inputs must fail closed
- unsupported lanes must fail closed

Supported lane scope for this phase:
- verification_burden
- recurrence_pressure
- exposure_factor
- optionally priority_score only if repo structure remains clean and tests remain strong

Do not implement:
- full hybrid reviewability lane execution unless there is already a clearly safe repo-local pattern
- control_effectiveness
- governance_velocity
- residual_governance_risk
- improvement_yield

TASK
Implement this slice only through these layers:
1. execution request/response schema additions
2. bounded execution service logic
3. factor/output/trace derivation logic for the supported initial lanes
4. bounded execution route(s)
5. tests
6. SYSTEM.md and modular system docs if repo truth changes

MINIMUM FIELD / CONTRACT REQUIREMENTS

1. Execution request DTO
Support at minimum:
- lane_id
- lane_spec_version
- variable registry binding
- parameter set binding
- threshold set binding where required
- policy bundle binding where required
- runtime profile binding
- input_bundle_id
- execution_mode

2. Successful execution persistence path
Support at minimum:
- root evaluation record
- factor rows
- output rows
- trace bundle metadata
- trace rows if required by trace posture
- compatibility tuple hash
- runtime admission truth aligned with existing repo behavior

3. Fail-closed execution validation
Support at minimum:
- missing lane spec blocks
- inactive or mismatched lane binding blocks
- missing required governed objects block
- missing required input values block
- runtime-inadmissible profile blocks
- unsupported lane blocks

CONSTRAINTS
You must preserve all of these:
- do not implement replay workers or queue processors
- do not implement stale-state automation workers
- do not implement downstream UI or dashboards
- do not invent new lifecycle semantics
- do not invent new runtime-admission semantics
- do not invent alternate lane formulas
- do not allow execution DTOs to bypass governed persistence logic
- do not mutate prior evaluations in place
- do not hide blocked, degraded, stale, audit-only, or superseded posture when relevant
- keep append-only lineage posture intact

REQUIRED VALIDATION POSTURE
At minimum, canonical execution must fail closed unless:
- the requested lane spec exists and is active
- the requested parameter set exists, is version-bound, and matches the lane
- the requested threshold set exists when the lane requires it
- the requested policy bundle exists when required
- the runtime profile exists and remains canonically admissible
- the input bundle exists and is frozen/admissible
- the compatibility tuple hash can be resolved truthfully
- all required input variables for the lane are present
- the lane is in the supported Phase 6 execution set

If any required input value is missing, do not silently degrade into guessed values.

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
- at least the first bounded lane wave can execute canonically through governed service logic
- execution is compatibility-bound, runtime-bound, and input-bound
- successful execution persists canonical evaluation/output/factor/trace truth through existing governed tables
- missing required bindings or inputs fail closed
- unsupported lanes fail closed
- tests cover happy-path and invalid-path execution
- SYSTEM.md is updated if repo truth changed
- completion language is truthful about what this slice does and does not yet implement

OUT OF SCOPE
Do not implement these in this session:
- replay queue processors or workers
- stale-state automation jobs
- downstream UI/dashboard work
- public integration surfaces
- full hybrid reviewability execution if it complicates the slice beyond safe substrate work
- broad batch execution/orchestration engine
- mass recomputation engine
- cross-service distribution work

READ THESE FIRST BEFORE CHANGING CODE
1. BDS AI implementation doctrine materials already in context
2. SYSTEM.md
3. current Phase 5 implementation receipt / summary
4. forge_math_canonical_equation_stack_top_level_overview.md
5. forge_math_canonical_equation_specification_v_1_initial.md
6. forge_math_lane_governance_persistence_replay_and_runtime_contract_v_1_initial.md
7. forge_math_persistence_compatibility_and_replay_plan.md
8. forge_math_enterprise_readiness_hardening_addendum.md

FINAL REMINDER
This is a bounded build slice.
The goal is not to make ForgeMath done.
The goal is to make ForgeMath’s Phase 6 initial execution-engine substrate real, governed, testable, and safe to review.
```

---

## Planned Validation Commands

Use or adapt these after implementation:

```bash
cd /home/charlie/Forge/ecosystem/ForgeMath
python3 -m compileall app tests
/home/charlie/Forge/ecosystem/DataForge/.venv/bin/python -m pytest tests -q
FORGEMATH_DATABASE_URL=sqlite:///./phase6_verify.db /home/charlie/Forge/ecosystem/DataForge/.venv/bin/alembic upgrade head
./doc/system/BUILD.sh
```

Add a live Postgres validation pass during review if this phase adds or changes persistence behavior beyond the existing SQLite verification posture.

---

## Intended Next Step After Phase 6

After Phase 6 is accepted, the likely next slice is one of these:

- **Phase 7: replay-worker and stale-state automation substrate**
- **Phase 7: execution hardening, migration/security/workload control, and broader lane rollout**

That choice should be made after Phase 6 code review lands.

