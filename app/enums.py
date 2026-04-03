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


def enum_values(enum_cls: type[StrEnum]) -> tuple[str, ...]:
    return tuple(member.value for member in enum_cls)
