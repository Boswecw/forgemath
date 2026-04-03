"""ForgeMath Phase 4 deterministic runtime admission."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260402_0004"
down_revision: Union[str, None] = "20260402_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DETERMINISTIC_ADMISSION_STATES = (
    "admitted_canonical_deterministic",
    "blocked_missing_runtime_profile",
    "blocked_incomplete_runtime_profile",
    "blocked_non_deterministic_profile",
    "blocked_retired_runtime_profile",
    "blocked_runtime_incompatible",
)


def _enum_check(column_name: str, values: tuple[str, ...], name: str) -> sa.CheckConstraint:
    joined = ", ".join(f"'{value}'" for value in values)
    return sa.CheckConstraint(f"{column_name} IN ({joined})", name=name)


def upgrade() -> None:
    with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
        batch_op.add_column(
            sa.Column(
                "deterministic_admission_state",
                sa.String(length=48),
                nullable=False,
                server_default="admitted_canonical_deterministic",
            )
        )
        batch_op.add_column(
            sa.Column(
                "runtime_validation_reason_code",
                sa.String(length=255),
                nullable=False,
                server_default="phase4_backfill_runtime_validation",
            )
        )
        batch_op.add_column(sa.Column("runtime_validation_reason_detail", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("determinism_certificate_ref", sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column(
                "bit_exact_eligible",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.create_check_constraint(
            "ck_forgemath_lane_evaluations_deterministic_admission_state",
            "deterministic_admission_state IN ("
            "'admitted_canonical_deterministic', 'blocked_missing_runtime_profile', "
            "'blocked_incomplete_runtime_profile', 'blocked_non_deterministic_profile', "
            "'blocked_retired_runtime_profile', 'blocked_runtime_incompatible'"
            ")",
        )

    with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
        batch_op.alter_column("deterministic_admission_state", server_default=None)
        batch_op.alter_column("runtime_validation_reason_code", server_default=None)
        batch_op.alter_column("bit_exact_eligible", server_default=None)

    op.create_table(
        "forgemath_runtime_admission_events",
        sa.Column("event_id", sa.String(length=36), primary_key=True),
        sa.Column("lane_evaluation_id", sa.String(length=36), nullable=False),
        sa.Column("runtime_profile_id", sa.String(length=255), nullable=False),
        sa.Column("runtime_profile_version", sa.Integer(), nullable=False),
        sa.Column("admission_outcome", sa.String(length=48), nullable=False),
        sa.Column("reason_code", sa.String(length=255), nullable=False),
        sa.Column("reason_detail", sa.Text(), nullable=True),
        sa.Column("determinism_certificate_ref", sa.String(length=255), nullable=True),
        sa.Column("bit_exact_eligible", sa.Boolean(), nullable=False, server_default=sa.false()),
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
            "runtime_profile_version > 0",
            name="ck_fm_runtime_adm_evt_profile_ver_pos",
        ),
        _enum_check(
            "admission_outcome",
            DETERMINISTIC_ADMISSION_STATES,
            "ck_forgemath_runtime_admission_events_admission_outcome",
        ),
    )
    op.create_index(
        "ix_forgemath_runtime_admission_events_lane_evaluation_id",
        "forgemath_runtime_admission_events",
        ["lane_evaluation_id"],
    )
    op.create_index(
        "ix_forgemath_runtime_admission_events_runtime_profile_id",
        "forgemath_runtime_admission_events",
        ["runtime_profile_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_forgemath_runtime_admission_events_runtime_profile_id",
        table_name="forgemath_runtime_admission_events",
    )
    op.drop_index(
        "ix_forgemath_runtime_admission_events_lane_evaluation_id",
        table_name="forgemath_runtime_admission_events",
    )
    op.drop_table("forgemath_runtime_admission_events")

    with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
        batch_op.drop_constraint(
            "ck_forgemath_lane_evaluations_deterministic_admission_state",
            type_="check",
        )
        batch_op.drop_column("bit_exact_eligible")
        batch_op.drop_column("determinism_certificate_ref")
        batch_op.drop_column("runtime_validation_reason_detail")
        batch_op.drop_column("runtime_validation_reason_code")
        batch_op.drop_column("deterministic_admission_state")
