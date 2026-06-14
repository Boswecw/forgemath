"""ForgeMath lineage emitter tests.

Use a recording mock transport rather than spinning up dataforge-Local in-process
because both repos use the same top-level ``app`` package name.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the ForgeMath src tree wins for app.lineage.* imports.
_FORGEMATH_ROOT = Path(__file__).resolve().parents[2]
if str(_FORGEMATH_ROOT) not in sys.path:
    sys.path.insert(0, str(_FORGEMATH_ROOT))

# The lineage emitter binds to the external forge_lineage_sdk (a vendored Forge
# ecosystem package, not published to PyPI). When it is not importable, skip
# this module rather than aborting collection for the entire test suite.
pytest.importorskip("forge_lineage_sdk")

from tests.lineage._lineage_harness import make_recording_client  # noqa: E402

from app.lineage.emitter import ForgeMathLineageEmitter, NullLineageEmitter  # noqa: E402


def _emitter() -> tuple[ForgeMathLineageEmitter, object]:
    client, backend = make_recording_client(
        writer_identity="forgemath", writer_token="local-forgemath"
    )
    return ForgeMathLineageEmitter(client), backend


def test_emit_evaluation_and_output_writes_full_pair():
    emitter, backend = _emitter()
    status = emitter.emit_evaluation_and_output(
        lane_evaluation_id="lane-eval-001",
        lane_id="lane-A",
        evaluated_at="2026-05-04T16:00:00Z",
        node_revision="rev-1",
        output_payload={
            "output_id": "out-001",
            "lane_evaluation_id": "lane-eval-001",
            "payload_hash": "c" * 64,
            "schema_version": "forgemath_output.v1",
            "produced_at": "2026-05-04T16:00:01Z",
            "stale": False,
        },
    )
    assert status.outcome == "lineage_available"
    assert status.evaluation_node_id and status.output_node_id and status.produced_edge_id

    assert len(backend.envelopes) == 1
    env = backend.envelopes[0]
    types_seen = {n["node_type"] for n in env["nodes"]}
    assert types_seen == {"forgemath_evaluation", "forgemath_output"}
    edge_types = {e["edge_type"] for e in env["edges"]}
    assert edge_types == {"produced"}
    assert env["edges"][0]["causality_class"] == "deterministic"


def test_upstream_eval_cal_node_id_emits_a_consumed_edge():
    """Option A: the cross-producer link so a downstream walk reaches forgemath_output."""
    emitter, backend = _emitter()
    status = emitter.emit_evaluation_and_output(
        lane_evaluation_id="lane-eval-xp",
        lane_id="lane-A",
        evaluated_at="2026-05-04T16:00:00Z",
        output_payload={
            "output_id": "out-xp",
            "lane_evaluation_id": "lane-eval-xp",
            "payload_hash": "e" * 64,
            "schema_version": "forgemath_output.v1",
        },
        upstream_eval_cal_node_id="node:eval_cal_record:upstream-1",
    )
    assert status.outcome == "lineage_available"
    env = backend.envelopes[0]
    edge_types = {e["edge_type"] for e in env["edges"]}
    assert edge_types == {"produced", "consumed"}
    consumed = next(e for e in env["edges"] if e["edge_type"] == "consumed")
    assert consumed["source_node_id"] == "node:eval_cal_record:upstream-1"
    assert consumed["target_node_id"] == status.evaluation_node_id
    assert consumed["causality_class"] == "derived"


def test_emit_runtime_admission_links_back_to_evaluation():
    emitter, backend = _emitter()
    s1 = emitter.emit_evaluation_and_output(
        lane_evaluation_id="lane-eval-002",
        lane_id="lane-B",
        evaluated_at="2026-05-04T16:00:00Z",
        output_payload={
            "output_id": "out-002",
            "lane_evaluation_id": "lane-eval-002",
            "payload_hash": "d" * 64,
            "schema_version": "forgemath_output.v1",
        },
    )
    s2 = emitter.emit_runtime_admission(
        evaluation_node_id=s1.evaluation_node_id,
        admission_id="adm-002",
        lane_evaluation_id="lane-eval-002",
        decision="admitted",
        decided_at="2026-05-04T16:01:00Z",
    )
    assert s2.outcome == "lineage_available"
    assert s2.runtime_admission_node_id is not None
    last = backend.envelopes[-1]
    assert last["nodes"][0]["node_type"] == "forgemath_runtime_admission"
    assert last["edges"][0]["edge_type"] == "informed"


def test_emitter_is_non_blocking_when_unreachable():
    from forge_lineage_sdk import LineageClient

    sdk = LineageClient(
        base_url="http://127.0.0.1:1",
        writer_identity="forgemath",
        writer_token="local-forgemath",
    )
    em = ForgeMathLineageEmitter(sdk)
    status = em.emit_evaluation_and_output(
        lane_evaluation_id="x",
        lane_id="x",
        evaluated_at="2026-05-04T00:00:00Z",
        output_payload={
            "output_id": "x",
            "lane_evaluation_id": "x",
            "payload_hash": "0" * 64,
            "schema_version": "forgemath_output.v1",
        },
    )
    assert status.outcome in ("lineage_missing", "lineage_degraded")


def test_null_emitter_is_safe():
    null = NullLineageEmitter()
    assert null.emit_evaluation_and_output(lane_evaluation_id="x").outcome == "lineage_missing"
    assert null.emit_runtime_admission(admission_id="x").outcome == "lineage_missing"
