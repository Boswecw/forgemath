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
