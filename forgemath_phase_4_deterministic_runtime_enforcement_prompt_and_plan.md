# ForgeMath Phase 4 — Deterministic Runtime Enforcement Prompt and Plan

**Date:** April 2, 2026  
**Time Zone:** America/New_York

## Intended use

This canvas is the governed implementation package for the next ForgeMath slice after Phase 3.

It is written for VS Code / Codex style implementation work, but it is also valid as a manual implementation plan.

---

# 1. Mission

Implement **ForgeMath Phase 4: deterministic runtime enforcement and canonical execution admission control**.

This slice is about making runtime determinism a real enforced control surface rather than a doctrine-only claim.

The goal is **not** to build the full math engine.
The goal is **not** to build replay workers.
The goal is **not** to build downstream UI surfaces.

The goal is to make canonical execution admission fail closed unless deterministic runtime requirements are satisfied and persisted as inspectable truth.

---

# 2. Repo State Assumption

Use this prompt only if the repo already has:

- Phase 1 governance registries complete
- Phase 2 canonical evaluation persistence complete
- Phase 3 lifecycle governance complete
- initial API, models, schemas, services, and tests already in place for those phases

Do **not** redo Phase 1.
Do **not** redo Phase 2.
Do **not** redo Phase 3.
Do **not** widen scope into later hardening phases.

---

# 3. Why Phase 4 Exists

The repo now has:

- versioned governance registries
- canonical evaluation persistence
- replay / stale / supersession lifecycle governance

But the repo still needs a real runtime control layer that answers:

- was this evaluation admitted under an admissible deterministic runtime profile?
- was non-determinism explicitly blocked?
- are required numeric, sorting, serialization, timezone, and seed policies actually present?
- can downstream systems inspect runtime admission truth instead of guessing?
- can a runtime posture retirement or incompatibility affect evaluation authority honestly?

Without this slice, ForgeMath can claim determinism doctrinally, but it cannot yet enforce deterministic runtime compliance as canonical admission truth.

---

# 4. Phase 4 Outcomes

This slice should produce five concrete outcomes.

## Outcome 1 — Runtime admission truth is real

Canonical evaluations must expose explicit runtime admission posture.

## Outcome 2 — Deterministic profile enforcement is real

A canonical evaluation cannot be admitted if its runtime profile is missing, incomplete, retired, or explicitly non-deterministic.

## Outcome 3 — Determinism evidence is inspectable

The system should expose enough runtime validation truth that downstream services can inspect whether deterministic runtime requirements were actually satisfied.

## Outcome 4 — Lifecycle truth stays coherent

Runtime enforcement must integrate cleanly with replay, stale, and status posture rather than creating conflicting truths.

## Outcome 5 — Downstream truth is safer

Downstream consumers should not guess whether an evaluation was canonically admitted under valid deterministic runtime rules.
They should be able to read governed runtime admission truth from persisted canonical records.

---

# 5. Controlled Vocabulary to Freeze in This Slice

Use these vocabularies exactly unless the repo already locked them differently and that difference is intentional and documented.

## Compatibility resolution states

- `resolved_hard_compatible`
- `resolved_with_bounded_migration`
- `audit_only`
- `blocked_incompatible`

## Replay states

- `replay_safe`
- `replay_safe_with_bounded_migration`
- `audit_readable_only`
- `not_replayable`

## Result statuses

- `computed_strict`
- `computed_degraded`
- `blocked`
- `audit_only`
- `invalid`

## Stale states

- `fresh`
- `stale_upstream_changed`
- `stale_policy_superseded`
- `stale_input_invalidated`
- `stale_semantics_changed`
- `stale_determinism_retired`

## Runtime profile contract fields

The runtime profile object must support at minimum:

- `runtime_profile_id`
- `numeric_precision_mode`
- `rounding_mode`
- `sort_policy_id`
- `serialization_policy_id`
- `timezone_policy`
- `seed_policy`
- `non_determinism_allowed_flag`

## Recommended runtime admission vocabulary

If the repo needs an explicit admission-state enum rather than a boolean, prefer a controlled family such as:

