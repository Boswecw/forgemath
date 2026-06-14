"""Opt-in, non-blocking lineage emission for the Evaluation Spine authority flow.

Lives in the lineage layer (the transport boundary) so the authority service stays focused on
math. When ``FORGEMATH_LINEAGE_URL`` is set, after ForgeMath evaluates an eval_calibration_report
this emits the ``forgemath_evaluation`` + ``forgemath_output`` nodes and — when the upstream
``eval_cal_record`` node can be discovered — the ``consumed`` edge into it, completing the
edge-connected chain forge-eval bundle → eval-cal → forgemath_output that ForgeCommand's gate-walk
traverses. Default-OFF and fail-soft: any failure is logged and the evaluation still completes.

Discovery: ForgeMath holds the calibration report (``calibration_report_id``); eval-cal set its
``eval_cal_record.record_id`` to that same id, so the upstream node is found by matching
``record_id`` over ``list_nodes("eval_cal_record")``. ForgeMath emits only its own lineage (what
it consumed + produced) — no recomputation of upstream authority; the non_recalculation posture in
the output payload is unchanged.
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

FORGEMATH_LINEAGE_URL_ENV = "FORGEMATH_LINEAGE_URL"
FORGEMATH_LINEAGE_TOKEN_ENV = "FORGEMATH_LINEAGE_TOKEN"
EVAL_CAL_RECORD_NODE_TYPE = "eval_cal_record"


def _discover_eval_cal_record(client: Any, calibration_report_id: str) -> str | None:
    """Find the eval_cal_record lineage node whose record_id == the calibration report id."""
    if not calibration_report_id:
        return None
    for node in client.list_nodes(node_type=EVAL_CAL_RECORD_NODE_TYPE, limit=50):
        payload = node.get("payload") or {}
        if str(payload.get("record_id") or "") == calibration_report_id:
            nid = node.get("node_id")
            return str(nid) if nid else None
    return None


def _lane_evaluation_id(output_payload: dict[str, Any]) -> str:
    """A stable id for the forgemath_evaluation node, derived from the canonical evaluation ref
    (``forgemath_lane_evaluation:{uuid}:v1``)."""
    ref = str(output_payload.get("canonical_evaluation_ref") or "")
    parts = ref.split(":")
    if len(parts) >= 2 and parts[1]:
        return parts[1]
    return str(output_payload.get("output_id") or "forgemath-eval")


def emit_forgemath_lineage(
    *,
    report_payload: dict[str, Any],
    output_payload: dict[str, Any],
    output_artifact_path: str | None = None,
    output_artifact_hash: str | None = None,
) -> str:
    """Emit forgemath_evaluation + forgemath_output (+ consumed edge to eval-cal when found).
    Returns the lineage outcome string. Default-OFF (``FORGEMATH_LINEAGE_URL`` unset → no-op).
    Never raises.

    ``output_artifact_path``/``output_artifact_hash`` locate the full output contract the authority
    wrote; the forgemath_output node references it via artifact_ref so a consumer resolves the rich
    result (incl. the ``proposal_candidate_allowed`` gate) from the artifact, not the slim node.
    """
    base_url = os.environ.get(FORGEMATH_LINEAGE_URL_ENV, "").strip()
    if not base_url:
        return "lineage_missing"
    try:
        from forge_lineage_sdk import LineageClient

        from app.lineage.emitter import ForgeMathLineageEmitter

        token = os.environ.get(FORGEMATH_LINEAGE_TOKEN_ENV, "").strip() or "local-forgemath"
        client = LineageClient(
            base_url=base_url,
            writer_identity=ForgeMathLineageEmitter.WRITER_IDENTITY,
            writer_token=token,
        )
        calibration_report_id = str(report_payload.get("calibration_report_id") or "")
        upstream = _discover_eval_cal_record(client, calibration_report_id)
        if upstream is None:
            logger.warning(
                "forgemath lineage: no eval_cal_record node for calibration_report_id=%r; "
                "emitting without the consumed edge",
                calibration_report_id,
            )
        status = ForgeMathLineageEmitter(client).emit_evaluation_and_output(
            lane_evaluation_id=_lane_evaluation_id(output_payload),
            lane_id=str(output_payload.get("lane_id") or "") or None,
            output_payload=dict(output_payload),
            evaluated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            upstream_eval_cal_node_id=upstream,
            output_artifact_path=output_artifact_path,
            output_artifact_hash=output_artifact_hash,
        )
        return status.outcome
    except Exception as exc:  # noqa: BLE001
        logger.warning("forgemath lineage emission skipped; evaluation continues", exc_info=exc)
        return "lineage_missing"
