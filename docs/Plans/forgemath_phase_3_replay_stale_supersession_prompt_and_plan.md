# ForgeMath Phase 3 — Replay, Stale-State, and Supersession Prompt and Plan

**Date:** April 2, 2026  
**Time Zone:** America/New_York

## Intended use

This canvas is the governed implementation package for the next ForgeMath slice after Phase 2.

It is written for VS Code / Codex style implementation work, but it is also valid as a manual implementation plan.

---

# 1. Mission

Implement **ForgeMath Phase 3: replay-state, stale-state, recomputation posture, and supersession lifecycle control**.

This slice is about turning persisted evaluation truth into governed lifecycle truth.

The goal is **not** to build the math engine.
The goal is **not** to build replay workers.
The goal is **not** to build final downstream UI surfaces.

The goal is to make canonical evaluation records lifecycle-safe, lineage-safe, and audit-safe.

---

# 2. Repo State Assumption

Use this prompt only if the repo already has:

- Phase 1 governance registries complete
- Phase 2 canonical evaluation persistence complete
- initial API, models, schemas, services, and tests already in place for those phases

Do **not** redo Phase 1.
Do **not** redo Phase 2.
Do **not** widen scope into later hardening phases.

---

# 3. Why Phase 3 Exists

Phase 2 gives ForgeMath persisted evaluation facts.

Phase 3 gives ForgeMath the governance layer that answers:

- is this result still fresh?
- can this result still be replayed?
- if not, why not?
- what superseded it?
- what recomputation posture applies?
- what lifecycle truth must downstream consumers see?

Without this slice, ForgeMath can store results but cannot safely govern their continuing authority.

---

# 4. Phase 3 Outcomes

This slice should produce five concrete outcomes.

## Outcome 1 — Replay-state contract is real

Each canonical evaluation must have an explicit replay classification.

## Outcome 2 — Stale-state contract is real

Each canonical evaluation must have an explicit freshness / stale posture.

## Outcome 3 — Supersession lineage is real

A later evaluation may supersede an earlier one without mutating or hiding history.

## Outcome 4 — Recomputation posture is real

The system must be able to say whether recomputation is:

- not needed
- optional
- mandatory
- or impossible except as audit preservation

## Outcome 5 — Downstream truth is safer

Downstream consumers should not need to guess the lifecycle state of an evaluation.
They should be able to read governed lifecycle truth from persisted canonical records.

---

# 5. Controlled Vocabulary to Freeze in This Slice

Use these vocabularies exactly unless the repo already locked them differently and that difference is intentional and documented.

## Replay states

- `replay_safe`
- `replay_safe_with_bounded_migration`
- `audit_readable_only`
- `not_replayable`

## Stale states

- `fresh`
- `stale_upstream_changed`
- `stale_policy_superseded`
- `stale_input_invalidated`
- `stale_semantics_changed`
- `stale_determinism_retired`

## Recomputation actions

- `no_recompute_needed`
- `optional_recompute`
- `mandatory_recompute`
- `preserve_as_audit_only`

## Supersession classes

- `input_supersession`
- `parameter_supersession`
- `policy_supersession`
- `semantic_supersession`
- `projection_supersession`

## Compatibility resolution states

These may already exist from Phase 2, but this slice must use them correctly.

- `resolved_hard_compatible`
- `resolved_with_bounded_migration`
- `audit_only`
- `blocked_incompatible`

---

# 6. Core Doctrine for This Slice

Phase 3 must preserve these rules.

1. Historical canonical records do not mutate in place to reflect a later truth state.
2. Supersession creates lineage, not erasure.
3. Replay posture must be explicit, not inferred ad hoc by downstream consumers.
4. Stale posture must be explicit, not silently hidden.
5. Semantic change must not be disguised as direct equivalence.
6. If replay is blocked, the system must say why.
7. Recomputation decisions must be governable and inspectable.
8. Read-model convenience must not replace canonical lifecycle truth.

---

# 7. Build Scope

This slice should be implemented only through these layers:

1. Alembic migration(s)
2. SQLAlchemy models
3. Pydantic request / response schemas
4. lifecycle validation and derivation service logic
5. bounded API routes
6. tests
7. SYSTEM.md update if repo truth changed materially

Do not move beyond those layers.

---

# 8. What This Slice Should Add

## 8.1 Lifecycle fields on canonical evaluations

