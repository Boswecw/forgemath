from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

EVAL_CALIBRATION_REPORT_SCHEMA_VERSION = "eval_cal_node.calibration_report.v1"
FORGEMATH_LANE_EVALUATION_REF_SCHEMA_VERSION = "forgemath.lane_evaluation_ref.v1"
LANE_ID = "self_healing_candidate_confidence_v1"
NON_RECALCULATION_NOTICE = (
    "Downstream systems must reference this ForgeMath result and must not recalculate "
    "canonical confidence, band, threshold, proposal allowance, or rollback decision."
)


class EvaluationSpineContractError(ValueError):
    """Raised when an evaluation-spine payload violates a governed contract."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


def _candidate_schema_paths(family: str, filename: str) -> list[Path]:
    candidates: list[Path] = []
    for raw_entry in sys.path:
        if not raw_entry:
            continue
        entry = Path(raw_entry).resolve()
        candidates.extend(
            [
                entry / "contracts" / "families" / family / filename,
                entry / "forge_contract_core" / "contracts" / "families" / family / filename,
            ]
        )
    # Local fallback for future vendored contract copies, if present.
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidates.append(parent / "contracts" / "families" / family / filename)
    return candidates


def _load_contract_schema(family: str, filename: str) -> dict[str, Any] | None:
    for path in _candidate_schema_paths(family, filename):
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    return None


def _format_error_path(path: list[Any]) -> str:
    return "$" if not path else "$" + "".join(f"[{part!r}]" if isinstance(part, int) else f".{part}" for part in path)


def _validate_with_jsonschema(payload: dict[str, Any], schema: dict[str, Any], *, artifact_family: str) -> None:
    try:
        from jsonschema import Draft7Validator
    except Exception:
        return

    validator = Draft7Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda err: (list(err.path), err.message))
    if not errors:
        return
    raise EvaluationSpineContractError(
        "payload failed contract-core schema validation",
        details={
            "artifact_family": artifact_family,
            "errors": [
                {
                    "path": _format_error_path(list(error.path)),
                    "message": error.message,
                }
                for error in errors
            ],
        },
    )


def _require_dict(payload: Any, *, artifact_family: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise EvaluationSpineContractError(
            "payload must be a JSON object",
            details={"artifact_family": artifact_family, "actual_type": type(payload).__name__},
        )
    return payload


def _require_keys(payload: dict[str, Any], keys: list[str], *, artifact_family: str) -> None:
    missing = [key for key in keys if key not in payload]
    if missing:
        raise EvaluationSpineContractError(
            "payload missing required fields",
            details={"artifact_family": artifact_family, "missing": missing},
        )


def _fallback_validate_eval_calibration_report(payload: dict[str, Any]) -> None:
    _require_keys(
        payload,
        [
            "schema_version",
            "calibration_report_id",
            "source_forge_eval_evidence_bundle_ref",
            "source_artifact_hash",
            "repository_id",
            "score_normalization_version",
            "calibrated_scores",
            "confidence_band_candidate",
            "threshold_crossings",
            "validation_state",
        ],
        artifact_family="eval_calibration_report",
    )
    if payload.get("schema_version") != EVAL_CALIBRATION_REPORT_SCHEMA_VERSION:
        raise EvaluationSpineContractError(
            "unexpected eval calibration schema_version",
            details={"actual": payload.get("schema_version")},
        )
    if payload.get("validation_state") not in {"passed", "failed", "blocked"}:
        raise EvaluationSpineContractError("invalid validation_state")
    if payload.get("confidence_band_candidate") not in {
        "high_confidence",
        "medium_confidence",
        "low_confidence",
        "unknown",
    }:
        raise EvaluationSpineContractError("invalid confidence_band_candidate")
    if not isinstance(payload.get("calibrated_scores"), list) or not payload["calibrated_scores"]:
        raise EvaluationSpineContractError("calibrated_scores must be a non-empty list")
    for item in payload["calibrated_scores"]:
        if not isinstance(item, dict):
            raise EvaluationSpineContractError("calibrated_scores entries must be objects")
        _require_keys(
            item,
            ["metric_name", "raw_score", "calibrated_score", "weight"],
            artifact_family="eval_calibration_report.calibrated_score",
        )


def _fallback_validate_forgemath_lane_evaluation_ref(payload: dict[str, Any]) -> None:
    _require_keys(
        payload,
        [
            "schema_version",
            "lane_id",
            "lane_version",
            "source_eval_calibration_report_ref",
            "source_artifact_hash",
            "canonical_evaluation_ref",
            "canonical_score_ref",
            "threshold_decision_ref",
            "proposal_candidate_allowed",
            "rollback_required",
        ],
        artifact_family="forgemath_lane_evaluation_ref",
    )
    if payload.get("schema_version") != FORGEMATH_LANE_EVALUATION_REF_SCHEMA_VERSION:
        raise EvaluationSpineContractError("unexpected forgemath lane evaluation schema_version")
    if payload.get("lane_id") != LANE_ID:
        raise EvaluationSpineContractError("unexpected lane_id")
    if payload.get("lane_version") != 1:
        raise EvaluationSpineContractError("unexpected lane_version")
    if not re.match(r"^[a-z][a-z0-9_]*:[0-9a-fA-F-]{36}:v[1-9][0-9]*$", str(payload.get("source_eval_calibration_report_ref", ""))):
        raise EvaluationSpineContractError("source_eval_calibration_report_ref is malformed")
    if not re.match(r"^sha256:[a-f0-9]{64}$", str(payload.get("source_artifact_hash", ""))):
        raise EvaluationSpineContractError("source_artifact_hash is malformed")
    if "non_recalculation_notice" in payload and payload["non_recalculation_notice"] != NON_RECALCULATION_NOTICE:
        raise EvaluationSpineContractError("non_recalculation_notice is not canonical")


def validate_eval_calibration_report_payload(payload: Any) -> dict[str, Any]:
    checked = _require_dict(payload, artifact_family="eval_calibration_report")
    schema = _load_contract_schema(
        "eval_calibration_report",
        "eval_calibration_report.v1.schema.json",
    )
    if schema is not None:
        _validate_with_jsonschema(checked, schema, artifact_family="eval_calibration_report")
    _fallback_validate_eval_calibration_report(checked)
    return {
        "consumer_repo_id": "forgemath",
        "artifact_family": "eval_calibration_report",
        "artifact_version": 1,
        "validation_state": "passed",
    }


def validate_forgemath_lane_evaluation_ref_payload(payload: Any) -> dict[str, Any]:
    checked = _require_dict(payload, artifact_family="forgemath_lane_evaluation_ref")
    schema = _load_contract_schema(
        "forgemath_lane_evaluation_ref",
        "forgemath_lane_evaluation_ref.v1.schema.json",
    )
    if schema is not None:
        _validate_with_jsonschema(checked, schema, artifact_family="forgemath_lane_evaluation_ref")
    _fallback_validate_forgemath_lane_evaluation_ref(checked)
    return {
        "consumer_repo_id": "forgemath",
        "artifact_family": "forgemath_lane_evaluation_ref",
        "artifact_version": 1,
        "validation_state": "passed",
    }