- `admitted_canonical_deterministic`
- `blocked_missing_runtime_profile`
- `blocked_incomplete_runtime_profile`
- `blocked_non_deterministic_profile`
- `blocked_retired_runtime_profile`
- `blocked_runtime_incompatible`

Only add this if it cleanly fits the repo’s existing enum posture.
Do not invent redundant layers unless they improve clarity and auditability.

---

# 6. Core Doctrine for This Slice

Phase 4 must preserve these rules.

1. Runtime determinism must be enforced, not assumed.
2. No canonical evaluation may be admitted when `non_determinism_allowed_flag = true`.
3. Required runtime-policy fields must exist before canonical admission.
4. Runtime admission truth must be explicit, not implied.
5. Runtime enforcement must not silently conflict with lifecycle truth.
6. Historical visibility and lineage posture must remain intact.
7. Downstream read models must not replace canonical runtime admission truth.
8. This slice is about admission control, not full formula execution.

---

# 7. Build Scope

This slice should be implemented only through these layers:

1. Alembic migration(s)
2. SQLAlchemy models
3. Pydantic request / response schemas
4. deterministic runtime validation and admission service logic
5. bounded API routes
6. tests
7. SYSTEM.md update if repo truth changed materially

Do not move beyond those layers.

---

# 8. What This Slice Should Add

## 8.1 Runtime admission truth on evaluations

If not already present, ensure canonical evaluations support at minimum:

- `runtime_profile_id`
- explicit deterministic runtime admission outcome surface
- `runtime_validation_reason_code`
- `runtime_validation_reason_detail`
- `determinism_certificate_ref` or equivalent explicit runtime evidence surface if needed
- `bit_exact_eligible` or equivalent governed posture if the repo needs that distinction

If some of these belong in a separate runtime admission table instead of only on the root evaluation row, that is acceptable **only if** the root evaluation still exposes current effective runtime admission truth cleanly.

## 8.2 Optional runtime admission event/history table

If the repo design benefits from explicit event history, add a table such as:

- `forgemath_runtime_admission_events`

Suggested minimum fields:

- `event_id`
- `lane_evaluation_id`
- `runtime_profile_id`
- `admission_outcome`
- `reason_code`
- `reason_detail`
- `determinism_certificate_ref`
- `created_at`
- `created_by`

This is optional for Phase 4, but recommended if it improves auditability without widening scope too much.

## 8.3 Runtime validation / admission service

Add service logic that can derive or validate:

- whether a runtime profile is present
- whether required runtime fields are complete
- whether the profile is admissible for canonical execution
- whether `non_determinism_allowed_flag` blocks canonical admission
- whether bit-exact eligibility can be truthfully claimed if that distinction exists

The service should not execute the lane math engine.
It should only govern deterministic runtime admission and evidence posture.

## 8.4 Transition and admission safety

Implement fail-closed rules so invalid runtime claims cannot be written as canonical truth.

Examples:

- cannot admit canonical execution if runtime profile is missing
- cannot admit canonical execution if `non_determinism_allowed_flag = true`
- cannot admit canonical execution if required policy fields are absent
- cannot claim bit-exact eligibility if the runtime profile does not support that posture
- cannot silently leave runtime admission ambiguous on a canonical evaluation

## 8.5 Read-safe runtime inspection API

Add bounded route support to:

- inspect runtime admission truth for an evaluation
- inspect runtime profile validation outcome where helpful
- expose deterministic admission posture without widening into UI or projection-heavy work

Keep this slice backend-only.
No UI.

---

# 9. Recommended Implementation Shape

## 9.1 Migration work

Add the schema changes needed for deterministic runtime enforcement.

Possible paths:

### Path A — Minimal root-table expansion

Add runtime admission fields directly to `forgemath_lane_evaluations`.

### Path B — Root-table expansion plus event table

Add current-state runtime admission fields on `forgemath_lane_evaluations` and an append-only runtime admission event table.

Preferred posture:

- keep current effective admission truth easy to read from the root evaluation row
- keep runtime admission decisions auditable

## 9.2 Model layer

Add or update ORM models for:

- runtime admission fields
- optional runtime admission events
- any governed deterministic evidence surface used by this slice

## 9.3 Schema layer

Add explicit DTOs for:

