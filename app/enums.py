from enum import StrEnum


class LaneFamily(StrEnum):
    CANONICAL_NUMERIC = "canonical_numeric"
    HYBRID_GATE = "hybrid_gate"
    GOVERNANCE_SUPPORT = "governance_support"


class TraceTier(StrEnum):
    TIER_1_FULL = "tier_1_full"
    TIER_2_STANDARD = "tier_2_standard"
    TIER_3_RECONSTRUCTION = "tier_3_reconstruction"


class ResultStatus(StrEnum):
    COMPUTED_STRICT = "computed_strict"
    COMPUTED_DEGRADED = "computed_degraded"
    BLOCKED = "blocked"
    AUDIT_ONLY = "audit_only"
    INVALID = "invalid"


class ReplayState(StrEnum):
    REPLAY_SAFE = "replay_safe"
    REPLAY_SAFE_WITH_BOUNDED_MIGRATION = "replay_safe_with_bounded_migration"
    AUDIT_READABLE_ONLY = "audit_readable_only"
    NOT_REPLAYABLE = "not_replayable"


class StaleState(StrEnum):
    FRESH = "fresh"
    STALE_UPSTREAM_CHANGED = "stale_upstream_changed"
    STALE_POLICY_SUPERSEDED = "stale_policy_superseded"
    STALE_INPUT_INVALIDATED = "stale_input_invalidated"
    STALE_SEMANTICS_CHANGED = "stale_semantics_changed"
    STALE_DETERMINISM_RETIRED = "stale_determinism_retired"


class DeterministicAdmissionState(StrEnum):
    ADMITTED_CANONICAL_DETERMINISTIC = "admitted_canonical_deterministic"
    BLOCKED_MISSING_RUNTIME_PROFILE = "blocked_missing_runtime_profile"
    BLOCKED_INCOMPLETE_RUNTIME_PROFILE = "blocked_incomplete_runtime_profile"
    BLOCKED_NON_DETERMINISTIC_PROFILE = "blocked_non_deterministic_profile"
    BLOCKED_RETIRED_RUNTIME_PROFILE = "blocked_retired_runtime_profile"
    BLOCKED_RUNTIME_INCOMPATIBLE = "blocked_runtime_incompatible"


class RecomputationAction(StrEnum):
    NO_RECOMPUTE_NEEDED = "no_recompute_needed"
    OPTIONAL_RECOMPUTE = "optional_recompute"
    MANDATORY_RECOMPUTE = "mandatory_recompute"
    PRESERVE_AS_AUDIT_ONLY = "preserve_as_audit_only"


class SupersessionClass(StrEnum):
    INPUT_SUPERSESSION = "input_supersession"
    PARAMETER_SUPERSESSION = "parameter_supersession"
    POLICY_SUPERSESSION = "policy_supersession"
    SEMANTIC_SUPERSESSION = "semantic_supersession"
    PROJECTION_SUPERSESSION = "projection_supersession"


class CompatibilityResolutionState(StrEnum):
    RESOLVED_HARD_COMPATIBLE = "resolved_hard_compatible"
    RESOLVED_WITH_BOUNDED_MIGRATION = "resolved_with_bounded_migration"
    AUDIT_ONLY = "audit_only"
    BLOCKED_INCOMPATIBLE = "blocked_incompatible"


class OutputPosture(StrEnum):
    RAW = "raw"
    BANDED = "banded"
    CLASSIFIED = "classified"
    GATED = "gated"


class PolicyBundleKind(StrEnum):
    NULL_POLICY = "null_policy"
    DEGRADED_MODE_POLICY = "degraded_mode_policy"
    GENERAL_POLICY = "general_policy"


class ScopeClass(StrEnum):
    LOCAL = "local"
    CLOUD = "cloud"
    HYBRID = "hybrid"


class MigrationClass(StrEnum):
    BOUNDED_MIGRATION = "bounded_migration"
    SEMANTIC_SUPERSESSION = "semantic_supersession"
    AUDIT_ONLY_RECLASSIFICATION = "audit_only_reclassification"
    ROLLBACK_RECOVERY = "rollback_recovery"
    NUMERIC_SERIALIZATION_MIGRATION = "numeric_serialization_migration"
    ARTIFACT_HASHING_MIGRATION = "artifact_hashing_migration"
    TRACE_HASHING_MIGRATION = "trace_hashing_migration"
    COMPATIBILITY_INTERPRETATION_MIGRATION = "compatibility_interpretation_migration"
    PROJECTION_COMPATIBILITY_MIGRATION = "projection_compatibility_migration"


class MigrationCompatibilityClass(StrEnum):
    HARD_COMPATIBLE = "hard_compatible"
    BOUNDED_MIGRATION = "bounded_migration"
    AUDIT_ONLY = "audit_only"
    BLOCKED_INCOMPATIBLE = "blocked_incompatible"


class MigrationApprovalState(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class DeterminismSensitiveArtifact(StrEnum):
    NUMERIC_SERIALIZATION = "numeric_serialization"
    ARTIFACT_HASHING = "artifact_hashing"
    TRACE_HASHING = "trace_hashing"
    COMPATIBILITY_INTERPRETATION = "compatibility_interpretation"
    PROJECTION_COMPATIBILITY = "projection_compatibility"


class PriorityClass(StrEnum):
    IMMEDIATE_CRITICAL = "immediate_critical"
    STANDARD = "standard"
    BACKGROUND = "background"


class BudgetClass(StrEnum):
    IMMEDIATE_CRITICAL_BUDGET = "immediate_critical_budget"
    DAILY_STANDARD_BUDGET = "daily_standard_budget"
    BACKGROUND_BUDGET = "background_budget"


class IncidentClass(StrEnum):
    COMPATIBILITY_RESOLUTION_FAILURE = "compatibility_resolution_failure"
    REGISTRY_INTEGRITY_FAILURE = "registry_integrity_failure"
    DETERMINISM_VIOLATION = "determinism_violation"
    TRACE_PERSISTENCE_FAILURE = "trace_persistence_failure"
    PROJECTION_DRIFT_FAILURE = "projection_drift_failure"
    REPLAY_QUEUE_SATURATION = "replay_queue_saturation"
    UNAUTHORIZED_OVERRIDE_ATTEMPT = "unauthorized_override_attempt"
    SEMANTIC_MIGRATION_MISCLASSIFICATION = "semantic_migration_misclassification"


class RuntimeRecoveryPosture(StrEnum):
    CANONICAL_RUNTIME_HEALTHY = "canonical_runtime_healthy"
    RETIRED_FOR_CANONICAL_EXECUTION = "retired_for_canonical_execution"
    AUDIT_ONLY_DUE_TO_RUNTIME_PROFILE_RETIREMENT = "audit_only_due_to_runtime_profile_retirement"
    REQUIRES_PROFILE_REBINDING = "requires_profile_rebinding"


class RuntimeRecoveryAction(StrEnum):
    NO_RECOVERY_NEEDED = "no_recovery_needed"
    REQUIRES_PROFILE_REBINDING = "requires_profile_rebinding"
    REQUIRES_RECOMPUTE_UNDER_NEW_RUNTIME_PROFILE = "requires_recompute_under_new_runtime_profile"
    PRESERVE_AS_AUDIT_ONLY = "preserve_as_audit_only"


def enum_values(enum_cls: type[StrEnum]) -> tuple[str, ...]:
    return tuple(member.value for member in enum_cls)
