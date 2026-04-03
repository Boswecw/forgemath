# ForgeMath Codex Build Slice Bundle — Phase 2

**Date:** April 2, 2026  
**Time Zone:** America/New_York

---

## Intended Destination

`02-forge-ecosystem/forgemath/` or `98-drafts/` until reviewed and promoted.

---

## Purpose

This document is a **copy/paste-ready Codex prompt bundle** for beginning the next ForgeMath implementation slice in VS Code.

It is designed to satisfy the BDS AI implementation doctrine by explicitly packaging:

- doctrine context
- mission context
- specification context
- ecosystem role/boundary context
- constraints
- output format
- acceptance posture

This prompt is for **Phase 2 only**.

It does **not** authorize a full-system redesign or a jump into the math execution engine.

---

## Codex Master Prompt

You are acting as a **senior implementation engineer** working inside the **ForgeMath** repository.

You are continuing an already-started governed implementation.

Phase 1 is already complete.
Do not redo Phase 1.
Do not widen scope.
Do not redesign the repo.

Your mission is to implement **ForgeMath Phase 2: canonical evaluation persistence and control-surface foundations**.

---

## 1. Doctrine Context

This work is governed by the BDS AI implementation doctrine.

You must behave as though the following rules are mandatory:

- context is not optional
- implementation must be bounded
- verification is part of execution
- human authority remains final
- completion language must be truthful
- do not imply readiness, safety, or completeness beyond what is actually implemented and verified
- do not invent missing semantics when governing specs already define the allowed vocabulary
- preserve authority boundaries and append-only lineage posture

---

## 2. Mission Context

The current bounded mission is:

**Implement Phase 2 of ForgeMath** by adding the canonical persistence/control surfaces required for governed lane evaluation records.

Phase 1 already implemented:
- governance registries
- immutable registry/version rules
- runtime profile persistence
- scope registry
- migration package metadata
- Phase 1 API routes
- Phase 1 tests

Phase 2 must now implement:
- frozen input bundles
- lane evaluation root records
- lane output values
- lane factor values
- trace bundle metadata
- trace event rows
- replay queue events
- incident records
- canonical evaluation validation
- basic write/read API surfaces for these families

---

## 3. Specification Context

The work must follow the existing ForgeMath governing documents.

### The system position is:
ForgeMath is the ecosystem’s **canonical constitutional math and rule authority**, not a helper library and not a dashboard convenience layer.

### The current implementation rule is:
Phase 2 must establish the persistence and control substrate for canonical evaluations, but it must **not** yet implement the full math execution engine.

### Canonical evaluation doctrine includes:
- full compatibility tuple binding
- deterministic runtime profile binding
- frozen input bundle requirement
- append-only evaluation lineage
- explicit result status
- explicit replay state
- explicit stale state
- explicit trace posture
- fail-closed validation for missing or incompatible bindings

### Required governed vocabularies

#### Result status
- `computed_strict`
- `computed_degraded`
- `blocked`
- `audit_only`
- `invalid`

#### Replay state
- `replay_safe`
- `replay_safe_with_bounded_migration`
- `audit_readable_only`
- `not_replayable`

#### Stale state
- `fresh`
- `stale_upstream_changed`
- `stale_policy_superseded`
- `stale_input_invalidated`
- `stale_semantics_changed`
- `stale_determinism_retired`

#### Compatibility resolution state
- `resolved_hard_compatible`
- `resolved_with_bounded_migration`
- `audit_only`
- `blocked_incompatible`

#### Output posture
- `raw`
- `banded`
- `classified`
- `gated`

#### Trace tier
- `tier_1_full`
- `tier_2_standard`
- `tier_3_reconstruction`

### Required canonical table families for this phase

#### Evaluation persistence
- `forgemath_input_bundles`
- `forgemath_lane_evaluations`
- `forgemath_lane_output_values`
- `forgemath_lane_factor_values`
- `forgemath_trace_bundles`
- `forgemath_trace_events`

#### Operational control
- `forgemath_replay_queue_events`
- `forgemath_incident_records`

### Required compatibility tuple surface
Each lane evaluation must bind to a full compatibility tuple or equivalent persisted compatibility payload/hash including:
- `lane_spec_version`
- `variable_registry_version`
- `parameter_set_version`
- `threshold_registry_version`
- `prior_registry_version` where applicable
- `decay_registry_version` where applicable
- `null_policy_version`
- `degraded_mode_policy_version`
- `trace_schema_version`
- `projection_schema_version`
- `submodule_build_version`

A parameter version alone is never enough.

---

## 4. Ecosystem Role and Boundary Context

ForgeMath is a backend-only canonical authority substrate.
It is upstream of downstream consumers and must preserve strong constitutional boundaries.

That means:
- ForgeMath owns governed math/control truth for lane evaluation records
- downstream systems may read or render projections later
- downstream systems must not recompute canonical truth independently
- read models are not source-of-truth records
- Phase 2 must preserve future replay, supersession, and audit posture

This repo is still in controlled implementation posture.
It is not a public SaaS surface.
It is a governed internal business system component.

---

## 5. Exact Task

Implement **Phase 2 only** through the following layers:

1. Alembic migration(s)
2. SQLAlchemy models
3. Pydantic request/response schemas
4. validation service(s) for canonical evaluation writes
5. route skeletons for create/read operations
6. tests for fail-closed behavior and lineage invariants

### Tables to implement

#### `forgemath_input_bundles`
Support at minimum:
- `input_bundle_id`
- scope linkage where appropriate
- provenance class
- collection timestamp
- admissibility notes
- normalization scope
- deterministic input hash
- source artifact refs payload
- inline values payload where needed
- `created_at`
- `created_by`