- runtime admission read model
- runtime inspection read model
- any bounded runtime transition or validation request if needed

Do not flatten canonical truth and projection convenience into one vague DTO.

## 9.4 Service layer

Add a dedicated runtime admission service module or equivalent section in the existing service layer.

Responsibilities should include:

- validate runtime profile completeness
- validate deterministic admissibility
- reject non-deterministic canonical admission
- derive runtime reason codes and detail
- preserve fail-closed behavior

## 9.5 Route layer

Add bounded routes such as:

- get evaluation runtime admission truth
- optional runtime validation inspection route if repo style supports it

Route names can follow repo conventions.

## 9.6 Test layer

Add runtime-focused tests for:

- missing runtime profile rejection
- incomplete runtime profile rejection
- non-deterministic profile rejection
- successful deterministic admission
- lifecycle coherence when runtime posture is retired or invalidated
- inspection route coverage

---

# 10. Phase 4 Rules the Code Must Enforce

## Rule 1 — Canonical admission requires runtime profile

A canonical evaluation must not be admitted without a runtime profile.

## Rule 2 — Non-deterministic profiles are disallowed

A canonical evaluation must not be admitted if `non_determinism_allowed_flag = true`.

## Rule 3 — Runtime profile completeness is required

A runtime profile must not be treated as canonically admissible if required policy fields are absent.

## Rule 4 — Runtime admission truth must be explicit

The repo must expose clear runtime admission truth, not force downstream systems to infer it from partial data.

## Rule 5 — Bit-exact posture must be honest

If the repo supports a `bit_exact_eligible` distinction or similar, it must only be set when the runtime contract actually supports that claim.

## Rule 6 — Runtime enforcement must align with lifecycle truth

A retired or invalid runtime posture must not silently leave lifecycle truth unchanged when that would be misleading.

## Rule 7 — Historical visibility remains intact

Runtime admission failures, invalidations, or retirements must preserve lineage and historical truth.

---

# 11. Minimum Acceptance Criteria

This slice counts as successful only if all of the following are true.

1. A canonical evaluation exposes explicit runtime admission truth.
2. Canonical admission fails closed when runtime profile requirements are not satisfied.
3. Non-deterministic profiles cannot be used for canonical admission.
4. Runtime admission truth is persisted and inspectable.
5. Tests cover the main valid and invalid deterministic runtime admission paths.
6. Completion language stays truthful about what Phase 4 does and does not yet implement.

---

# 12. What Is Out of Scope

Do **not** implement these in Phase 4.

- the full math execution engine
- replay workers or queue processors
- stale-state automation engine
- downstream UI or ForgeCommand screens
- projection/read-model expansion beyond what is minimally needed for runtime inspection
- migration, workload, or security hardening beyond the bounded needs of this slice

---

# 13. Recommended File Families to Expect

Depending on repo structure, expect work in files like:

- `alembic/versions/...`
- `app/models/...`
- `app/schemas/...`
- `app/services/...`
- `app/api/...`
- `tests/...`
- `SYSTEM.md`

---

# 14. VS Code / Codex Prompt

