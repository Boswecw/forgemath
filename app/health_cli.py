"""ForgeMath ecosystem-health self-check.

ForgeMath is invoked as a CLI producer in the Evaluation Spine flow (and also exposes a FastAPI
surface). This module gives a downstream consumer (ForgeCommand's `/ecosystem-health` topology) a
real, producer-owned health signal instead of a fabricated status.

Run: `python -m app.health_cli`  ->  prints one JSON object; exit 0 = ok, 1 = degraded.

Deliberately checks only the core math-authority modules (no DataForge/SDK dependency): lineage
emission is opt-in and must not make the producer look unhealthy when it is not configured.
"""
from __future__ import annotations

import importlib
import json
import sys
from datetime import datetime, timezone


def main() -> int:
    checks: dict[str, str] = {}
    status = "ok"
    for label, module in (
        ("evaluation_spine_authority", "app.services.evaluation_spine_authority"),
        ("evaluation_spine_contract", "app.contracts.evaluation_spine"),
    ):
        try:
            importlib.import_module(module)
            checks[label] = "ok"
        except Exception as exc:  # noqa: BLE001
            checks[label] = f"error: {type(exc).__name__}"
            status = "degraded"

    try:
        from importlib.metadata import version as _pkg_version

        version = _pkg_version("forgemath")
    except Exception:  # noqa: BLE001
        version = "unknown"

    print(
        json.dumps(
            {
                "service": "ForgeMath",
                "status": status,
                "version": version,
                "role": "evaluation-spine math authority (CLI producer; FastAPI also available)",
                "checks": checks,
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    )
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