#### `forgemath_lane_evaluations`
Support at minimum:
- `lane_evaluation_id`
- `lane_id`
- `lane_spec_version`
- `lane_family`
- `execution_mode`
- `result_status`
- `compatibility_resolution_state`
- `runtime_profile_id`
- `input_bundle_id`
- `trace_bundle_id`
- `created_at`
- `replay_state`
- `stale_state`
- `superseded_by_evaluation_id`
- `raw_output_hash`
- `compatibility_tuple_hash` or equivalent persisted compatibility binding
- scope linkage where appropriate

#### `forgemath_lane_output_values`
Support at minimum:
- `lane_evaluation_id`
- `output_field_name`
- `output_posture`
- `numeric_value`
- `text_value`
- `enum_value`
- `value_range_class`
- `is_primary_output`
- `created_at`

#### `forgemath_lane_factor_values`
Support at minimum:
- `lane_evaluation_id`
- `factor_name`
- `raw_value`
- `normalized_value`
- `weighted_value`
- `omitted_flag`
- `omission_reason`
- `provenance_class`
- `volatility_class`
- `created_at`

#### `forgemath_trace_bundles`
Support at minimum:
- `trace_bundle_id`
- `lane_evaluation_id`
- `trace_tier`
- `trace_schema_version`
- `trace_bundle_hash`
- `reconstructable_flag`
- `created_at`

#### `forgemath_trace_events`
Support at minimum:
- `trace_bundle_id`
- `trace_step_order`
- `trace_event_type`
- `trace_payload_ref`
- `trace_summary`
- `created_at`

#### `forgemath_replay_queue_events`
Support at minimum:
- `replay_event_id`
- `triggering_reason`
- `priority_class`
- `budget_class`
- `operator_review_required_flag`
- `status`
- related lane/scope/input/evaluation linkage where appropriate
- `created_at`

#### `forgemath_incident_records`
Support at minimum:
- `incident_id`
- `incident_class`
- `severity`
- affected scope/lane linkage where appropriate
- `summary`
- `canonical_truth_impact_flag`
- related evaluation linkage where appropriate
- `created_at`

---

## 6. Constraints

You must preserve the following constraints:

1. Do not implement the actual lane math engine yet.
2. Do not invent new equation semantics.
3. Do not allow canonical evaluation records without a frozen input bundle.
4. Do not allow canonical evaluation records without compatibility binding.
5. Do not allow canonical evaluation records without runtime profile linkage.
6. Do not flatten hybrid gate lanes into scalar-only assumptions.
7. Do not let read DTOs become canonical source truth.
8. Do not use ungoverned free text where controlled vocabularies are clearly required.
9. Preserve append-only posture and supersession lineage.
10. Fail closed when required bindings are missing, unresolved, or incompatible.
11. Do not move into replay worker orchestration yet.
12. Do not move into projection/read-model expansion yet.
13. Do not move into UI work.

---

## 7. Required Validation Posture

At minimum, canonical evaluation creation must fail closed unless:
- lane spec exists and is active/admissible
- input bundle exists and is frozen
- runtime profile exists and is canonical-safe
- compatibility fields are present
- compatibility resolution state is valid
- replay state is derivable and valid
- stale state is valid
- result status is valid
- trace tier is sufficient for the declared evaluation posture

Also preserve lineage rules so blocked/audit-only/degraded records still maintain governed historical visibility.

---

## 8. Output Format

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

---

## 9. Acceptance Criteria

This implementation counts as a good Phase 2 result only if:
- the new tables exist through Alembic
- ORM models are defined cleanly
- DTOs are separated between write/read roles
- canonical evaluation writes fail closed when bindings are incomplete or invalid
- tests cover the major invalid-write paths
- supersession/lineage posture is preserved
- completion language is truthful about what Phase 2 does and does not yet implement

---

## 10. Explicit Out of Scope

Do not implement these in this session:
- lane math formulas
- compatibility resolution engine beyond bounded validation/persistence support
- replay worker execution
- stale-state automation engine
- full projection DTO suite
- lakehouse storage split
- security role enforcement workflow
- dual-control approval workflow
- ForgeCommand integration
- public application integration

---

## 11. Files Codex Should Read First

Read these first before changing code:

### Doctrine
- `bds_ai_implementation_context_and_execution_protocol.md`

### Repo/system truth
- `SYSTEM.md`

### Current implementation state
- Phase 1 implementation receipt / summary

### Governing ForgeMath specs
- `forge_math_canonical_equation_stack_top_level_overview.md`
- `forge_math_lane_governance_persistence_replay_and_runtime_contract_v_1_initial.md`
- `forge_math_canonical_equation_specification_v_1_initial.md`
- `forgemath_persistence_compatibility_and_replay_plan.md`
- `forgemath_enterprise_readiness_hardening_addendum.md`

### Current mission prompt
- `vscode_forgemath_phase2_implementation_prompt_and_plan`

---

## 12. Recommended Operator Use

Paste this prompt into Codex after opening the ForgeMath repo and making sure the above files are available in context.

If the response starts widening scope, redesigning the repo, or jumping into execution-engine math, stop and restate:

**Phase 2 only. Persistence and control surface only. No execution engine yet.**

---

## Final Prompt Reminder

This is a **bounded build-slice prompt**.
The goal is not to make ForgeMath “done.”
The goal is to make ForgeMath’s **Phase 2 canonical evaluation substrate** real, governed, testable, and safe to review.
