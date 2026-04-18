# ForgeMath Lane Governance, Persistence, Replay, and Runtime Contract v1 — Initial

**Date:** April 2, 2026  
**Time Zone:** America/New_York

---

## Purpose

This document translates the canonical equation stack into operational governance requirements.

It freezes the lane contract layer that must sit beside the equations themselves so ForgeMath can become an implementation-safe constitutional math surface rather than a mathematically elegant but operationally unstable subsystem.

---

## Governing Thesis

A ForgeMath lane result is only canonical when all of the following are true at the same time:

- the lane spec is active,
- the input variables are semantically known,
- the parameter and threshold bindings are immutable and valid,
- the runtime execution path is deterministic,
- the compatibility tuple resolves,
- the input bundle is frozen and admissible,
- the result status is explicit,
- the replay classification is explicit,
- and the trace posture is sufficient for the lane’s authority class.

If any of those fail, authority must be reduced, blocked, or shifted to audit-only posture.

---

# 1. Lane Result Envelope

Every canonical lane evaluation should emit a root envelope with at least:

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

---

# 2. Compatibility Tuple Contract

Every canonical evaluation must bind to a full compatibility tuple.

## Required tuple fields
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

## Compatibility resolution states
- `resolved_hard_compatible`
- `resolved_with_bounded_migration`
- `audit_only`
- `blocked_incompatible`

## Hard rule
A lane evaluation is never valid because of a parameter version alone.
It is valid only when the full tuple resolves.

---

# 3. Deterministic Runtime Contract

Each lane must execute under an admitted deterministic runtime profile.

## Required runtime profile fields
- `runtime_profile_id`
- `numeric_precision_mode`
- `rounding_mode`
- `sort_policy_id`
- `serialization_policy_id`
- `timezone_policy`
- `seed_policy`
- `non_determinism_allowed_flag`

## Hard rules
- `non_determinism_allowed_flag` must be false for canonical execution.
- No canonical lane may depend on unordered accumulation.
- No canonical lane may use wall-clock values inside canonical math.
- Bit-exact lanes must reproduce byte-identical results for the same frozen bundle and same compatibility tuple.

---

# 4. Input Bundle Contract

Every canonical evaluation must bind to a frozen input bundle.

## Required bundle content
- source artifact refs
- inline values where needed
- provenance class
- collection timestamp
- admissibility notes
- normalization scope
- deterministic input hash

## Hard rule
No canonical evaluation exists without a frozen input bundle or frozen input-bundle reference set.

---

# 5. Immutable Binding Doctrine

The following objects must be immutable once used in any persisted canonical evaluation:

- lane specs
- parameter sets
- threshold sets
- prior sets
- decay sets
- null policy bundles
- degraded mode policy bundles
- determinism runtime profiles

## Required fields for immutable governance objects
- stable id
- version
- payload hash
- effective from
- superseded at
- superseded by
- retired reason

## Hard rule
Changes create new objects.
They do not mutate active historical ones in place.

---

# 6. Result Status Model

Every canonical lane evaluation must emit one result status:

- `computed_strict`
- `computed_degraded`
- `blocked`
- `audit_only`
- `invalid`

## Meaning

### `computed_strict`
Full admissibility and authority requirements satisfied.

### `computed_degraded`
Lane executed, but degraded policy or reduced confidence posture applies.

### `blocked`
Lane did not produce a canonical governed output because hard gate conditions prevented valid execution.

### `audit_only`
Historically inspectable, but not authoritative for current canonical use.

### `invalid`
Output should not be trusted even as an advisory computed result.

---

# 7. Replay Classification Contract

Every evaluation must emit one replay state:

- `replay_safe`
- `replay_safe_with_bounded_migration`
- `audit_readable_only`
- `not_replayable`

## Replay-safe minimum
A result can only be replay-safe when all of the following are present and valid:

- compatibility tuple
- input bundle
- lane spec binding
- parameter binding
- threshold / prior / decay binding as applicable
- output artifact
- trace bundle or reconstructable factor set

## Hard rule
If replay is blocked, the diagnostic reason must be explicit.

---

# 8. Stale and Recomputation Contract

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

## Hard rules
- recomputation creates a new evaluation record
- prior results remain visible in lineage
- semantic changes must not be hidden behind fake equivalence

---

# 9. Supersession Contract

## Supersession classes
- `input_supersession`
- `parameter_supersession`
- `policy_supersession`
- `semantic_supersession`
- `projection_supersession`

## Required supersession fields
- `superseded_by_evaluation_id`
- `supersession_reason`
- `supersession_timestamp`
- `supersession_class`

## Hard rule
Superseded results remain visible.
They do not disappear from history.

---

# 10. Trace Tier Contract

Not every lane needs the same trace depth, but some lanes do.

## Tier 1 — Full trace
Required for:
- strict evaluations
- blocked evaluations
- degraded evaluations
- gate-relevant outputs
- posterior / ambiguity / high-governance lanes

## Tier 2 — Standard trace
Allowed for:
- routine deterministic numeric score lanes
- lower-risk advisory lanes

## Tier 3 — Reconstruction trace
Allowed only when policy explicitly permits it.