If not already present, ensure the root evaluation record supports at minimum:

- `replay_state`
- `stale_state`
- `recomputation_action`
- `superseded_by_evaluation_id`
- `supersession_reason`
- `supersession_timestamp`
- `supersession_class`
- `lifecycle_reason_code` or equivalent explicit reason surface
- `lifecycle_reason_detail` or equivalent diagnostic note surface

If some of these belong in a separate lifecycle event table instead of only on the root row, that is acceptable **only if** the root evaluation still exposes current effective lifecycle truth cleanly.

## 8.2 Optional lifecycle event/history table

If the repo design benefits from explicit event history, add a table such as:

- `forgemath_evaluation_lifecycle_events`

Suggested minimum fields:

- `event_id`
- `lane_evaluation_id`
- `event_type`
- `prior_replay_state`
- `new_replay_state`
- `prior_stale_state`
- `new_stale_state`
- `prior_recomputation_action`
- `new_recomputation_action`
- `reason_code`
- `reason_detail`
- `related_evaluation_id`
- `created_at`
- `created_by`

This is optional for Phase 3, but recommended if it improves auditability without widening scope too much.

## 8.3 Lifecycle derivation service

Add service logic that can derive or validate:

- replay state
- stale state
- recomputation action
- supersession legality

The service should not perform actual replay execution.
It should only govern lifecycle classification and transitions.

## 8.4 Transition safety

Implement transition rules so invalid lifecycle moves fail closed.

Examples:

- cannot mark an evaluation `replay_safe` if required replay bindings are missing
- cannot mark a semantic-break result as directly fresh and equivalent
- cannot supersede an evaluation without required supersession class and timestamp
- cannot hide prior evaluations from lineage
- cannot mark a result `fresh` if the input bundle was invalidated

## 8.5 Read-safe lifecycle API

Add bounded route support to:

- inspect lifecycle truth for an evaluation
- apply governed supersession / stale / replay posture changes where policy allows
- list lineage for a superseded evaluation chain

Keep this slice backend-only.
No UI.

---

# 9. Recommended Implementation Shape

## 9.1 Migration work

Add the schema changes needed for lifecycle governance.

Possible paths:

### Path A — Minimal root-table expansion

Add new lifecycle columns directly to `forgemath_lane_evaluations`.

### Path B — Root-table expansion plus event table

Add current-state columns on `forgemath_lane_evaluations` and an append-only lifecycle event table.

Preferred posture:

- keep current effective state easy to read from the root evaluation row
- keep lifecycle transitions auditable

## 9.2 Model layer

Add or update ORM models for:

- lifecycle state fields
- supersession linkage
- optional lifecycle events

## 9.3 Schema layer

Add explicit DTOs for:

- lifecycle update request
- lifecycle read model
- lineage chain read model
- supersession request

Do not flatten canonical truth and projection convenience into one vague DTO.

## 9.4 Service layer

Add a dedicated lifecycle service module or equivalent section in the existing service layer.

Responsibilities should include:

- derive replay state
- derive stale state
- derive recomputation action
- validate supersession transitions
- preserve fail-closed behavior

## 9.5 Route layer

Add bounded routes such as:

- get evaluation lifecycle
- get evaluation lineage
- apply supersession
- apply stale/replay classification change where operator-governed actions are allowed

Route names can follow repo conventions.

## 9.6 Test layer

Add lifecycle-focused tests for:

- replay-state derivation
- stale-state derivation
- semantic supersession behavior
- lineage visibility
- invalid transition rejection
- fail-closed missing-binding cases

---

# 10. Phase 3 Rules the Code Must Enforce

## Rule 1 — Replay-safe minimum

An evaluation must not be `replay_safe` unless all required replay bindings exist and are valid.

Minimum expected replay requirements:

- compatibility tuple valid enough for replay posture
- frozen input bundle exists
- required lane spec binding exists
- required parameter binding exists
- threshold / policy binding exists as needed
- output artifact exists
- trace bundle or reconstructable factor set exists

## Rule 2 — Replay-blocked diagnostics

If replay is blocked, a reason must be explicit.

Examples:

- missing input bundle
- missing trace bundle
- incompatible semantic migration
- retired runtime profile
- invalidated required source artifact

## Rule 3 — Stale-state truth

An evaluation cannot remain `fresh` when governed invalidation conditions are true.

## Rule 4 — Recomputation truth

