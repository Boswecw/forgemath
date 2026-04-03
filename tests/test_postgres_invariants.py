import os
from pathlib import Path

from alembic import command
from alembic.config import Config
import pytest
from sqlalchemy import create_engine, inspect


REPO_ROOT = Path(__file__).resolve().parents[1]


def _postgres_test_url() -> str:
    url = os.getenv("FORGEMATH_POSTGRES_TEST_URL")
    if not url:
        pytest.skip("FORGEMATH_POSTGRES_TEST_URL is not set; skipping Postgres-backed invariant test.")
    return url


def _alembic_config(postgres_url: str) -> Config:
    config = Config(str(REPO_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(REPO_ROOT / "alembic"))
    config.set_main_option("sqlalchemy.url", postgres_url)
    return config


def test_postgres_schema_uses_canonical_decimal_text_and_unique_artifact_fields():
    postgres_url = _postgres_test_url()
    command.upgrade(_alembic_config(postgres_url), "head")

    engine = create_engine(postgres_url)
    try:
        inspector = inspect(engine)

        output_columns = {column["name"]: column for column in inspector.get_columns("forgemath_lane_output_values")}
        factor_columns = {column["name"]: column for column in inspector.get_columns("forgemath_lane_factor_values")}

        assert "CHAR" in str(output_columns["numeric_value"]["type"]).upper()
        assert "CHAR" in str(factor_columns["raw_value"]["type"]).upper()
        assert "CHAR" in str(factor_columns["normalized_value"]["type"]).upper()
        assert "CHAR" in str(factor_columns["weighted_value"]["type"]).upper()

        output_unique_constraints = {
            constraint["name"] for constraint in inspector.get_unique_constraints("forgemath_lane_output_values")
        }
        factor_unique_constraints = {
            constraint["name"] for constraint in inspector.get_unique_constraints("forgemath_lane_factor_values")
        }
        evaluation_unique_constraints = {
            constraint["name"] for constraint in inspector.get_unique_constraints("forgemath_lane_evaluations")
        }

        migration_columns = {
            column["name"]: column for column in inspector.get_columns("forgemath_migration_packages")
        }

        assert "uq_forgemath_lane_output_values_lane_evaluation_field" in output_unique_constraints
        assert "uq_forgemath_lane_factor_values_lane_evaluation_factor" in factor_unique_constraints
        assert (
            "uq_forgemath_lane_evaluations_active_canonical_execution_key"
            in evaluation_unique_constraints
        )
        assert "determinism_sensitive_artifacts" in migration_columns
    finally:
        engine.dispose()
