"""Mock-transport harness for emitter tests.

We do NOT import dataforge-Local because both repos define a top-level ``app``
package and the imports collide. Instead we record outbound requests via
httpx.MockTransport and assert on the captured envelopes / schemas.
"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any

import httpx


_REPO_ROOT = Path(__file__).resolve().parents[4]
_SDK_PATH = _REPO_ROOT / "contracts" / "forge_lineage" / "sdk"
if str(_SDK_PATH) not in sys.path:
    sys.path.insert(0, str(_SDK_PATH))


class RecordingLineageBackend:
    """In-memory backend that mimics enough of dataforge-Local's behavior to
    drive the LineageClient through happy + duplicate paths."""

    def __init__(self) -> None:
        self.envelopes: list[dict[str, Any]] = []
        self.nodes: list[dict[str, Any]] = []
        self.edges: list[dict[str, Any]] = []
        self.idempotency_keys: set[str] = set()

    def __call__(self, request: httpx.Request) -> httpx.Response:
        import json as _json

        body = _json.loads(request.content.decode("utf-8")) if request.content else {}
        path = request.url.path

        if path == "/api/v1/lineage/envelopes":
            self.envelopes.append(body)
            accepted_nodes = []
            accepted_edges = []
            for n in body.get("nodes", []):
                if n["idempotency_key"] in self.idempotency_keys:
                    accepted_nodes.append(self._receipt("node", n, "accepted_duplicate"))
                else:
                    self.nodes.append(n)
                    self.idempotency_keys.add(n["idempotency_key"])
                    accepted_nodes.append(self._receipt("node", n, "accepted"))
            for e in body.get("edges", []):
                if e["idempotency_key"] in self.idempotency_keys:
                    accepted_edges.append(self._receipt("edge", e, "accepted_duplicate"))
                else:
                    self.edges.append(e)
                    self.idempotency_keys.add(e["idempotency_key"])
                    accepted_edges.append(self._receipt("edge", e, "accepted"))
            return httpx.Response(
                200,
                json={
                    "accepted_nodes": accepted_nodes,
                    "accepted_edges": accepted_edges,
                    "pending_edges": [],
                    "rejected": [],
                },
            )
        if path == "/api/v1/lineage/nodes":
            return httpx.Response(
                200, json={"validation_status": "accepted", "receipt": self._receipt("node", body, "accepted")}
            )
        if path == "/api/v1/lineage/edges":
            return httpx.Response(
                200, json={"validation_status": "accepted", "receipt": self._receipt("edge", body, "accepted")}
            )
        return httpx.Response(404)

    @staticmethod
    def _receipt(record_type: str, record: dict[str, Any], status: str) -> dict[str, Any]:
        return {
            "schema_version": "LineageWriteReceipt.v1",
            "receipt_id": f"receipt:{uuid.uuid4()}",
            "record_type": record_type,
            "record_id": record.get("node_id") or record.get("edge_id") or "",
            "idempotency_key": record["idempotency_key"],
            "payload_hash": record.get("payload_hash", "0" * 64),
            "writer_identity": record["writer_identity"],
            "accepted_at": "2026-05-04T00:00:00Z",
            "validation_status": status,
            "signature_status": "unsigned",
        }


def make_recording_client(*, writer_identity: str, writer_token: str):
    from forge_lineage_sdk import LineageClient

    backend = RecordingLineageBackend()
    transport = httpx.MockTransport(backend)
    http_client = httpx.Client(transport=transport, base_url="http://testserver")
    return (
        LineageClient(
            base_url="http://testserver",
            writer_identity=writer_identity,
            writer_token=writer_token,
            http_client=http_client,
        ),
        backend,
    )