Recomputation posture must be derived from lifecycle truth, not set arbitrarily.

## Rule 5 — Semantic break truth

If semantics changed materially, prior evaluations must not be treated as equivalent current truth.
They should become stale and/or audit-only according to the contract.

## Rule 6 — Supersession is additive

Supersession creates new lineage links.
It does not overwrite or delete the prior result.

## Rule 7 — Lineage remains visible

Superseded records remain queryable and inspectable.

---

# 11. Minimum Acceptance Criteria

This slice counts as successful only if all of the following are true.

1. A canonical evaluation can expose explicit replay state, stale state, and recomputation action.
2. Supersession links can be created without mutating prior historical truth.
3. Invalid lifecycle transitions fail closed.
4. Replay-safe claims are blocked when required bindings are missing.
5. Semantic supersession does not fake equivalence.
6. Tests cover the main valid and invalid lifecycle paths.
7. Completion language stays truthful about what Phase 3 does and does not yet implement.

---

# 12. What Is Out of Scope

Do **not** implement these in Phase 3.

- the math execution engine
- actual replay workers or queue processors
- runtime numerical enforcement logic beyond what is needed to classify stale state related to determinism retirement
- downstream UI or ForgeCommand screens
- projection/read-model expansion beyond what is minimally needed for lifecycle inspection
- migration hardening beyond the bounded needs of this slice
- security role system unless a tiny amount is already required by existing route patterns

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
Do not redo completed work.
Do not widen scope.
Do not redesign the repo.

Your mission is to implement ForgeMath Phase 3: replay-state, stale-state, recomputation posture, and supersession lifecycle control.

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
- supersession must preserve historical visibility
- replay posture must be explicit, not guessed by downstream consumers
- stale posture must be explicit, not silently hidden

MISSION CONTEXT
The repo already has the following implemented or established:
- Phase 1 governance registries
- Phase 2 canonical evaluation persistence substrate
- initial API, models, schemas, services, and tests for those prior phases

This slice must now implement:
- replay-state governance
- stale-state governance
- recomputation action governance
- supersession linkage and lineage visibility
- lifecycle validation and bounded lifecycle inspection routes
- tests for valid and invalid lifecycle transitions

SYSTEM / BOUNDARY CONTEXT
ForgeMath is a backend-only canonical authority service for governed lane math.
It sits upstream of downstream persistence consumers, projection surfaces, and operator views.

That means:
- canonical lifecycle truth must be persisted and inspectable
- read models are not canonical truth
- downstream systems must not guess replay or stale posture
- historical truth must remain visible through lineage

This repo is in controlled implementation posture.
It is not a public SaaS surface.
It is an internal governed business system component.

SPECIFICATION CONTEXT
This slice must establish the lifecycle control substrate required for canonical evaluation governance, but it must not yet implement the math engine, replay workers, or UI surfaces.

Use these governed vocabularies exactly.

Replay states:
- replay_safe
- replay_safe_with_bounded_migration
- audit_readable_only
- not_replayable

Stale states:
- fresh
- stale_upstream_changed
- stale_policy_superseded
- stale_input_invalidated
- stale_semantics_changed
- stale_determinism_retired

Recomputation actions:
- no_recompute_needed
- optional_recompute
- mandatory_recompute
- preserve_as_audit_only

Supersession classes:
- input_supersession
- parameter_supersession
- policy_supersession
- semantic_supersession
- projection_supersession

Compatibility resolution states:
- resolved_hard_compatible
- resolved_with_bounded_migration
- audit_only
- blocked_incompatible

TASK
Implement this slice only through these layers:
1. Alembic migration(s)
2. SQLAlchemy models
3. Pydantic schemas
4. lifecycle validation / derivation services
5. bounded API routes
6. tests
7. SYSTEM.md update if repo truth changed materially

MINIMUM FIELD / CONTRACT REQUIREMENTS

1. Lifecycle truth on evaluations
Support at minimum:
- replay_state
- stale_state
- recomputation_action
- superseded_by_evaluation_id
- supersession_reason
- supersession_timestamp
- supersession_class
- explicit lifecycle reason surface

2. Optional lifecycle history table if needed
Support at minimum:
- event id
- lane evaluation id
- event type
- prior and new lifecycle values
- reason code
- reason detail
- related evaluation id
- created_at
- created_by

