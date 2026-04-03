# ForgeMath Phase 7 Hardening Prompt and Plan

**Date:** April 3, 2026  
**Time Zone:** America/New_York

## Purpose

This document folds the strongest valid hardening recommendations from the recent outside reviews into the next governed implementation slice for ForgeMath.

It does **not** replace current repo truth.
It carries current repo truth forward and turns the best remaining hardening needs into a bounded Phase 7 implementation plan and execution prompt.

Phase 7 should be treated as a **durability, operability, and control-surface hardening phase**.
It is not the phase for widening ForgeMath into broad orchestration, multi-lane expansion, or background automation at full scale.

---

# 1. Current Repo Position

ForgeMath currently has:

- governed registries
- canonical evaluation persistence
- lifecycle posture
- deterministic runtime admission
- bounded canonical execution for the initial lane wave
- authority-boundary hardening for manual ingest vs canonical execution
- deterministic decimal-string numeric persistence
- stable artifact hashing across equivalent superseding reruns
- projection/read-model surfaces
- strong fail-closed validation posture

The current repo is therefore **not missing core constitutional architecture**.
The next pressure points are:

- stronger durability for active-canonical exclusivity
- clearer migration policy around determinism-sensitive schema changes
- improved operational control surfaces for lifecycle pressure
- stronger future-growth invariant coverage
- better operator recovery posture for runtime-profile problems

That is the Phase 7 mission.

---

# 2. Phase 7 Thesis

Phase 7 exists to harden ForgeMath at the point where service-layer correctness begins to need stronger persistence-level and operator-control reinforcement.

The governing thesis is:

**If ForgeMath is becoming the canonical mathematical authority, then the repo must now strengthen the durability and operational control layers around current-truth exclusivity, determinism-sensitive migrations, lifecycle transition pressure, and operator recovery.**

Phase 7 is therefore about making the current architecture harder to accidentally violate as the repo grows.

---

# 3. What From the Reviews Gets Folded In

## 3.1 Accept now into Phase 7

These should be folded directly into the Phase 7 slice.

### A. Database-enforced exclusivity for active canonical executions
Current service-layer protection is good, but future expansion should not rely only on service logic.

### B. Determinism-sensitive migration and compatibility policy
Any schema or serialization change that can affect canonical numeric strings, raw hashes, factor hashes, trace hashes, or compatibility interpretation needs explicit governance.

### C. Expanded invariant and boundary test coverage for growth
Add tests for:

- future lane-family expansion boundaries
- mixed-version compatibility pressure
- invalid supersession sequences
- determinism-sensitive migration cases
- DB exclusivity behavior where feasible

### D. Operator-visible lifecycle control preparation
Not full background automation yet, but explicit control surfaces and persisted reason vocabularies should be improved where needed so replay/stale pressure can be managed cleanly later.

## 3.2 Accept later, but prepare now

These should influence design but not become the main implementation payload of Phase 7.

### A. Replay workers / stale-state automation engine
Still deferred. Phase 7 may prepare contracts or records, but should not widen into full worker orchestration.

### B. Rich operational counters / metrics / observability stack
Useful, but should remain secondary to hardening truth and constraints first.

### C. Runtime-profile recovery workflows as full operator tooling
Phase 7 should define the persistence and contract posture needed for recovery, but should not turn into a full admin product surface.

---

# 4. Phase 7 Implementation Goals

Phase 7 should implement five tightly bounded goals.

## Goal 1 — Stronger current-truth exclusivity
Add a persistence-level safeguard for the rule that an execution context may not hold more than one active canonical execution unless governed supersession is explicit.

This may be implemented through:

- a partial unique index
- a current-truth marker strategy
- a constrained active-state materialization rule
- or another database-enforced mechanism

The implementation must preserve append-only lineage and must not flatten history.

## Goal 2 — Determinism-sensitive migration governance
Add explicit migration/compatibility rules for changes that affect:

- numeric serialization
- canonical artifact hashing
- trace hashing
- projection interpretation if compatibility-relevant
- deterministic replay comparability

