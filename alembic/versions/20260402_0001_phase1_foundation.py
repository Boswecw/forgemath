"""ForgeMath Phase 1 governance foundation."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260402_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LANE_FAMILIES = ("canonical_numeric", "hybrid_gate", "governance_support")
TRACE_TIERS = ("tier_1_full", "tier_2_standard", "tier_3_reconstruction")
POLICY_KINDS = ("null_policy", "degraded_mode_policy", "general_policy")
SCOPE_CLASSES = ("local", "cloud", "hybrid")
MIGRATION_CLASSES = (
    "bounded_migration",
    "semantic_supersession",
    "audit_only_reclassification",
    "rollback_recovery",
)
MIGRATION_COMPATIBILITY_CLASSES = (
    "hard_compatible",
    "bounded_migration",
    "audit_only",
    "blocked_incompatible",
)
MIGRATION_APPROVAL_STATES = (
    "draft",
    "pending_review",
    "approved",
    "rejected",
)


def _enum_check(column_name: str, values: tuple[str, ...], name: str) -> sa.CheckConstraint:
    joined = ", ".join(f"'{value}'" for value in values)
    return sa.CheckConstraint(f"{column_name} IN ({joined})", name=name)


def _versioned_columns(identity_column: str) -> list[sa.Column]:
    return [
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column(identity_column, sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("effective_from", sa.DateTime(timezone=True), nullable=False),
        sa.Column("superseded_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("superseded_by_id", sa.String(length=36), nullable=True),
        sa.Column("retired_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.UniqueConstraint(identity_column, "version", name=f"uq_{identity_column}_version"),
        sa.CheckConstraint("version > 0", name=f"ck_{identity_column}_version_positive"),
        sa.CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name=f"ck_{identity_column}_supersession_consistency",
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "forgemath_scope_registry",
        *_versioned_columns("scope_id"),
        sa.Column("scope_class", sa.String(length=32), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        _enum_check("scope_class", SCOPE_CLASSES, "ck_forgemath_scope_registry_scope_class"),
    )
    op.create_index(
        "ix_forgemath_scope_registry_scope_id",
        "forgemath_scope_registry",
        ["scope_id"],
    )

    op.create_table(
        "forgemath_lane_specs",
        *_versioned_columns("lane_id"),
        sa.Column("lane_family", sa.String(length=32), nullable=False),
        sa.Column("trace_tier", sa.String(length=32), nullable=False),
        sa.Column("is_admissible", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("payload", sa.JSON(), nullable=False),
        _enum_check("lane_family", LANE_FAMILIES, "ck_forgemath_lane_specs_lane_family"),
        _enum_check("trace_tier", TRACE_TIERS, "ck_forgemath_lane_specs_trace_tier"),
    )
    op.create_index("ix_forgemath_lane_specs_lane_id", "forgemath_lane_specs", ["lane_id"])

    op.create_table(
        "forgemath_variable_registry",
        *_versioned_columns("variable_registry_id"),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_forgemath_variable_registry_identity",
        "forgemath_variable_registry",
        ["variable_registry_id"],
    )

    op.create_table(
        "forgemath_parameter_sets",
        *_versioned_columns("parameter_set_id"),
        sa.Column("lane_id", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_forgemath_parameter_sets_parameter_set_id",
        "forgemath_parameter_sets",
        ["parameter_set_id"],
    )

    op.create_table(
        "forgemath_threshold_sets",
        *_versioned_columns("threshold_set_id"),
        sa.Column("lane_id", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
    )
    op.create_index(
        "ix_forgemath_threshold_sets_threshold_set_id",
        "forgemath_threshold_sets",
        ["threshold_set_id"],
    )

    op.create_table(
        "forgemath_policy_bundles",
        *_versioned_columns("policy_bundle_id"),
        sa.Column("policy_kind", sa.String(length=32), nullable=False),
        sa.Column("lane_id", sa.String(length=255), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        _enum_check("policy_kind", POLICY_KINDS, "ck_forgemath_policy_bundles_policy_kind"),
    )
    op.create_index(
        "ix_forgemath_policy_bundles_policy_bundle_id",
        "forgemath_policy_bundles",
        ["policy_bundle_id"],
    )

    op.create_table(
        "forgemath_runtime_profiles",
        *_versioned_columns("runtime_profile_id"),
        sa.Column("numeric_precision_mode", sa.String(length=64), nullable=False),
        sa.Column("rounding_mode", sa.String(length=64), nullable=False),
        sa.Column("sort_policy_id", sa.String(length=255), nullable=False),
        sa.Column("serialization_policy_id", sa.String(length=255), nullable=False),
        sa.Column("timezone_policy", sa.String(length=64), nullable=False),
        sa.Column("seed_policy", sa.String(length=255), nullable=False),
        sa.Column(
            "non_determinism_allowed_flag",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index(
        "ix_forgemath_runtime_profiles_runtime_profile_id",
        "forgemath_runtime_profiles",
        ["runtime_profile_id"],
    )

    op.create_table(
        "forgemath_migration_packages",
        *_versioned_columns("migration_id"),
        sa.Column("migration_class", sa.String(length=48), nullable=False),
        sa.Column("source_versions", sa.JSON(), nullable=False),
        sa.Column("target_versions", sa.JSON(), nullable=False),
        sa.Column("affected_artifacts", sa.JSON(), nullable=False),
        sa.Column("migration_logic_summary", sa.Text(), nullable=False),
        sa.Column("compatibility_class_after_migration", sa.String(length=48), nullable=False),
        sa.Column("rollback_plan", sa.Text(), nullable=False),
        sa.Column("replay_impact_statement", sa.Text(), nullable=False),
        sa.Column("audit_only_impact_statement", sa.Text(), nullable=False),
        sa.Column("approval_state", sa.String(length=32), nullable=False),
        _enum_check(
            "migration_class",
            MIGRATION_CLASSES,
            "ck_forgemath_migration_packages_migration_class",
        ),
        _enum_check(
            "compatibility_class_after_migration",
            MIGRATION_COMPATIBILITY_CLASSES,
            "ck_forgemath_migration_packages_compatibility_class",
        ),
        _enum_check(
            "approval_state",
            MIGRATION_APPROVAL_STATES,
            "ck_forgemath_migration_packages_approval_state",
        ),
    )
    op.create_index(
        "ix_forgemath_migration_packages_migration_id",
        "forgemath_migration_packages",
        ["migration_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_forgemath_migration_packages_migration_id",
        table_name="forgemath_migration_packages",
    )
    op.drop_table("forgemath_migration_packages")

    op.drop_index(
        "ix_forgemath_runtime_profiles_runtime_profile_id",
        table_name="forgemath_runtime_profiles",
    )
    op.drop_table("forgemath_runtime_profiles")

    op.drop_index(
        "ix_forgemath_policy_bundles_policy_bundle_id",
        table_name="forgemath_policy_bundles",
    )
    op.drop_table("forgemath_policy_bundles")

    op.drop_index(
        "ix_forgemath_threshold_sets_threshold_set_id",
        table_name="forgemath_threshold_sets",
    )
    op.drop_table("forgemath_threshold_sets")

    op.drop_index(
        "ix_forgemath_parameter_sets_parameter_set_id",
        table_name="forgemath_parameter_sets",
    )
    op.drop_table("forgemath_parameter_sets")

    op.drop_index(
        "ix_forgemath_variable_registry_identity",
        table_name="forgemath_variable_registry",
    )
    op.drop_table("forgemath_variable_registry")

    op.drop_index("ix_forgemath_lane_specs_lane_id", table_name="forgemath_lane_specs")
    op.drop_table("forgemath_lane_specs")

    op.drop_index(
        "ix_forgemath_scope_registry_scope_id",
        table_name="forgemath_scope_registry",
    )
    op.drop_table("forgemath_scope_registry")