## Hard rule
Blocked, degraded, strict, and gate-relevant outputs may not rely on Tier 3 only.

---

# 11. Persistence Families

ForgeMath should persist canonical truth across distinct families.

## Registry and control truth
- `forgemath_lane_specs`
- `forgemath_variable_registry`
- `forgemath_parameter_sets`
- `forgemath_threshold_sets`
- `forgemath_policy_bundles`
- `forgemath_runtime_profiles`
- `forgemath_migration_packages`
- `forgemath_scope_registry`

## Evaluation and fact truth
- `forgemath_input_bundles`
- `forgemath_lane_evaluations`
- `forgemath_lane_output_values`
- `forgemath_lane_factor_values`
- `forgemath_trace_bundles`
- `forgemath_trace_events`
- `forgemath_projection_records`
- `forgemath_replay_queue_events`
- `forgemath_incident_records`

---

# 12. Projection Contract

Projection DTOs are read models only.
They are not canonical truth.

## Required initial projection surfaces
- `LaneEvaluationSummaryModel`
- `LaneEvaluationDetailModel`
- `LaneFactorInspectionModel`
- `LaneTraceInspectionModel`
- `LaneReplayDiagnosticModel`

## Required projection bindings
- `projection_schema_version`
- `source_evaluation_id`
- `source_compatibility_tuple_hash`

## Hard rule
No projection DTO may be written back as canonical source truth.

---

# 13. Lane-Type Requirements

## Numeric lanes
Must define:
- equation
- factor list
- normalization rules
- weighting rules
- threshold mapping
- result-status behavior
- trace tier

## Hybrid gate lanes
Must define:
- hard block conditions
- degraded conditions
- optional numeric posture if used
- replay posture implications
- required trace minimum

## Governance support surfaces
Must define:
- lifecycle state transitions
- authority implications
- projection visibility rules
- audit behavior

---

# 14. Security and Authority Contract

Minimum protected actions should include:

- create new lane spec version
- publish or retire parameter sets
- publish threshold sets
- approve migration package
- initiate mass replay
- perform semantic supersession
- approve status override
- reclassify legacy results as canonical

## Recommended role surfaces
- `forgemath_registry_admin`
- `forgemath_parameter_admin`
- `forgemath_migration_approver`
- `forgemath_replay_operator`
- `forgemath_read_auditor`
- `forgemath_read_standard`
- `forgemath_override_approver`

## Hard rule
No routine application service should have unrestricted authority across registry, migration, replay, and override domains.

---

# 15. Workload and Replay Control

ForgeMath must handle recompute pressure safely.

## Required controls
- replay queue priority classes
- max concurrent recomputes
- replay budget windows
- gate-critical replay reservation capacity
- backpressure signals
- operator-visible replay events for mass cascades

## Suggested replay budgets
- `immediate_critical_budget`
- `daily_standard_budget`
- `background_budget`

## Hard rule
Replay storms must not silently degrade gate-critical freshness.

---

# 16. Data Quality Gates

## Registry DQ gates
- no orphan registry refs
- no duplicate active compatibility tuple for same scope
- no unresolved determinism refs
- no active lane without required compatible policy bundles
- no active parameter set without payload hash

## Evaluation DQ gates
Before canonical write:
- compatibility tuple resolved
- input bundle frozen
- deterministic runtime profile valid
- lane spec active
- required bindings present
- replay state derivable

## Projection DQ gates
Before serving:
- source evaluation visible
- source evaluation not hidden invalidly
- projection schema compatible
- stale / replay posture surfaced correctly

---

# 17. Production Promotion Gates

ForgeMath should not become authoritative until it proves:

## Gate 1 — registry truth gate
Registry versioning, immutable bindings, compatibility resolution, and DQ enforcement work.

## Gate 2 — deterministic execution gate
Repeated execution over frozen inputs is stable and runtime enforcement is real.

## Gate 3 — persistence and replay gate
Append-only write discipline, replay-safe classification, stale transitions, and supersession lineage work.

## Gate 4 — trace and projection gate
Trace tiering and read-model alignment work without flattening truth.

## Gate 5 — migration and rollback gate
Bounded migrations, semantic-break handling, and rollback posture are executable.

## Gate 6 — security and override gate
Protected actions are role-gated and override lineage is immutable.

## Gate 7 — workload and incident gate
Replay storms are controlled and ForgeMath incidents emit governed records.

---

# 18. Immediate Build Sequence

## Phase 1
Freeze lane envelope, result statuses, replay states, and compatibility tuple.

## Phase 2
Create immutable registry objects and root evaluation persistence tables.

## Phase 3
Implement input bundles, factor/output grain, and trace bundle contract.

## Phase 4
Implement stale-state, replay-state, and supersession state machines.

## Phase 5
Implement deterministic runtime profiles and execution checks.

## Phase 6
Implement projection DTOs and replay diagnostics.

## Phase 7
Implement migration, security, workload, and incident hardening.

---

## Final Position

This contract layer is what turns ForgeMath from a strong equation idea into an enterprise-safe mathematical authority.

With this document beside the equation specification, the next work can move directly into:

- schema registry work,
- DataForge DDL,
- DTO design,
- deterministic runtime implementation,
- and slice-by-slice build sequencing.