```text
You are acting as a senior implementation engineer working inside the ForgeMath repository.

You are continuing an already-started governed implementation.

Phase 1 is complete.
Phase 2 is complete.
Phase 3 is complete.
Do not redo completed work.
Do not widen scope.
Do not redesign the repo.

Your mission is to implement ForgeMath Phase 4: deterministic runtime enforcement and canonical execution admission control.

ROLE
You are a bounded implementation engineer, not a speculative architect.
Your job is to extend the current repo safely and explicitly.

DOCTRINE CONTEXT
This work is governed by the BDS AI implementation doctrine.

You must behave as though these rules are mandatory:
- context is not optional
- implementation must be bounded
- verification is part of execution
- human authority remains final
- completion language must be truthful
- do not imply readiness, safety, or completeness beyond what is actually implemented and verified
- do not invent missing semantics when governing specs already define the allowed vocabulary
- preserve authority boundaries and append-only lineage posture
- runtime determinism must be enforced, not assumed
- canonical execution admission must fail closed when deterministic requirements are not satisfied
- read models are not canonical truth
- historical visibility and lineage posture must remain intact

MISSION CONTEXT
The repo already has the following implemented or established:
- Phase 1 governance registries
- Phase 2 canonical evaluation persistence substrate
- Phase 3 lifecycle governance for replay, stale posture, recomputation posture, and supersession lineage
- initial API, models, schemas, services, and tests for those prior phases

This slice must now implement:
- deterministic runtime profile enforcement
- canonical execution admission validation tied to runtime profiles
- deterministic execution certificate / evidence surface
- runtime-profile validation for canonical evaluation creation
- bounded runtime inspection routes if needed
- tests for valid and invalid deterministic runtime admission

SYSTEM / BOUNDARY CONTEXT
ForgeMath is a backend-only canonical authority service for governed lane math.
It sits upstream of downstream persistence consumers, projection surfaces, and operator views.

That means:
- canonical execution may not be admitted without deterministic runtime compliance
- runtime profile truth must be persisted and inspectable
- downstream systems must not guess whether deterministic requirements were actually satisfied
- canonical evaluation records must reflect runtime-governed admission truth
- this phase is about execution admission control, not the full math engine

This repo is in controlled implementation posture.
It is not a public SaaS surface.
It is an internal governed business system component.

SPECIFICATION CONTEXT
This slice must establish the deterministic runtime control substrate required for canonical execution admission, but it must not yet implement the full lane math engine, replay workers, or downstream UI surfaces.

Use these governed vocabularies exactly.

Compatibility resolution states:
- resolved_hard_compatible
- resolved_with_bounded_migration
- audit_only
- blocked_incompatible

Replay states:
- replay_safe
- replay_safe_with_bounded_migration
- audit_readable_only
- not_replayable

Result statuses:
- computed_strict
- computed_degraded
- blocked
- audit_only
- invalid

Stale states:
- fresh
- stale_upstream_changed
- stale_policy_superseded
- stale_input_invalidated
- stale_semantics_changed
- stale_determinism_retired

The runtime profile object must support at minimum:
- runtime_profile_id
- numeric_precision_mode
- rounding_mode
- sort_policy_id
- serialization_policy_id
- timezone_policy
- seed_policy
- non_determinism_allowed_flag

TASK
Implement this slice only through these layers:
1. Alembic migration(s) if schema additions are needed
2. SQLAlchemy models
3. Pydantic schemas
4. deterministic runtime validation / admission services
5. bounded API routes
6. tests
7. SYSTEM.md update if repo truth changed materially

MINIMUM FIELD / CONTRACT REQUIREMENTS

1. Runtime admission truth on canonical evaluations
Support at minimum:
- runtime_profile_id
- deterministic_admission_state or equivalent explicit admission outcome surface
- runtime_validation_reason_code
- runtime_validation_reason_detail
- determinism_certificate_ref or equivalent explicit runtime evidence surface if needed
- bit_exact_eligible flag or equivalent governed posture if the repo needs that distinction

2. Runtime validation / admission contract
Support at minimum:
- reject canonical admission when runtime profile is missing
- reject canonical admission when non_determinism_allowed_flag is true
- reject canonical admission when required runtime fields are absent
- reject canonical admission when runtime profile is retired, inactive, or incompatible if the repo already models that posture
- preserve fail-closed behavior for invalid runtime-policy claims

3. Optional runtime event / evidence history if needed
If the design benefits from explicit audit history, support at minimum:
- event id
- lane evaluation id or execution admission id
- runtime profile id
- admission outcome
- reason code
- reason detail
- created_at
- created_by

CONSTRAINTS
You must preserve all of these:
- do not implement the full math engine
- do not implement replay workers or queue processors
- do not invent new semantic vocabularies beyond the governed contract
- do not admit canonical execution without deterministic runtime compliance
- do not allow canonical admission when non_determinism_allowed_flag is true
- do not allow unordered accumulation or runtime ambiguity to be treated as acceptable for canonical execution
- do not move into UI work
- preserve append-only lineage posture
- preserve historical visibility for prior evaluations
- fail closed when deterministic runtime truth cannot be validly derived

REQUIRED VALIDATION POSTURE
At minimum, canonical execution admission or canonical evaluation creation must fail closed unless:
- required evaluation or execution context exists
- runtime profile exists
- runtime profile is admissible for canonical execution
- non_determinism_allowed_flag is false
- required numeric / sorting / serialization / timezone / seed policy fields are present
- compatibility and lifecycle posture remain coherent with the runtime admission claim

Also preserve lifecycle rules so stale, blocked, audit-only, or superseded records still maintain governed historical visibility where required.

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
- canonical evaluation admission is explicitly governed by deterministic runtime profile validation
- invalid runtime profiles fail closed
- non-deterministic profiles cannot be used for canonical admission
- runtime admission truth is persisted and inspectable
- tests cover major valid and invalid runtime admission paths
- completion language is truthful about what this slice does and does not yet implement

OUT OF SCOPE
Do not implement these in this session:
- full lane math execution engine
- replay workers
- stale-state automation engine
- full projection/read-model package
- migration/workload/security hardening phases
- downstream UI surfaces

READ THESE FIRST BEFORE CHANGING CODE
1. BDS AI Implementation Context and Execution Protocol
2. SYSTEM.md
3. current Phase 3 repo state / receipt if available
4. ForgeMath top-level overview
5. ForgeMath persistence / compatibility / replay plan
6. ForgeMath lane governance / persistence / replay / runtime contract
7. ForgeMath canonical equation specification
8. ForgeMath enterprise readiness hardening addendum

FINAL REMINDER
This is a bounded build slice.
The goal is not to make ForgeMath done.
The goal is to make ForgeMath Phase 4 real, governed, testable, and safe to review.
```

