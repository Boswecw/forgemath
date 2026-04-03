## 11. Database Schema

Phase 1 ships one initial migration: `20260402_0001_phase1_foundation`.

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
| `forgemath_migration_packages` | Migration metadata | `migration_id`, `version`, source/target versions, approval state | controlled migration and approval vocabulary |

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

