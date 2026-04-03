"""ForgeMath Phase 2 evaluation foundation."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260402_0002"
down_revision: Union[str, None] = "20260402_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LANE_FAMILIES = ("canonical_numeric", "hybrid_gate", "governance_support")
RESULT_STATUSES = ("computed_strict", "computed_degraded", "blocked", "audit_only", "invalid")
REPLAY_STATES = (
    "replay_safe",
    "replay_safe_with_bounded_migration",
    "audit_readable_only",
    "not_replayable",
)
STALE_STATES = (
    "fresh",
    "stale_upstream_changed",
    "stale_policy_superseded",
    "stale_input_invalidated",
    "stale_semantics_changed",
    "stale_determinism_retired",
)
COMPATIBILITY_STATES = (
    "resolved_hard_compatible",
    "resolved_with_bounded_migration",
    "audit_only",
    "blocked_incompatible",
)
OUTPUT_POSTURES = ("raw", "banded", "classified", "gated")
TRACE_TIERS = ("tier_1_full", "tier_2_standard", "tier_3_reconstruction")
PRIORITY_CLASSES = ("immediate_critical", "standard", "background")
BUDGET_CLASSES = (
    "immediate_critical_budget",
    "daily_standard_budget",
    "background_budget",
)
INCIDENT_CLASSES = (
    "compatibility_resolution_failure",
    "registry_integrity_failure",
    "determinism_violation",
    "trace_persistence_failure",
    "projection_drift_failure",
    "replay_queue_saturation",
    "unauthorized_override_attempt",
    "semantic_migration_misclassification",
)


def _enum_check(column_name: str, values: tuple[str, ...], name: str) -> sa.CheckConstraint:
    joined = ", ".join(f"'{value}'" for value in values)
    return sa.CheckConstraint(f"{column_name} IN ({joined})", name=name)


def upgrade() -> None:
    op.create_table(
        "forgemath_input_bundles",
        sa.Column("input_bundle_id", sa.String(length=36), primary_key=True),
        sa.Column("scope_id", sa.String(length=255), nullable=True),
        sa.Column("scope_version", sa.Integer(), nullable=True),
        sa.Column("provenance_class", sa.String(length=255), nullable=False),
        sa.Column("collection_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("admissibility_notes", sa.Text(), nullable=True),
        sa.Column("normalization_scope", sa.String(length=255), nullable=False),
        sa.Column("deterministic_input_hash", sa.String(length=64), nullable=False),
        sa.Column("source_artifact_refs", sa.JSON(), nullable=False),
        sa.Column("inline_values", sa.JSON(), nullable=False),
        sa.Column("frozen_flag", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.UniqueConstraint(
            "deterministic_input_hash",
            name="uq_forgemath_input_bundles_deterministic_input_hash",
        ),
        sa.CheckConstraint(
            "scope_version IS NULL OR scope_version > 0",
            name="ck_forgemath_input_bundles_scope_version_positive",
        ),
    )
    op.create_index(
        "ix_forgemath_input_bundles_scope_id",
        "forgemath_input_bundles",
        ["scope_id"],
    )

    op.create_table(
        "forgemath_lane_evaluations",
        sa.Column("lane_evaluation_id", sa.String(length=36), primary_key=True),
        sa.Column("lane_id", sa.String(length=255), nullable=False),
        sa.Column("lane_spec_version", sa.Integer(), nullable=False),
        sa.Column("lane_family", sa.String(length=32), nullable=False),
        sa.Column("execution_mode", sa.String(length=64), nullable=False),
        sa.Column("result_status", sa.String(length=32), nullable=False),
        sa.Column("compatibility_resolution_state", sa.String(length=48), nullable=False),
        sa.Column("runtime_profile_id", sa.String(length=255), nullable=False),
        sa.Column("runtime_profile_version", sa.Integer(), nullable=False),
        sa.Column("input_bundle_id", sa.String(length=36), nullable=False),
        sa.Column("trace_bundle_id", sa.String(length=36), nullable=False),
        sa.Column("replay_state", sa.String(length=48), nullable=False),
        sa.Column("stale_state", sa.String(length=48), nullable=False),
        sa.Column("superseded_by_evaluation_id", sa.String(length=36), nullable=True),
        sa.Column("raw_output_hash", sa.String(length=64), nullable=True),
        sa.Column("compatibility_tuple_hash", sa.String(length=64), nullable=False),
        sa.Column("compatibility_binding_payload", sa.JSON(), nullable=False),
        sa.Column("scope_id", sa.String(length=255), nullable=True),
        sa.Column("scope_version", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["input_bundle_id"],
            ["forgemath_input_bundles.input_bundle_id"],
            ondelete="RESTRICT",
        ),
        sa.UniqueConstraint("trace_bundle_id", name="uq_forgemath_lane_evaluations_trace_bundle_id"),
        sa.UniqueConstraint(
            "superseded_by_evaluation_id",
            name="uq_forgemath_lane_evaluations_superseded_by_evaluation_id",
        ),
        sa.CheckConstraint(
            "lane_spec_version > 0",
            name="ck_forgemath_lane_evaluations_lane_spec_version_positive",
        ),
        sa.CheckConstraint(
            "runtime_profile_version > 0",
            name="ck_forgemath_lane_evaluations_runtime_profile_version_positive",
        ),
        sa.CheckConstraint(
            "scope_version IS NULL OR scope_version > 0",
            name="ck_forgemath_lane_evaluations_scope_version_positive",
        ),
        _enum_check("lane_family", LANE_FAMILIES, "ck_forgemath_lane_evaluations_lane_family"),
        _enum_check("result_status", RESULT_STATUSES, "ck_forgemath_lane_evaluations_result_status"),
        _enum_check(
            "compatibility_resolution_state",
            COMPATIBILITY_STATES,
            "ck_forgemath_lane_evaluations_compatibility_resolution_state",
        ),
        _enum_check("replay_state", REPLAY_STATES, "ck_forgemath_lane_evaluations_replay_state"),
        _enum_check("stale_state", STALE_STATES, "ck_forgemath_lane_evaluations_stale_state"),
    )
    op.create_index(
        "ix_forgemath_lane_evaluations_lane_id",
        "forgemath_lane_evaluations",
        ["lane_id"],
    )
    op.create_index(
        "ix_forgemath_lane_evaluations_runtime_profile_id",
        "forgemath_lane_evaluations",
        ["runtime_profile_id"],
    )
    op.create_index(
        "ix_forgemath_lane_evaluations_input_bundle_id",
        "forgemath_lane_evaluations",
        ["input_bundle_id"],
    )
    op.create_index(
        "ix_forgemath_lane_evaluations_compatibility_tuple_hash",
        "forgemath_lane_evaluations",
        ["compatibility_tuple_hash"],
    )
    op.create_index(
        "ix_forgemath_lane_evaluations_scope_id",
        "forgemath_lane_evaluations",
        ["scope_id"],
    )

    op.create_table(
        "forgemath_lane_output_values",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("lane_evaluation_id", sa.String(length=36), nullable=False),
        sa.Column("output_field_name", sa.String(length=255), nullable=False),
        sa.Column("output_posture", sa.String(length=32), nullable=False),
        sa.Column("numeric_value", sa.Float(), nullable=True),
        sa.Column("text_value", sa.Text(), nullable=True),
        sa.Column("enum_value", sa.String(length=255), nullable=True),
        sa.Column("value_range_class", sa.String(length=255), nullable=True),
        sa.Column("is_primary_output", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["lane_evaluation_id"],
            ["forgemath_lane_evaluations.lane_evaluation_id"],
            ondelete="CASCADE",
        ),
        _enum_check(
            "output_posture",
            OUTPUT_POSTURES,
            "ck_forgemath_lane_output_values_output_posture",
        ),
    )
    op.create_index(
        "ix_forgemath_lane_output_values_lane_evaluation_id",
        "forgemath_lane_output_values",
        ["lane_evaluation_id"],
    )

    op.create_table(
        "forgemath_lane_factor_values",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("lane_evaluation_id", sa.String(length=36), nullable=False),
        sa.Column("factor_name", sa.String(length=255), nullable=False),
        sa.Column("raw_value", sa.Float(), nullable=True),
        sa.Column("normalized_value", sa.Float(), nullable=True),
        sa.Column("weighted_value", sa.Float(), nullable=True),
        sa.Column("omitted_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("omission_reason", sa.Text(), nullable=True),
        sa.Column("provenance_class", sa.String(length=255), nullable=True),
        sa.Column("volatility_class", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["lane_evaluation_id"],
            ["forgemath_lane_evaluations.lane_evaluation_id"],
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_forgemath_lane_factor_values_lane_evaluation_id",
        "forgemath_lane_factor_values",
        ["lane_evaluation_id"],
    )

    op.create_table(
        "forgemath_trace_bundles",
        sa.Column("trace_bundle_id", sa.String(length=36), primary_key=True),
        sa.Column("lane_evaluation_id", sa.String(length=36), nullable=False),
        sa.Column("trace_tier", sa.String(length=32), nullable=False),
        sa.Column("trace_schema_version", sa.Integer(), nullable=False),
        sa.Column("trace_bundle_hash", sa.String(length=64), nullable=False),
        sa.Column("reconstructable_flag", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["lane_evaluation_id"],
            ["forgemath_lane_evaluations.lane_evaluation_id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("lane_evaluation_id", name="uq_forgemath_trace_bundles_lane_evaluation_id"),
        sa.CheckConstraint(
            "trace_schema_version > 0",
            name="ck_forgemath_trace_bundles_trace_schema_version_positive",
        ),
        _enum_check("trace_tier", TRACE_TIERS, "ck_forgemath_trace_bundles_trace_tier"),
    )
    op.create_index(
        "ix_forgemath_trace_bundles_lane_evaluation_id",
        "forgemath_trace_bundles",
        ["lane_evaluation_id"],
    )

    op.create_table(
        "forgemath_trace_events",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("trace_bundle_id", sa.String(length=36), nullable=False),
        sa.Column("trace_step_order", sa.Integer(), nullable=False),
        sa.Column("trace_event_type", sa.String(length=255), nullable=False),
        sa.Column("trace_payload_ref", sa.String(length=1024), nullable=False),
        sa.Column("trace_summary", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["trace_bundle_id"],
            ["forgemath_trace_bundles.trace_bundle_id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint(
            "trace_bundle_id",
            "trace_step_order",
            name="uq_forgemath_trace_events_trace_bundle_order",
        ),
        sa.CheckConstraint(
            "trace_step_order >= 0",
            name="ck_forgemath_trace_events_trace_step_order_nonnegative",
        ),
    )
    op.create_index(
        "ix_forgemath_trace_events_trace_bundle_id",
        "forgemath_trace_events",
        ["trace_bundle_id"],
    )

    op.create_table(
        "forgemath_replay_queue_events",
        sa.Column("replay_event_id", sa.String(length=36), primary_key=True),
        sa.Column("triggering_reason", sa.Text(), nullable=False),
        sa.Column("priority_class", sa.String(length=32), nullable=False),
        sa.Column("budget_class", sa.String(length=48), nullable=False),
        sa.Column(
            "operator_review_required_flag",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("status", sa.String(length=64), nullable=False),
        sa.Column("related_lane_id", sa.String(length=255), nullable=True),
        sa.Column("related_scope_id", sa.String(length=255), nullable=True),
        sa.Column("related_input_bundle_id", sa.String(length=36), nullable=True),
        sa.Column("related_lane_evaluation_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["related_input_bundle_id"],
            ["forgemath_input_bundles.input_bundle_id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["related_lane_evaluation_id"],
            ["forgemath_lane_evaluations.lane_evaluation_id"],
            ondelete="SET NULL",
        ),
        _enum_check(
            "priority_class",
            PRIORITY_CLASSES,
            "ck_forgemath_replay_queue_events_priority_class",
        ),
        _enum_check(
            "budget_class",
            BUDGET_CLASSES,
            "ck_forgemath_replay_queue_events_budget_class",
        ),
    )
    op.create_index(
        "ix_forgemath_replay_queue_events_related_lane_id",
        "forgemath_replay_queue_events",
        ["related_lane_id"],
    )
    op.create_index(
        "ix_forgemath_replay_queue_events_related_scope_id",
        "forgemath_replay_queue_events",
        ["related_scope_id"],
    )
    op.create_index(
        "ix_forgemath_replay_queue_events_related_input_bundle_id",
        "forgemath_replay_queue_events",
        ["related_input_bundle_id"],
    )
    op.create_index(
        "ix_forgemath_replay_queue_events_related_lane_evaluation_id",
        "forgemath_replay_queue_events",
        ["related_lane_evaluation_id"],
    )

    op.create_table(
        "forgemath_incident_records",
        sa.Column("incident_id", sa.String(length=36), primary_key=True),
        sa.Column("incident_class", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=64), nullable=False),
        sa.Column("affected_scope_id", sa.String(length=255), nullable=True),
        sa.Column("affected_lane_id", sa.String(length=255), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column(
            "canonical_truth_impact_flag",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("related_lane_evaluation_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["related_lane_evaluation_id"],
            ["forgemath_lane_evaluations.lane_evaluation_id"],
            ondelete="SET NULL",
        ),
        _enum_check(
            "incident_class",
            INCIDENT_CLASSES,
            "ck_forgemath_incident_records_incident_class",
        ),
    )
    op.create_index(
        "ix_forgemath_incident_records_affected_scope_id",
        "forgemath_incident_records",
        ["affected_scope_id"],
    )
    op.create_index(
        "ix_forgemath_incident_records_affected_lane_id",
        "forgemath_incident_records",
        ["affected_lane_id"],
    )
    op.create_index(
        "ix_forgemath_incident_records_related_lane_evaluation_id",
        "forgemath_incident_records",
        ["related_lane_evaluation_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_forgemath_incident_records_related_lane_evaluation_id",
        table_name="forgemath_incident_records",
    )
    op.drop_index(
        "ix_forgemath_incident_records_affected_lane_id",
        table_name="forgemath_incident_records",
    )
    op.drop_index(
        "ix_forgemath_incident_records_affected_scope_id",
        table_name="forgemath_incident_records",
    )
    op.drop_table("forgemath_incident_records")

    op.drop_index(
        "ix_forgemath_replay_queue_events_related_lane_evaluation_id",
        table_name="forgemath_replay_queue_events",
    )
    op.drop_index(
        "ix_forgemath_replay_queue_events_related_input_bundle_id",
        table_name="forgemath_replay_queue_events",
    )
    op.drop_index(
        "ix_forgemath_replay_queue_events_related_scope_id",
        table_name="forgemath_replay_queue_events",
    )
    op.drop_index(
        "ix_forgemath_replay_queue_events_related_lane_id",
        table_name="forgemath_replay_queue_events",
    )
    op.drop_table("forgemath_replay_queue_events")

    op.drop_index(
        "ix_forgemath_trace_events_trace_bundle_id",
        table_name="forgemath_trace_events",
    )
    op.drop_table("forgemath_trace_events")

    op.drop_index(
        "ix_forgemath_trace_bundles_lane_evaluation_id",
        table_name="forgemath_trace_bundles",
    )
    op.drop_table("forgemath_trace_bundles")

    op.drop_index(
        "ix_forgemath_lane_factor_values_lane_evaluation_id",
        table_name="forgemath_lane_factor_values",
    )
    op.drop_table("forgemath_lane_factor_values")

    op.drop_index(
        "ix_forgemath_lane_output_values_lane_evaluation_id",
        table_name="forgemath_lane_output_values",
    )
    op.drop_table("forgemath_lane_output_values")

    op.drop_index(
        "ix_forgemath_lane_evaluations_scope_id",
        table_name="forgemath_lane_evaluations",
    )
    op.drop_index(
        "ix_forgemath_lane_evaluations_compatibility_tuple_hash",
        table_name="forgemath_lane_evaluations",
    )
    op.drop_index(
        "ix_forgemath_lane_evaluations_input_bundle_id",
        table_name="forgemath_lane_evaluations",
    )
    op.drop_index(
        "ix_forgemath_lane_evaluations_runtime_profile_id",
        table_name="forgemath_lane_evaluations",
    )
    op.drop_index(
        "ix_forgemath_lane_evaluations_lane_id",
        table_name="forgemath_lane_evaluations",
    )
    op.drop_table("forgemath_lane_evaluations")

    op.drop_index(
        "ix_forgemath_input_bundles_scope_id",
        table_name="forgemath_input_bundles",
    )
    op.drop_table("forgemath_input_bundles")
