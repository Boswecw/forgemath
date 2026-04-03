# VSCode Implementation Prompt and Plan — ForgeMath Initial Build

**Date:** April 2, 2026  
**Time Zone:** America/New_York

---

## Intended Destination

`02-forge-ecosystem/dataforge/` or `98-drafts/` until reviewed, then promote into the correct Forge/DataForge protocol location.

---

## Purpose

This document is the **initial VSCode build prompt and implementation plan** for beginning the first real implementation slice of **ForgeMath** based on the current architecture and hardening documents.

This prompt is designed for use with **VSCode AI coding workflows** as an implementation-driving prompt, not as a theory review.

It assumes the implementation target is the **DataForge repo** first, because ForgeMath’s first operational authority surface is:

- compatibility-bound evaluation governance,
- immutable persistence,
- replay/stale lineage control,
- deterministic runtime enforcement metadata,
- and read models for downstream operator surfaces.

This implementation must align with the following source documents:

- ForgeMath Persistence, Compatibility, and Replay Plan
- ForgeMath Enterprise Readiness Hardening Addendum

---

## What This First Slice Must Do

This first slice is **not** the full math engine.

It is the **governed substrate** required before broader lane formulas are allowed to become canonical.

The first slice should establish:

1. versioned registry truth
2. immutable parameter / threshold / policy storage
3. compatibility tuple resolution structure
4. canonical lane evaluation persistence grain
5. replay and stale-state vocabulary
6. deterministic runtime profile persistence
7. migration / replay queue / incident table foundations
8. initial API contracts and read-model DTOs
9. fail-closed validation gates for canonical writes

---

## VSCode Build Prompt

Use the following prompt in VSCode.

---

You are working inside the **DataForge** repository as a senior implementation engineer.

Your task is to build the **initial governed ForgeMath persistence and control surface**.

This is **not** a speculative redesign.  
This is a bounded implementation slice.

### Mission

Implement the first production-grade ForgeMath substrate that establishes:

- canonical authority boundary support,
- compatibility tuple persistence and resolution support,
- immutable registry objects,
- append-only lane evaluation persistence,
- replay/stale/supersession state support,
- deterministic runtime profile support,
- migration package support,
- replay queue event support,
- incident record support,
- and read-model/API foundations.

### Architectural intent

ForgeMath is the only canonical execution authority for governed lane math once adopted.

DataForge does **not** re-implement formulas.
DataForge persists:

- registry truth,
- input bundle truth,
- evaluation lineage,
- output/factor records,
- trace metadata,
- replay state,
- migration metadata,
- runtime profile metadata,
- and operator-facing read models.

### Hard constraints

1. Do **not** implement the full lane math engine yet.
2. Do **not** invent formula semantics.
3. Do **not** collapse immutable registries into mutable tables.
4. Do **not** allow in-place mutation of parameter/threshold/policy versions after use.
5. Do **not** permit canonical evaluation writes without compatibility and validation surfaces.
6. Do **not** let projection/read-model tables become source-of-truth.
7. Preserve append-only lineage posture for evaluation facts.
8. Use fail-closed behavior whenever registry resolution or compatibility resolution fails.
9. Design for local/cloud scope declaration instead of assuming one universal comparison domain.
10. Keep the design implementation-safe and reviewable.

### Build target for this slice

Create the database, model, schema, API, and service-layer foundations for the following canonical table families:

#### Registry / governance tables
- forgemath_lane_specs
- forgemath_variable_registry
- forgemath_parameter_sets
- forgemath_threshold_sets
- forgemath_policy_bundles
- forgemath_runtime_profiles
- forgemath_scope_registry
- forgemath_migration_packages

#### Input / evaluation / trace tables
- forgemath_input_bundles
- forgemath_lane_evaluations
- forgemath_lane_output_values
- forgemath_lane_factor_values
- forgemath_trace_bundles
- forgemath_trace_events
- forgemath_projection_records
- forgemath_replay_queue_events
- forgemath_incident_records

### Required schema behavior

#### Immutable versioned registries
Implement versioned registry objects with strong uniqueness and immutability posture for:
- lane specs
- variables
- parameter sets
- threshold sets
- policy bundles
- runtime profiles

Where appropriate include:
- stable ids
- version fields
- payload hash
- effective_from
- superseded_at
- superseded_by
- retired_reason
- created_at
- created_by or actor fields if already consistent with repo patterns

#### Lane evaluations
Implement append-only root evaluation facts with support for:
- lane_evaluation_id
- lane_id
- lane_spec_version
- compatibility resolution state
- execution mode
- evaluation result status
- input_bundle_id
- trace_bundle_id
- runtime_profile_id
- raw_output_hash
- replay_state
- stale_state
- superseded_by
- created_at
- scope linkage where appropriate

#### Output/factor grain
Implement child tables for output values and factor values.

Output rows should support posture classes such as:
- raw
- banded
- classified
- gated

Factor rows should support:
- raw_value
- normalized_value
- weighted_value
- omitted_flag
- omission_reason
- provenance_class
- volatility_class

#### Migration packages
Implement migration package persistence with fields for:
- migration id
- migration class
- source versions
- target versions
- affected artifacts/tables
- migration logic summary
- compatibility class after migration
- rollback plan
- replay impact statement
- audit-only impact statement
- approval state

#### Replay queue events
Implement replay queue events with support for:
- replay event id
- triggering reason
- priority class
- budget class
- operator review requirement
- related scope
- related lane or compatibility tuple context
- status
- created_at