These changes must never be treated as harmless structural edits if they can alter canonical equality or replay meaning.

## Goal 3 — Lifecycle pressure control hardening
Strengthen the persistence and service contract around replay/stale/supersession control so future worker automation has a stronger substrate.

This includes tightening:

- reason vocabularies
- transition guards
- conflict recording
- operator-visible failure semantics

This does **not** mean implementing full replay workers.

## Goal 4 — Runtime-profile recovery posture
Add explicit governed posture for what happens when a runtime profile becomes:

- incomplete
- retired
- invalid for canonical execution
- superseded after use

The goal is not to relax fail-closed behavior.
The goal is to make recovery and supersession pathways more explicit and reviewable.

## Goal 5 — Growth-oriented invariant coverage
Expand the automated tests so that future expansion is more likely to fail closed.

---

# 5. Phase 7 Boundaries

## In scope

Phase 7 may include:

1. Alembic migration(s)
2. SQLAlchemy model updates
3. Pydantic schema updates
4. Service-layer hardening
5. Validation updates
6. Additional invariant helpers
7. Targeted documentation updates
8. Test additions

## Out of scope

Phase 7 must **not** implement:

- broad replay worker infrastructure
- stale-state automation engine
- broad multi-lane orchestration
- hybrid-gate execution expansion
- external observability platform integration
- downstream UI/operator dashboard work
- cloud/service mesh/runtime deployment work
- generalized metrics platform work

---

# 6. Required Doctrine for Phase 7

The following rules remain mandatory:

- append-only lineage must remain intact
- read models must not become source truth
- canonical truth must remain fail-closed
- history must not be rewritten to simulate current truth
- service-level protections may be strengthened by DB constraints, but DB constraints must not break valid lineage/supersession behavior
- determinism-sensitive schema changes must be explicitly governed
- no background automation should be smuggled into this phase under the name of hardening
- completion language must remain truthful

---

# 7. Controlled Vocabulary and Hardening Areas

## 7.1 Current-truth exclusivity language
Use exact posture language around:

- active canonical execution
- explicit supersession
- current-truth exclusivity
- append-only replacement
- conflict rejection

## 7.2 Determinism-sensitive migration classes
Phase 7 should either add or explicitly define a migration policy family for changes such as:

- `numeric_serialization_migration`
- `artifact_hashing_migration`
- `trace_hashing_migration`
- `compatibility_interpretation_migration`
- `projection_compatibility_migration`

If current repo vocabulary should remain narrower, these can be expressed as subclasses or reason codes under the existing migration package doctrine.

## 7.3 Runtime-profile recovery language
Use explicit posture such as:

- `retired_for_canonical_execution`
- `superseded_for_canonical_execution`
- `requires_profile_rebinding`
- `requires_recompute_under_new_runtime_profile`
- `audit_only_due_to_runtime_profile_retirement`

Only adopt terms that fit the existing controlled vocabulary style.

---

# 8. Build Sequence for Phase 7

## Slice 7A — Persistence-level active canonical exclusivity
Implement the database-supported protection for current active canonical execution truth.

Deliverables:

- migration
- model changes if needed
- service updates
- tests
- docs

## Slice 7B — Determinism-sensitive migration doctrine in code
Implement the persistence/service/schema support needed to distinguish migrations that can affect canonical determinism or replay equality.

Deliverables:

- migration package hardening if needed
- schema/service updates
- validation rules
- tests
- docs

## Slice 7C — Lifecycle pressure and recovery hardening
Tighten lifecycle and runtime-profile recovery posture without building full automation.

Deliverables:

- service/schema updates
- conflict/failure reason handling
- tests
- docs

## Slice 7D — Forward-growth invariant coverage
Add the future-growth test layer and any small supporting code required to make those tests meaningful.

Deliverables:

- test files or test expansions
- any minimal support helpers
- docs/test matrix update

---

# 9. Recommended Acceptance Criteria

