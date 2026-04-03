"""ForgeMath authority boundary and canonical numeric hardening."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260402_0005"
down_revision: Union[str, None] = "20260402_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.alter_column(
            "forgemath_lane_output_values",
            "numeric_value",
            existing_type=sa.Float(),
            type_=sa.String(length=128),
            existing_nullable=True,
            postgresql_using="numeric_value::text",
        )
        op.create_unique_constraint(
            "uq_forgemath_lane_output_values_lane_evaluation_field",
            "forgemath_lane_output_values",
            ["lane_evaluation_id", "output_field_name"],
        )

        op.alter_column(
            "forgemath_lane_factor_values",
            "raw_value",
            existing_type=sa.Float(),
            type_=sa.String(length=128),
            existing_nullable=True,
            postgresql_using="raw_value::text",
        )
        op.alter_column(
            "forgemath_lane_factor_values",
            "normalized_value",
            existing_type=sa.Float(),
            type_=sa.String(length=128),
            existing_nullable=True,
            postgresql_using="normalized_value::text",
        )
        op.alter_column(
            "forgemath_lane_factor_values",
            "weighted_value",
            existing_type=sa.Float(),
            type_=sa.String(length=128),
            existing_nullable=True,
            postgresql_using="weighted_value::text",
        )
        op.create_unique_constraint(
            "uq_forgemath_lane_factor_values_lane_evaluation_factor",
            "forgemath_lane_factor_values",
            ["lane_evaluation_id", "factor_name"],
        )
        return

    with op.batch_alter_table("forgemath_lane_output_values", recreate="always") as batch_op:
        batch_op.alter_column(
            "numeric_value",
            existing_type=sa.Float(),
            type_=sa.String(length=128),
            existing_nullable=True,
        )
        batch_op.create_unique_constraint(
            "uq_forgemath_lane_output_values_lane_evaluation_field",
            ["lane_evaluation_id", "output_field_name"],
        )

    with op.batch_alter_table("forgemath_lane_factor_values", recreate="always") as batch_op:
        batch_op.alter_column(
            "raw_value",
            existing_type=sa.Float(),
            type_=sa.String(length=128),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "normalized_value",
            existing_type=sa.Float(),
            type_=sa.String(length=128),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "weighted_value",
            existing_type=sa.Float(),
            type_=sa.String(length=128),
            existing_nullable=True,
        )
        batch_op.create_unique_constraint(
            "uq_forgemath_lane_factor_values_lane_evaluation_factor",
            ["lane_evaluation_id", "factor_name"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    if dialect == "postgresql":
        op.drop_constraint(
            "uq_forgemath_lane_factor_values_lane_evaluation_factor",
            "forgemath_lane_factor_values",
            type_="unique",
        )
        op.alter_column(
            "forgemath_lane_factor_values",
            "weighted_value",
            existing_type=sa.String(length=128),
            type_=sa.Float(),
            existing_nullable=True,
            postgresql_using="NULLIF(weighted_value, '')::double precision",
        )
        op.alter_column(
            "forgemath_lane_factor_values",
            "normalized_value",
            existing_type=sa.String(length=128),
            type_=sa.Float(),
            existing_nullable=True,
            postgresql_using="NULLIF(normalized_value, '')::double precision",
        )
        op.alter_column(
            "forgemath_lane_factor_values",
            "raw_value",
            existing_type=sa.String(length=128),
            type_=sa.Float(),
            existing_nullable=True,
            postgresql_using="NULLIF(raw_value, '')::double precision",
        )

        op.drop_constraint(
            "uq_forgemath_lane_output_values_lane_evaluation_field",
            "forgemath_lane_output_values",
            type_="unique",
        )
        op.alter_column(
            "forgemath_lane_output_values",
            "numeric_value",
            existing_type=sa.String(length=128),
            type_=sa.Float(),
            existing_nullable=True,
            postgresql_using="NULLIF(numeric_value, '')::double precision",
        )
        return

    with op.batch_alter_table("forgemath_lane_factor_values", recreate="always") as batch_op:
        batch_op.drop_constraint(
            "uq_forgemath_lane_factor_values_lane_evaluation_factor",
            type_="unique",
        )
        batch_op.alter_column(
            "raw_value",
            existing_type=sa.String(length=128),
            type_=sa.Float(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "normalized_value",
            existing_type=sa.String(length=128),
            type_=sa.Float(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "weighted_value",
            existing_type=sa.String(length=128),
            type_=sa.Float(),
            existing_nullable=True,
        )

    with op.batch_alter_table("forgemath_lane_output_values", recreate="always") as batch_op:
        batch_op.drop_constraint(
            "uq_forgemath_lane_output_values_lane_evaluation_field",
            type_="unique",
        )
        batch_op.alter_column(
            "numeric_value",
            existing_type=sa.String(length=128),
            type_=sa.Float(),
            existing_nullable=True,
        )