#### Incident records
Implement incident persistence with support for:
- incident id
- incident class
- severity
- affected scope
- affected lane or subsystem
- summary
- canonical-truth impact flag
- created_at
- linked review/AAR metadata if repo conventions exist

### Compatibility tuple support

Create a compatibility tuple structure that can be persisted or deterministically reconstructed for each evaluation. It must account for:
- lane_spec_version
- variable_registry_version
- parameter_set_version
- threshold_registry_version
- prior_registry_version if present
- decay_registry_version if present
- null_policy_version
- degraded_mode_policy_version
- trace_schema_version
- projection_schema_version
- submodule_build_version

Also implement compatibility resolution state vocabulary:
- resolved_hard_compatible
- resolved_with_bounded_migration
- audit_only
- blocked_incompatible

### Determinism/runtime profile support

Create a runtime profile model/table that supports:
- runtime_profile_id
- numeric_precision_mode
- rounding_mode
- sort_policy_id
- serialization_policy_id
- timezone_policy
- seed_policy
- non_determinism_allowed_flag

Canonical evaluation records must be able to bind to a runtime profile.

### Initial application layers to build

Build the initial slice through these layers:

1. Alembic migration(s)
2. SQLAlchemy models
3. Pydantic request/response schemas
4. service-layer validation helpers
5. compatibility resolution skeleton service
6. basic write API routes for registry creation and lane evaluation ingestion
7. basic read API routes for evaluation summary/detail surfaces
8. tests for schema invariants, immutability, and fail-closed validation

### Validation posture

Implement fail-closed checks so canonical evaluation creation is blocked when required references are missing or incompatible.

At minimum validate:
- referenced lane spec exists and is active/admissible
- referenced input bundle exists and is frozen
- referenced runtime profile exists
- required compatibility fields are present
- replay state is derivable
- stale state/status vocabulary values are valid
- projection/read-model records cannot masquerade as canonical source truth

### Output format for your work

Work in bounded steps.

For each changed file:
1. state the exact path
2. explain why it exists
3. provide the implementation
4. keep contracts explicit
5. do not leave placeholder TODO architecture where concrete fields can already be defined

### First implementation goal

Complete **Phase 1 and Phase 2 only**:

#### Phase 1
- ForgeMath table and enum foundation
- immutable registry table design
- runtime profile table
- scope registry table
- migration package table

#### Phase 2
- input bundle table
- lane evaluation root table
- output/factor tables
- trace bundle/event tables
- replay queue and incident tables

Do not move to advanced orchestration until the persistence/control surface is stable.

When done, summarize:
- what was created
- what invariants are enforced
- what still remains for Phase 3+
- what tests should be run next

---

## Implementation Plan for You

This is the practical build order to follow after using the prompt.

### Phase A — Lock vocabulary first
Before writing new routes, lock:
- enums
- status vocabularies
- compatibility resolution states
- replay states
- stale states
- migration classes
- incident classes
- priority/budget classes
- scope classes where already clear

**Deliverable:** one shared enum/constants module and one schema registry note in repo docs if needed.

### Phase B — Build Alembic foundation
Create the first migration set for:
- registry tables
- runtime profile table
- scope registry table
- migration package table
- input bundle and evaluation tables
- output/factor/trace tables
- replay queue and incident tables

**Hard rule:** do not bury semantic statuses in ungoverned free text where an enum or controlled vocabulary should exist.

### Phase C — Build ORM and schema layer
Implement:
- SQLAlchemy models
- Pydantic DTOs
- request/response objects

Keep evaluation write DTOs separate from read-model DTOs.

### Phase D — Build validation services
Implement service helpers for:
- registry resolution
- compatibility tuple assembly
- fail-closed canonical write validation
- immutable-used-object protection

### Phase E — Build initial API slice
Initial routes should likely cover:
- create/read lane specs
- create/read parameter sets
- create/read threshold sets
- create/read policy bundles
- create/read runtime profiles
- create/read input bundles
- create lane evaluation
- get lane evaluation summary
- get lane evaluation detail
- get replay diagnostic summary

### Phase F — Build tests before broadening
Minimum tests:
- cannot mutate used parameter set in place
- cannot create canonical evaluation without required binding refs
- cannot create canonical evaluation with blocked compatibility state
- supersession fields preserve lineage rather than overwrite
- replay queue event accepts only governed classes
- incident record persists canonical-truth impact metadata

---

## Recommended First Concrete Build Slice

Tell VSCode to begin with this exact practical order:

1. enum/constants module
2. Alembic migration for registry and evaluation families
3. ORM models
4. Pydantic schemas
5. validation service for canonical evaluation writes
6. route skeletons
7. tests for fail-closed behavior

That gives you a real substrate fast without jumping ahead into higher-level orchestration.

---

## What Must Wait Until the Next Prompt

The following should be deferred until the first persistence slice is stable:

- actual lane formula execution engine
- bounded migration executor logic
- replay worker orchestration
- operator review workflows
- ForgeCommand UI wiring
- backfill pipelines
- dual-control approval flow
- lakehouse split for high-volume trace families
- SLO instrumentation and incident automation

---

## Suggested Next Prompt After This One

After the first persistence/control slice is in place, the next VSCode prompt should target:

**ForgeMath Phase 3 — compatibility resolution service, replay/stale state machine, and canonical evaluation guardrails**

---

## Source Basis

This prompt/plan is grounded in:

- ForgeMath Persistence, Compatibility, and Replay Plan
- ForgeMath Enterprise Readiness Hardening Addendum

