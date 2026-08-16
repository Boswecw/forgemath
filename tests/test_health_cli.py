from __future__ import annotations

import importlib

from app import health_cli


REQUIRED_FIELDS = {"service", "status", "version", "role", "checks", "checked_at"}


def test_default_health_is_healthy_explicit_and_versioned() -> None:
    report = health_cli.build_report()

    assert set(report) == REQUIRED_FIELDS
    assert report["status"] == "ok"
    assert report["version"] == "0.1.0"
    assert report["checks"]["surface"] == "evaluation_spine_cli_imports"
    assert report["checks"]["database_connectivity"] == "not_checked"
    assert report["checks"]["migration_head_alignment"] == "not_checked"
    assert report["checks"]["fastapi_construction"] == "not_checked"
    assert report["checks"]["lineage_transport"] == "not_checked"


def test_default_health_degrades_when_a_core_import_fails(monkeypatch) -> None:
    real_import = importlib.import_module

    def failing_import(module: str):
        if module == "app.contracts.evaluation_spine":
            raise ImportError("contract unavailable")
        return real_import(module)

    monkeypatch.setattr(health_cli.importlib, "import_module", failing_import)
    report = health_cli.build_report()

    assert report["status"] == "degraded"
    assert report["checks"]["evaluation_spine_contract"] == "error: ImportError"


def test_readiness_treats_disabled_optional_lineage_as_healthy(monkeypatch) -> None:
    monkeypatch.delenv("FORGEMATH_LINEAGE_URL", raising=False)
    monkeypatch.delenv("FORGEMATH_LINEAGE_TOKEN", raising=False)
    checks: dict[str, str] = {}

    assert health_cli._check_lineage_configuration(checks) is True
    assert checks == {
        "lineage_transport": "not_checked",
        "lineage_configuration": "disabled",
    }


def test_readiness_degrades_for_lineage_token_without_url(monkeypatch) -> None:
    monkeypatch.delenv("FORGEMATH_LINEAGE_URL", raising=False)
    monkeypatch.setenv("FORGEMATH_LINEAGE_TOKEN", "configured-token")
    checks: dict[str, str] = {}

    assert health_cli._check_lineage_configuration(checks) is False
    assert checks["lineage_configuration"] == "error: token_configured_without_url"
    assert checks["lineage_transport"] == "not_checked"
