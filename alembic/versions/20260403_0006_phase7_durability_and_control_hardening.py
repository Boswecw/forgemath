"""ForgeMath Phase 7 durability and lifecycle-control hardening."""

from hashlib import sha256
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260403_0006"
down_revision: Union[str, None] = "20260402_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _canonical_json(payload) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash_payload(payload) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _active_canonical_execution_key(row) -> str:
    return _hash_payload(
        {
            "lane_id": row["lane_id"],
            "lane_spec_version": row["lane_spec_version"],
            "runtime_profile_id": row["runtime_profile_id"],
            "runtime_profile_version": row["runtime_profile_version"],
            "input_bundle_id": row["input_bundle_id"],
            "compatibility_tuple_hash": row["compatibility_tuple_hash"],
            "scope_id": row["scope_id"],
            "scope_version": row["scope_version"],
        }
    )


def _json_array_server_default(dialect: str):
    if dialect == "postgresql":
        return sa.text("'[]'::json")
    return sa.text("'[]'")


def _backfill_active_canonical_execution_keys() -> None:
    bind = op.get_bind()
    lane_evaluations = sa.table(
        "forgemath_lane_evaluations",
        sa.column("lane_evaluation_id", sa.String(length=36)),
        sa.column("lane_id", sa.String(length=255)),
        sa.column("lane_spec_version", sa.Integer()),
        sa.column("runtime_profile_id", sa.String(length=255)),
        sa.column("runtime_profile_version", sa.Integer()),
        sa.column("input_bundle_id", sa.String(length=36)),
        sa.column("compatibility_tuple_hash", sa.String(length=64)),
        sa.column("scope_id", sa.String(length=255)),
        sa.column("scope_version", sa.Integer()),
        sa.column("execution_mode", sa.String(length=64)),
        sa.column("result_status", sa.String(length=32)),
        sa.column("superseded_by_evaluation_id", sa.String(length=36)),
        sa.column("active_canonical_execution_key", sa.String(length=64)),
    )
    rows = bind.execute(
        sa.select(
            lane_evaluations.c.lane_evaluation_id,
            lane_evaluations.c.lane_id,
            lane_evaluations.c.lane_spec_version,
            lane_evaluations.c.runtime_profile_id,
            lane_evaluations.c.runtime_profile_version,
            lane_evaluations.c.input_bundle_id,
            lane_evaluations.c.compatibility_tuple_hash,
            lane_evaluations.c.scope_id,
            lane_evaluations.c.scope_version,
        ).where(
            lane_evaluations.c.execution_mode == "governed_canonical_execution",
            lane_evaluations.c.result_status.in_(("computed_strict", "computed_degraded")),
            lane_evaluations.c.superseded_by_evaluation_id.is_(None),
        )
    ).mappings()

    seen_keys: dict[str, str] = {}
    for row in rows:
        active_key = _active_canonical_execution_key(row)
        existing_id = seen_keys.get(active_key)
        if existing_id is not None:
            raise RuntimeError(
                "Phase 7 active canonical execution exclusivity backfill found duplicate active "
                f"execution contexts for LaneEvaluation {existing_id} and {row['lane_evaluation_id']}."
            )
        seen_keys[active_key] = row["lane_evaluation_id"]
        bind.execute(
            lane_evaluations.update()
            .where(lane_evaluations.c.lane_evaluation_id == row["lane_evaluation_id"])
            .values(active_canonical_execution_key=active_key)
        )


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.add_column(
            "forgemath_lane_evaluations",
            sa.Column("active_canonical_execution_key", sa.String(length=64), nullable=True),
        )
        op.add_column(
            "forgemath_migration_packages",
            sa.Column(
                "determinism_sensitive_artifacts",
                sa.JSON(),
                nullable=False,
                server_default=_json_array_server_default(dialect),
            ),
        )
    else:
        with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
            batch_op.add_column(
                sa.Column("active_canonical_execution_key", sa.String(length=64), nullable=True)
            )
        with op.batch_alter_table("forgemath_migration_packages") as batch_op:
            batch_op.add_column(
                sa.Column(
                    "determinism_sensitive_artifacts",
                    sa.JSON(),
                    nullable=False,
                    server_default=_json_array_server_default(dialect),
                )
            )

    _backfill_active_canonical_execution_keys()

    if dialect == "postgresql":
        op.create_unique_constraint(
            "uq_forgemath_lane_evaluations_active_canonical_execution_key",
            "forgemath_lane_evaluations",
            ["active_canonical_execution_key"],
        )
        op.alter_column(
            "forgemath_migration_packages",
            "determinism_sensitive_artifacts",
            server_default=None,
        )
        return

    with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
        batch_op.create_unique_constraint(
            "uq_forgemath_lane_evaluations_active_canonical_execution_key",
            ["active_canonical_execution_key"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.drop_constraint(
            "uq_forgemath_lane_evaluations_active_canonical_execution_key",
            "forgemath_lane_evaluations",
            type_="unique",
        )
        op.drop_column("forgemath_migration_packages", "determinism_sensitive_artifacts")
        op.drop_column("forgemath_lane_evaluations", "active_canonical_execution_key")
        return

    with op.batch_alter_table("forgemath_lane_evaluations") as batch_op:
        batch_op.drop_constraint(
            "uq_forgemath_lane_evaluations_active_canonical_execution_key",
            type_="unique",
        )
        batch_op.drop_column("active_canonical_execution_key")

    with op.batch_alter_table("forgemath_migration_packages") as batch_op:
        batch_op.drop_column("determinism_sensitive_artifacts")
