"""ForgeMath producer-side lineage emitter."""

from __future__ import annotations

import hashlib
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _ensure_sdk_on_path() -> None:
    here = Path(__file__).resolve()
    candidates = [
        here.parents[4] / "contracts" / "forge_lineage" / "sdk",
        Path.home() / "Forge" / "ecosystem" / "contracts" / "forge_lineage" / "sdk",
    ]
    for c in candidates:
        if c.exists() and str(c) not in sys.path:
            sys.path.insert(0, str(c))
            return


_ensure_sdk_on_path()

from forge_lineage_sdk import LineageClient, LocalOutcome  # noqa: E402
from forge_lineage_sdk.builders import build_edge, build_envelope, build_node  # noqa: E402


@dataclass
class LineageEmissionStatus:
    evaluation_node_id: str | None = None
    output_node_id: str | None = None
    produced_edge_id: str | None = None
    runtime_admission_node_id: str | None = None
    trace_node_id: str | None = None
    outcome: str = "lineage_missing"
    error: str | None = None


class ForgeMathLineageEmitter:
    WRITER_IDENTITY = "forgemath"
    SOURCE_SYSTEM = "forgemath"

    def __init__(self, client: LineageClient) -> None:
        self._client = client

    @classmethod
    def from_env(
        cls,
        *,
        base_url: str = "http://127.0.0.1:8005",
        writer_token: str = "local-forgemath",
    ) -> "ForgeMathLineageEmitter":
        return cls(
            LineageClient(
                base_url=base_url,
                writer_identity=cls.WRITER_IDENTITY,
                writer_token=writer_token,
            )
        )

    def emit_evaluation_and_output(
        self,
        *,
        lane_evaluation_id: str,
        lane_id: str | None,
        output_payload: dict[str, Any],
        evaluated_at: str,
        deterministic: bool = True,
        node_revision: str | None = None,
        trace_id: str | None = None,
    ) -> LineageEmissionStatus:
        """Emit a forgemath_evaluation node + a forgemath_output node + a
        ``produced`` ImpactEdge between them. Non-blocking."""
        try:
            return self._emit_evaluation_and_output(
                lane_evaluation_id=lane_evaluation_id,
                lane_id=lane_id,
                output_payload=output_payload,
                evaluated_at=evaluated_at,
                deterministic=deterministic,
                node_revision=node_revision,
                trace_id=trace_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("forgemath lineage emission raised", exc_info=exc)
            return LineageEmissionStatus(
                outcome="lineage_missing", error=f"{type(exc).__name__}: {exc}"
            )

    def emit_runtime_admission(
        self,
        *,
        evaluation_node_id: str,
        admission_id: str,
        lane_evaluation_id: str,
        decision: str,
        decided_at: str,
        reason: str | None = None,
        trace_id: str | None = None,
    ) -> LineageEmissionStatus:
        try:
            return self._emit_runtime_admission(
                evaluation_node_id=evaluation_node_id,
                admission_id=admission_id,
                lane_evaluation_id=lane_evaluation_id,
                decision=decision,
                decided_at=decided_at,
                reason=reason,
                trace_id=trace_id,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("forgemath admission lineage emission raised", exc_info=exc)
            return LineageEmissionStatus(
                outcome="lineage_missing", error=f"{type(exc).__name__}: {exc}"
            )

    # ---- internals ----

    def _emit_evaluation_and_output(
        self,
        *,
        lane_evaluation_id: str,
        lane_id: str | None,
        output_payload: dict[str, Any],
        evaluated_at: str,
        deterministic: bool,
        node_revision: str | None,
        trace_id: str | None,
    ) -> LineageEmissionStatus:
        trace = trace_id or f"trace:forgemath:{lane_evaluation_id}"

        eval_payload: dict[str, Any] = {
            "schema_version": "forgemath_evaluation.v1",
            "lane_evaluation_id": lane_evaluation_id,
            "evaluated_at": evaluated_at,
            "deterministic": bool(deterministic),
        }
        if lane_id:
            eval_payload["lane_id"] = lane_id
        if node_revision:
            eval_payload["node_revision"] = node_revision

        eval_node = build_node(
            node_type="forgemath_evaluation",
            payload_schema_id="forgemath_evaluation",
            payload_schema_version="v1",
            payload=eval_payload,
            source_system=self.SOURCE_SYSTEM,
            source_component="forgemath/evaluation",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            stable_source_id=f"forgemath:eval:{lane_evaluation_id}",
        )

        # Compute output identity if not provided.
        if "payload_hash" not in output_payload or "output_id" not in output_payload:
            digest = hashlib.sha256(
                json.dumps(output_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            output_payload = {**output_payload}
            output_payload.setdefault("output_id", f"forgemath_output:{digest[:16]}")
            output_payload.setdefault("payload_hash", digest)
            output_payload.setdefault("lane_evaluation_id", lane_evaluation_id)
            output_payload.setdefault("schema_version", "forgemath_output.v1")

        output_node = build_node(
            node_type="forgemath_output",
            payload_schema_id="forgemath_output",
            payload_schema_version="v1",
            payload=output_payload,
            source_system=self.SOURCE_SYSTEM,
            source_component="forgemath/output",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            stable_source_id=f"forgemath:output:{output_payload['output_id']}",
        )

        produced_edge = build_edge(
            source_node_id=eval_node["node_id"],
            target_node_id=output_node["node_id"],
            edge_type="produced",
            causality_class="deterministic",
            effect_class="shaping",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            created_by_system=self.SOURCE_SYSTEM,
            stable_source_id=f"{eval_node['node_id']}->{output_node['node_id']}",
        )

        envelope = build_envelope(
            writer_identity=self.WRITER_IDENTITY,
            trace_id=trace,
            nodes=[eval_node, output_node],
            edges=[produced_edge],
        )
        result = self._client.emit_envelope(envelope)

        if result.outcome in (LocalOutcome.accepted, LocalOutcome.accepted_duplicate):
            return LineageEmissionStatus(
                evaluation_node_id=eval_node["node_id"],
                output_node_id=output_node["node_id"],
                produced_edge_id=produced_edge["edge_id"],
                outcome="lineage_available",
            )
        return LineageEmissionStatus(
            evaluation_node_id=eval_node["node_id"],
            output_node_id=output_node["node_id"],
            outcome="lineage_degraded",
            error=(result.error.message if result.error else f"non-accept: {result.outcome}"),
        )

    def _emit_runtime_admission(
        self,
        *,
        evaluation_node_id: str,
        admission_id: str,
        lane_evaluation_id: str,
        decision: str,
        decided_at: str,
        reason: str | None,
        trace_id: str | None,
    ) -> LineageEmissionStatus:
        trace = trace_id or f"trace:forgemath:{lane_evaluation_id}"
        payload: dict[str, Any] = {
            "schema_version": "forgemath_runtime_admission.v1",
            "admission_id": admission_id,
            "lane_evaluation_id": lane_evaluation_id,
            "decided_at": decided_at,
            "decision": decision,
        }
        if reason:
            payload["reason"] = reason
        admission_node = build_node(
            node_type="forgemath_runtime_admission",
            payload_schema_id="forgemath_runtime_admission",
            payload_schema_version="v1",
            payload=payload,
            source_system=self.SOURCE_SYSTEM,
            source_component="forgemath/runtime",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            stable_source_id=f"forgemath:admission:{admission_id}",
        )
        informed_edge = build_edge(
            source_node_id=evaluation_node_id,
            target_node_id=admission_node["node_id"],
            edge_type="informed",
            causality_class="derived",
            effect_class="advisory",
            trace_id=trace,
            writer_identity=self.WRITER_IDENTITY,
            created_by_system=self.SOURCE_SYSTEM,
            stable_source_id=f"{evaluation_node_id}->{admission_node['node_id']}",
        )
        envelope = build_envelope(
            writer_identity=self.WRITER_IDENTITY,
            trace_id=trace,
            nodes=[admission_node],
            edges=[informed_edge],
        )
        result = self._client.emit_envelope(envelope)
        if result.outcome in (LocalOutcome.accepted, LocalOutcome.accepted_duplicate):
            return LineageEmissionStatus(
                runtime_admission_node_id=admission_node["node_id"],
                outcome="lineage_available",
            )
        return LineageEmissionStatus(
            runtime_admission_node_id=admission_node["node_id"],
            outcome="lineage_degraded",
            error=(result.error.message if result.error else f"non-accept: {result.outcome}"),
        )


class NullLineageEmitter:
    def emit_evaluation_and_output(self, **_kwargs: Any) -> LineageEmissionStatus:
        return LineageEmissionStatus(outcome="lineage_missing", error="emitter_disabled")

    def emit_runtime_admission(self, **_kwargs: Any) -> LineageEmissionStatus:
        return LineageEmissionStatus(outcome="lineage_missing", error="emitter_disabled")