---

# 15. Manual Build Plan

## Step 1 — inspect current Phase 3 runtime-profile handling

Confirm exactly what the repo already shipped for runtime profiles.

You want to identify:

- whether runtime profile persistence already exists completely
- whether evaluation creation already validates runtime profiles partially
- whether any deterministic evidence fields already exist
- whether runtime-profile retirement or compatibility posture is already modeled

## Step 2 — add migration for runtime admission truth

Create the schema changes for deterministic runtime enforcement.

Keep the schema minimal but complete.

## Step 3 — extend models and schemas

Add current effective runtime admission truth to the root evaluation model.
Add explicit DTOs for runtime reads and runtime validation surfaces.

## Step 4 — build runtime validation / admission service

This is the heart of the phase.

Implement the service logic that derives or validates:

- runtime profile admissibility
- deterministic runtime completeness
- non-determinism rejection
- runtime reason codes and detail
- optional bit-exact eligibility posture

## Step 5 — add bounded routes

Expose runtime admission truth safely through API routes.

## Step 6 — add runtime tests

Prove:

- missing runtime profile is rejected
- incomplete runtime profile is rejected
- non-deterministic runtime profile is rejected
- valid deterministic runtime admission succeeds
- runtime inspection routes return governed truth
- lifecycle posture stays coherent if runtime posture is retired or invalidated

## Step 7 — update SYSTEM.md

If repo truth materially changed, update SYSTEM.md so the repo mirror stays honest.

---

# 16. Suggested Validation Commands

Use repo-native commands if they already differ, but baseline should look like:

```bash
python -m pytest tests -q
```

And if your repo workflow supports it, also run targeted tests for the new runtime module.

Examples:

```bash
python -m pytest tests/test_phase4_runtime_admission.py -q
python -m pytest tests/test_phase4_runtime_profiles.py -q
```

If migration validation is already part of your local process, run that too.

---

# 17. Next Logical Phase After This One

If Phase 4 lands cleanly, the next major slice should be:

**Phase 5 — projection DTOs and read-model surfaces**

That phase should lock:

- summary/detail DTO truth
- replay diagnostic read models
- factor and trace inspection read models
- projection schema version binding
- read-model separation from canonical truth

---

# 18. Final Position

Phase 4 is the slice that turns runtime determinism from a stated principle into a governed admission control surface.

Once this lands, ForgeMath should be able to say:

- which runtime profile governed canonical admission
- whether deterministic requirements were satisfied
- why admission was blocked when it was blocked
- whether bit-exact posture can be truthfully claimed if that distinction exists
- and how runtime truth relates to lifecycle truth

That is the correct next implementation target.