Phase 7 counts as successful only if:

- the repo enforces active canonical execution exclusivity more strongly than service-only checks
- valid supersession still works without mutating history
- determinism-sensitive migration cases are explicitly governed rather than implied
- runtime-profile failure and recovery posture is clearer and more reviewable
- tests cover invalid exclusivity, invalid supersession, mixed-version pressure, and determinism-sensitive migration behavior
- SYSTEM.md and modular system docs remain aligned with implementation truth
- completion language is truthful about what is still deferred

---

# 10. Phase 7 Prompt

```text
You are acting as a senior implementation engineer working inside the ForgeMath repository.

You are continuing an already-started governed implementation.
Phase 1 through Phase 6 are already complete, including the pre-Phase-7 hardening pass that tightened authority boundaries, optional binding enforcement, computed artifact DTO semantics, supported-lane contract validation, deterministic decimal-string numeric persistence, and stable trace hashing across equivalent superseding reruns.
Do not redo completed work.
Do not widen scope.
Do not redesign the repo.

Your mission is to implement ForgeMath Phase 7: durability and lifecycle-control hardening for growth beyond the bounded Phase 6 lane wave.

ROLE
You are a bounded senior implementation engineer, not a speculative architect.
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
- preserve deterministic canonical truth and replay posture
- do not flatten history to simulate current truth
- do not implement deferred automation under the label of hardening

MISSION CONTEXT
The repo already has the following implemented or established:
- governed registries and immutable versioned control surfaces
- canonical evaluation persistence and lifecycle posture
- deterministic runtime admission persistence and inspection
- projection/read-model surfaces
- bounded canonical execution for the initial Phase 6 lane wave
- pre-Phase-7 hardening for authority boundaries, stricter DTO semantics, stable hashing, and stronger supported-lane validation

This slice must now implement:
- stronger persistence-level protection for active canonical execution exclusivity
- determinism-sensitive migration and compatibility hardening
- lifecycle pressure and runtime-profile recovery hardening without full automation
- expanded invariant coverage for future growth and invalid-state rejection
- aligned documentation updates reflecting Phase 7 truth

SYSTEM / BOUNDARY CONTEXT
ForgeMath is a backend-only canonical authority substrate for governed lane math in the Forge ecosystem.
It is upstream of downstream consumers and read models.

That means:
- canonical truth remains append-only and versioned
- read models are not source truth
- manual ingest may not mint computed canonical truth
- canonical execution authority remains bounded and fail-closed
- stronger durability is allowed, but not at the cost of lineage visibility
- the repo is an internal governed business system component, not a public SaaS surface

This repo is in controlled implementation posture.
It is an internal single-operator governed system.

SPECIFICATION CONTEXT
This slice must establish the next durability and lifecycle-control hardening layer, but it must not implement replay workers, stale-state automation engines, broad orchestration, or downstream UI/operator product surfaces.

The governing doctrine or specification requires:
- active canonical execution truth must not be silently duplicated
- explicit supersession must remain append-only and reviewable
- determinism-sensitive schema or serialization changes must be explicitly governed
- runtime-profile failure posture must remain fail-closed
- recovery and rebinding posture must become clearer without weakening canonical admission rules

Use these governed vocabularies exactly where already established and extend only where required by existing repo patterns.

Minimum hardening areas for this slice:
1. current-truth exclusivity
2. determinism-sensitive migration posture
3. lifecycle conflict and pressure posture
4. runtime-profile recovery posture
5. forward-growth invariant coverage

TASK
Implement this slice only through these layers:
1. Alembic migration(s)
2. SQLAlchemy models
3. Pydantic schemas
4. service-layer hardening
5. validation rules
6. targeted system documentation updates
7. tests

MINIMUM FIELD / CONTRACT / STRUCTURE REQUIREMENTS

1. Active canonical execution exclusivity
Support at minimum:
- a persistence-level exclusivity mechanism or equivalent enforced current-truth safeguard
- compatibility with explicit supersession behavior
- no mutation of historical rows to fake replacement
- clear rejection semantics for invalid duplicate active execution contexts
- tests proving valid supersession still works

2. Determinism-sensitive migration posture
Support at minimum:
- explicit handling for migrations or migration classes that affect numeric serialization, artifact hashing, trace hashing, or replay comparability
- validation that such changes are not treated as harmless structural migrations when canonical equality or replay meaning changes
- documentation alignment describing the policy
- tests covering at least one invalid and one valid determinism-sensitive migration scenario
- truthful failure posture for incompatible cases

3. Runtime-profile recovery posture
Support at minimum:
- explicit governed handling when runtime profiles are retired, superseded, incomplete, or invalid for canonical use
- preserved fail-closed canonical admission behavior
- clearer reason codes, recovery posture, rebinding posture, or audit posture where appropriate
- no silent downgrade into success
- tests for failure and governed recovery paths where applicable

4. Lifecycle pressure hardening
Support at minimum:
- explicit conflict reasons or improved transition rejection semantics where needed
- preserved lineage visibility
- no invalid stale-state reset or fake freshness restoration
- support that prepares future automation without implementing workers now
- tests for invalid sequences

CONSTRAINTS
You must preserve all of these:
- do not implement replay workers
- do not implement a stale-state automation engine
- do not invent broad orchestration semantics
- do not allow duplicate active canonical execution truth when the execution context should be exclusive
- do not allow history mutation to represent current truth
- preserve append-only lineage and supersession visibility
- fail closed when determinism-sensitive compatibility or migration requirements are not met
- do not move into downstream UI work
- do not move into cloud deployment or observability platform work

REQUIRED VALIDATION POSTURE
At minimum, canonical write or current-truth transition behavior must fail closed unless:
- exclusivity rules are satisfied
- explicit supersession requirements are satisfied
- required compatibility and determinism-sensitive migration posture is satisfied
- runtime-profile posture remains valid for canonical use
- lifecycle transitions remain governed and non-destructive

Also preserve lineage rules so superseded, retired, blocked, degraded, or audit-only records remain historically visible where required.

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
- active canonical execution exclusivity is enforced more strongly than before
- valid supersession still works without breaking append-only truth
- determinism-sensitive migration behavior is explicitly governed
- runtime-profile recovery posture is clearer while canonical admission still fails closed
- tests cover invalid duplicate current-truth cases, invalid supersession sequences, and determinism-sensitive migration pressure
- system documentation is updated to reflect actual Phase 7 truth
- completion language is truthful about what this slice still does not implement

OUT OF SCOPE
Do not implement these in this session:
- replay orchestration workers
- stale-state automation engine
- broad multi-lane expansion
- hybrid gate execution expansion
- external operator UI/dashboard work
- generalized metrics platform integration

READ THESE FIRST BEFORE CHANGING CODE
1. BDS AI Implementation Context and Execution Protocol
2. SYSTEM.md
3. the most recent Phase 6 / pre-Phase-7 implementation receipt
4. ForgeMath top-level overview
5. ForgeMath lane governance, persistence, replay, and runtime contract
6. ForgeMath canonical equation specification
7. ForgeMath enterprise readiness hardening addendum

FINAL REMINDER
This is a bounded hardening slice.
The goal is not to make ForgeMath done.
The goal is to make ForgeMath’s next durability and lifecycle-control layer real, governed, testable, and safe to review.
```

---

# 11. Recommended Immediate Next Move

Run Phase 7 as **one bounded implementation pass** only if the implementer can keep the work centered on:

- active canonical exclusivity
- determinism-sensitive migration posture
- runtime-profile recovery posture
- lifecycle conflict hardening
- invariant expansion

If the implementation starts drifting into worker infrastructure or broad orchestration, split it back down.

---

# 12. Final Position

Phase 7 should not be treated as a redesign phase.
It is a **durability and control-surface reinforcement phase**.

That is the correct place to fold in the strongest valid recommendations from the outside reviews while preserving current ForgeMath truth.

