"""Structured, non-destructive health reporting for ForgeMath.

``python -m app.health_cli`` preserves the lightweight Evaluation Spine CLI
producer probe consumed by Forge_Command. ``--readiness`` adds explicit local
configuration, database, migration, FastAPI, lane-registration, and optional
lineage-configuration checks. Neither mode applies migrations, creates a
database, emits lineage, or mutates canonical truth.
"""
from __future__ import annotations

import importlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any
from urllib.parse import urlparse

from app.config import DATABASE_URL, SERVICE_NAME, SERVICE_VERSION, validate_config


ROLE = "evaluation-spine math authority (CLI producer; FastAPI also available)"
EXPECTED_SUPPORTED_LANES = frozenset(
    {"verification_burden", "recurrence_pressure", "exposure_factor"}
)
NOT_CHECKED = "not_checked"


def _mark_error(checks: dict[str, str], label: str, exc: BaseException) -> None:
    checks[label] = f"error: {type(exc).__name__}"


def _default_checks() -> tuple[dict[str, str], bool]:
    checks = {
        "surface": "evaluation_spine_cli_imports",
        "database_connectivity": NOT_CHECKED,
        "migration_head_alignment": NOT_CHECKED,
        "fastapi_construction": NOT_CHECKED,
        "supported_lane_registration": NOT_CHECKED,
        "lineage_configuration": NOT_CHECKED,
        "lineage_transport": NOT_CHECKED,
    }
    healthy = True
    for label, module in (
        ("evaluation_spine_authority", "app.services.evaluation_spine_authority"),
        ("evaluation_spine_contract", "app.contracts.evaluation_spine"),
    ):
        try:
            importlib.import_module(module)
            checks[label] = "ok"
        except Exception as exc:  # noqa: BLE001
            _mark_error(checks, label, exc)
            healthy = False
    return checks, healthy


def _check_lineage_configuration(checks: dict[str, str]) -> bool:
    base_url = os.getenv("FORGEMATH_LINEAGE_URL", "").strip()
    token = os.getenv("FORGEMATH_LINEAGE_TOKEN", "").strip()
    checks["lineage_transport"] = NOT_CHECKED
    if not base_url:
        if token:
            checks["lineage_configuration"] = "error: token_configured_without_url"
            return False
        checks["lineage_configuration"] = "disabled"
        return True

    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        checks["lineage_configuration"] = "error: invalid_url"
        return False
    try:
        importlib.import_module("app.lineage.emitter")
    except Exception as exc:  # noqa: BLE001
        checks["lineage_configuration"] = f"error: sdk_unavailable ({type(exc).__name__})"
        return False
    checks["lineage_configuration"] = "configured_not_contacted"
    return True


def _sqlite_database_path(database_url: str) -> Path | None:
    from sqlalchemy.engine import make_url

    parsed = make_url(database_url)
    if not parsed.get_backend_name().startswith("sqlite"):
        return None
    database = parsed.database
    if not database or database == ":memory:":
        raise ValueError("readiness will not create or inspect an in-memory database")
    return Path(database).expanduser().resolve()


def _check_database_and_migrations(checks: dict[str, str]) -> bool:
    try:
        database_path = _sqlite_database_path(DATABASE_URL)
        if database_path is not None and not database_path.is_file():
            raise FileNotFoundError("configured SQLite database does not exist")

        from alembic.config import Config
        from alembic.migration import MigrationContext
        from alembic.script import ScriptDirectory
        from sqlalchemy import create_engine, text

        from app.database import _build_engine_kwargs

        probe_engine = create_engine(DATABASE_URL, **_build_engine_kwargs(DATABASE_URL))
        try:
            with probe_engine.connect() as connection:
                connection.execute(text("SELECT 1"))
                checks["database_connectivity"] = "ok"

                repo_root = Path(__file__).resolve().parents[1]
                alembic_config = Config(str(repo_root / "alembic.ini"))
                alembic_config.set_main_option("script_location", str(repo_root / "alembic"))
                expected_heads = tuple(sorted(ScriptDirectory.from_config(alembic_config).get_heads()))
                current_heads = tuple(sorted(MigrationContext.configure(connection).get_current_heads()))
                if current_heads != expected_heads:
                    checks["migration_head_alignment"] = (
                        "error: current=" + (",".join(current_heads) or "none")
                        + " expected=" + (",".join(expected_heads) or "none")
                    )
                    return False
                checks["migration_head_alignment"] = "ok"
        finally:
            probe_engine.dispose()
    except Exception as exc:  # noqa: BLE001
        if checks.get("database_connectivity") != "ok":
            _mark_error(checks, "database_connectivity", exc)
        if checks.get("migration_head_alignment") != "ok":
            checks["migration_head_alignment"] = NOT_CHECKED
        return False
    return True


def _readiness_checks() -> tuple[dict[str, str], bool]:
    checks = {
        "surface": "service_readiness",
        "configuration": NOT_CHECKED,
        "database_connectivity": NOT_CHECKED,
        "migration_head_alignment": NOT_CHECKED,
        "fastapi_construction": NOT_CHECKED,
        "supported_lane_registration": NOT_CHECKED,
        "lineage_configuration": NOT_CHECKED,
        "lineage_transport": NOT_CHECKED,
    }
    healthy = True

    try:
        validate_config()
        checks["configuration"] = "ok"
    except Exception as exc:  # noqa: BLE001
        _mark_error(checks, "configuration", exc)
        healthy = False

    if not _check_database_and_migrations(checks):
        healthy = False

    try:
        from fastapi import FastAPI
        from app.main import app

        if not isinstance(app, FastAPI):
            raise TypeError("app.main.app is not a FastAPI instance")
        checks["fastapi_construction"] = "ok"
    except Exception as exc:  # noqa: BLE001
        _mark_error(checks, "fastapi_construction", exc)
        healthy = False

    try:
        from app.services.execution_service import SUPPORTED_LANES

        if SUPPORTED_LANES != EXPECTED_SUPPORTED_LANES:
            raise ValueError("supported lane registration differs from the governed lane set")
        checks["supported_lane_registration"] = "ok"
    except Exception as exc:  # noqa: BLE001
        _mark_error(checks, "supported_lane_registration", exc)
        healthy = False

    if not _check_lineage_configuration(checks):
        healthy = False
    return checks, healthy


def build_report(*, readiness: bool = False) -> dict[str, Any]:
    checks, healthy = _readiness_checks() if readiness else _default_checks()
    return {
        "service": SERVICE_NAME,
        "status": "ok" if healthy else "degraded",
        "version": SERVICE_VERSION,
        "role": ROLE,
        "checks": checks,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if arguments not in ([], ["--readiness"]):
        print("usage: python -m app.health_cli [--readiness]", file=sys.stderr)
        return 2
    report = build_report(readiness=arguments == ["--readiness"])
    print(json.dumps(report, separators=(",", ":")))
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
