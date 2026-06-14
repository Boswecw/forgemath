"""Opt-in ForgeMath lineage emission: default-off + upstream discovery by calibration_report_id.

Self-contained — no DataForge-Local, no SDK needed for these paths.
"""
from __future__ import annotations

import sys
from pathlib import Path

_FORGEMATH_ROOT = Path(__file__).resolve().parents[2]
if str(_FORGEMATH_ROOT) not in sys.path:
    sys.path.insert(0, str(_FORGEMATH_ROOT))

from app.lineage.spine_emit import (  # noqa: E402
    FORGEMATH_LINEAGE_URL_ENV,
    _discover_eval_cal_record,
    _lane_evaluation_id,
    emit_forgemath_lineage,
)


class _FakeClient:
    def __init__(self, nodes: list[dict]) -> None:
        self._nodes = nodes

    def list_nodes(self, *, node_type: str, limit: int = 50) -> list[dict]:
        assert node_type == "eval_cal_record"
        return self._nodes


def test_discover_eval_cal_record_matches_by_report_id():
    nodes = [
        {"node_id": "node:r:1", "payload": {"record_id": "eval-calibration:other:v1"}},
        {"node_id": "node:r:2", "payload": {"record_id": "eval-calibration:run-x:v1"}},
    ]
    assert _discover_eval_cal_record(_FakeClient(nodes), "eval-calibration:run-x:v1") == "node:r:2"
    assert _discover_eval_cal_record(_FakeClient(nodes), "missing") is None
    assert _discover_eval_cal_record(_FakeClient(nodes), "") is None


def test_lane_evaluation_id_parsed_from_canonical_ref():
    assert _lane_evaluation_id({"canonical_evaluation_ref": "forgemath_lane_evaluation:abc-123:v1"}) == "abc-123"
    # fallback when the ref is absent
    assert _lane_evaluation_id({"output_id": "out-9"}) == "out-9"


def test_emit_is_default_off_when_url_unset(monkeypatch):
    monkeypatch.delenv(FORGEMATH_LINEAGE_URL_ENV, raising=False)
    outcome = emit_forgemath_lineage(
        report_payload={"calibration_report_id": "eval-calibration:run-x:v1"},
        output_payload={"proposal_candidate_allowed": True, "canonical_evaluation_ref": "forgemath_lane_evaluation:x:v1"},
    )
    assert outcome == "lineage_missing"  # no network, no-op
