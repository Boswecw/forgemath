"""ForgeMath Phase 3 lifecycle governance."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260402_0003"
down_revision: Union[str, None] = "20260402_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


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
RECOMPUTATION_ACTIONS = (
    "no_recompute_needed",
    "optional_recompute",
    "mandatory_recompute",
    "preserve_as_audit_only",
)
SUPERSESSION_CLASSES = (
    "input_supersession",
    "parameter_supersession",
    "policy_supersession",
    "semantic_supersession",
    "projection_supersession",
)


def _enum_check(column_name: str, values: tuple[str, ...], name: str) -> sa.CheckConstraint:
    joined = ", ".join(f"'{value}'" for value in values)
    return sa.CheckConstraint(f"{column_name} IN ({joined})", name=name)


def upgrade() -> None:
    with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
        batch_op.add_column(
            sa.Column(
                "recomputation_action",
                sa.String(length=32),
                nullable=False,
                server_default="preserve_as_audit_only",
            )
        )
        batch_op.add_column(sa.Column("supersession_reason", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("supersession_timestamp", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("supersession_class", sa.String(length=32), nullable=True))
        batch_op.add_column(
            sa.Column(
                "lifecycle_reason_code",
                sa.String(length=255),
                nullable=False,
                server_default="phase3_migration_backfill_required",
            )
        )
        batch_op.add_column(sa.Column("lifecycle_reason_detail", sa.Text(), nullable=True))
        batch_op.create_check_constraint(
            "ck_forgemath_lane_evaluations_recomputation_action",
            "recomputation_action IN ("
            "'no_recompute_needed', 'optional_recompute', 'mandatory_recompute', 'preserve_as_audit_only'"
            ")",
        )
        batch_op.create_check_constraint(
            "ck_forgemath_lane_evaluations_supersession_class",
            "supersession_class IS NULL OR supersession_class IN ("
            "'input_supersession', 'parameter_supersession', 'policy_supersession', "
            "'semantic_supersession', 'projection_supersession'"
            ")",
        )

    with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
        batch_op.alter_column("recomputation_action", server_default=None)
        batch_op.alter_column("lifecycle_reason_code", server_default=None)

    op.create_table(
        "forgemath_evaluation_lifecycle_events",
        sa.Column("event_id", sa.String(length=36), primary_key=True),
        sa.Column("lane_evaluation_id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("prior_replay_state", sa.String(length=48), nullable=True),
        sa.Column("new_replay_state", sa.String(length=48), nullable=False),
        sa.Column("prior_stale_state", sa.String(length=48), nullable=True),
        sa.Column("new_stale_state", sa.String(length=48), nullable=False),
        sa.Column("prior_recomputation_action", sa.String(length=32), nullable=True),
        sa.Column("new_recomputation_action", sa.String(length=32), nullable=False),
        sa.Column("reason_code", sa.String(length=255), nullable=False),
        sa.Column("reason_detail", sa.Text(), nullable=True),
        sa.Column("related_evaluation_id", sa.String(length=36), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["lane_evaluation_id"],
            ["forgemath_lane_evaluations.lane_evaluation_id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "event_type <> ''",
            name="ck_forgemath_evaluation_lifecycle_events_event_type_nonblank",
        ),
        _enum_check(
            "prior_replay_state",
            REPLAY_STATES,
            "ck_forgemath_evaluation_lifecycle_events_prior_replay_state",
        ),
        _enum_check(
            "new_replay_state",
            REPLAY_STATES,
            "ck_forgemath_evaluation_lifecycle_events_new_replay_state",
        ),
        _enum_check(
            "prior_stale_state",
            STALE_STATES,
            "ck_forgemath_evaluation_lifecycle_events_prior_stale_state",
        ),
        _enum_check(
            "new_stale_state",
            STALE_STATES,
            "ck_forgemath_evaluation_lifecycle_events_new_stale_state",
        ),
        _enum_check(
            "prior_recomputation_action",
            RECOMPUTATION_ACTIONS,
            "ck_fm_eval_lifecycle_evt_prior_recomp",
        ),
        _enum_check(
            "new_recomputation_action",
            RECOMPUTATION_ACTIONS,
            "ck_fm_eval_lifecycle_evt_new_recomp",
        ),
    )
    op.create_index(
        "ix_forgemath_evaluation_lifecycle_events_lane_evaluation_id",
        "forgemath_evaluation_lifecycle_events",
        ["lane_evaluation_id"],
    )
    op.create_index(
        "ix_forgemath_evaluation_lifecycle_events_related_evaluation_id",
        "forgemath_evaluation_lifecycle_events",
        ["related_evaluation_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_forgemath_evaluation_lifecycle_events_related_evaluation_id",
        table_name="forgemath_evaluation_lifecycle_events",
    )
    op.drop_index(
        "ix_forgemath_evaluation_lifecycle_events_lane_evaluation_id",
        table_name="forgemath_evaluation_lifecycle_events",
    )
    op.drop_table("forgemath_evaluation_lifecycle_events")

    with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
        batch_op.drop_constraint(
            "ck_forgemath_lane_evaluations_supersession_class",
            type_="check",
        )
        batch_op.drop_constraint(
            "ck_forgemath_lane_evaluations_recomputation_action",
            type_="check",
        )
        batch_op.drop_column("lifecycle_reason_detail")
        batch_op.drop_column("lifecycle_reason_code")
        batch_op.drop_column("supersession_class")
        batch_op.drop_column("supersession_timestamp")
        batch_op.drop_column("supersession_reason")
        batch_op.drop_column("recomputation_action")