3. Lifecycle inspection and lineage reads
Support at minimum:
- lifecycle read for one evaluation
- lineage visibility for superseded chains
- fail-closed invalid transition handling

CONSTRAINTS
You must preserve all of these:
- do not implement the math engine
- do not implement replay workers or queue processors
- do not invent new semantic vocabularies beyond the governed contract
- do not allow replay_safe when required bindings are missing
- do not allow fresh when invalidation conditions are present
- do not allow semantic supersession to fake equivalence
- preserve append-only lineage posture
- preserve historical visibility for superseded results
- fail closed when lifecycle truth cannot be validly derived
- do not move into UI work

REQUIRED VALIDATION POSTURE
At minimum, lifecycle state changes and supersession writes must fail closed unless:
- required evaluation exists
- required bindings exist for claimed replay posture
- stale classification matches governed invalidation conditions
- supersession class is valid
- supersession timestamp is present when required
- lineage visibility is preserved

Also preserve lineage rules so superseded, stale, blocked, or audit-only records still maintain governed historical visibility where required.

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
- evaluations expose explicit replay, stale, and recomputation posture
- supersession can be recorded without mutating prior truth
- invalid lifecycle transitions fail closed
- missing replay bindings block replay_safe posture
- tests cover major valid and invalid lifecycle paths
- completion language is truthful about what this slice does and does not yet implement

OUT OF SCOPE
Do not implement these in this session:
- math execution engine
- replay workers
- full projection/read-model package
- migration/workload/security hardening phases
- downstream UI surfaces

READ THESE FIRST BEFORE CHANGING CODE
1. BDS AI Implementation Context and Execution Protocol
2. SYSTEM.md
3. current Phase 2 repo state / receipt if available
4. ForgeMath top-level overview
5. ForgeMath persistence / compatibility / replay plan
6. ForgeMath lane governance / persistence / replay / runtime contract
7. ForgeMath canonical equation specification
8. ForgeMath enterprise readiness hardening addendum

FINAL REMINDER
This is a bounded build slice.
The goal is not to make ForgeMath done.
The goal is to make ForgeMath Phase 3 real, governed, testable, and safe to review.
```

---

# 15. Manual Build Plan

## Step 1 — inspect current Phase 2 schema and models

Confirm exactly what Phase 2 already shipped.

You want to identify:

- whether lifecycle fields already exist partially
- whether an event/history model already exists
- how evaluation IDs and lineage are currently represented
- whether replay-related enums were already frozen

## Step 2 — add migration for lifecycle control

Create the schema changes for replay/stale/supersession posture.

Keep the schema minimal but complete.

## Step 3 — extend models and schemas

Add current effective lifecycle truth to the root evaluation model.
Add explicit DTOs for lifecycle reads and lifecycle mutations.

## Step 4 — build lifecycle derivation service

This is the heart of the phase.

Implement the service logic that derives or validates:

- replay state
- stale state
- recomputation action
- legal supersession linkage

## Step 5 — add bounded routes

Expose lifecycle truth safely through API routes.

## Step 6 — add lifecycle tests

Prove:

- valid transitions work
- invalid transitions fail closed
- prior evaluations remain visible
- replay-safe claims are rejected when requirements are missing
- semantic supersession produces the right governance posture

## Step 7 — update SYSTEM.md

If repo truth materially changed, update SYSTEM.md so the repo mirror stays honest.

---

# 16. Suggested Validation Commands

Use repo-native commands if they already differ, but baseline should look like:

```bash
python -m pytest tests -q
```

And if your repo workflow supports it, also run targeted tests for the new lifecycle module.

Examples:

```bash
python -m pytest tests/test_phase3_lifecycle.py -q
python -m pytest tests/test_phase3_supersession.py -q
```

If migration validation is already part of your local process, run that too.

---

# 17. Next Logical Phase After This One

If Phase 3 lands cleanly, the next major slice should be:

**Phase 4 — deterministic runtime enforcement**

That phase should lock:

- runtime profile truth
- determinism checks
- numeric policy enforcement
- non-determinism rejection for canonical execution

---

# 18. Final Position

Phase 3 is the slice that turns persisted evaluation truth into governed lifecycle truth.

Once this lands, ForgeMath should be able to say:

- what a result is
- whether it is still fresh
- whether it can still be replayed
- whether it was superseded
- what recomputation posture applies
- and why

That is the correct next implementation target.

