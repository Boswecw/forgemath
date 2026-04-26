from __future__ import annotations

import hashlib
import json
from decimal import Decimal, ROUND_HALF_EVEN, getcontext
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from app.contracts.evaluation_spine import (
    FORGEMATH_LANE_EVALUATION_REF_SCHEMA_VERSION,
    LANE_ID,
    NON_RECALCULATION_NOTICE,
    EvaluationSpineContractError,
    validate_eval_calibration_report_payload,
    validate_forgemath_lane_evaluation_ref_payload,
)

getcontext().prec = 34

OUTPUT_FILENAME = "forgemath_lane_evaluation_ref.contract.json"
LANE_VERSION = 1
SCORE_SCALE = Decimal("0.000001")
REQUIRED_METRICS = {
    "source_validation_state": Decimal("0.50"),
    "artifact_coverage": Decimal("0.30"),
    "validation_reference_coverage": Decimal("0.20"),
}
HIGH_CONFIDENCE_THRESHOLD = Decimal("0.850000")
MEDIUM_CONFIDENCE_THRESHOLD = Decimal("0.600000")


class ForgeMathAuthorityInputError(ValueError):
    """Raised when a calibration report cannot be admitted into ForgeMath authority."""

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.details = details or {}


def stable_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def payload_sha256(payload: dict[str, Any]) -> str:
    return "sha256:" + hashlib.sha256(stable_json_bytes(payload)).hexdigest()


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ForgeMathAuthorityInputError(
            "failed to read eval calibration report JSON",
            details={"path": str(path), "error": str(exc)},
        ) from exc
    if not isinstance(loaded, dict):
        raise ForgeMathAuthorityInputError(
            "eval calibration report JSON must be an object",
            details={"path": str(path), "actual_type": type(loaded).__name__},
        )
    return loaded


def _decimal_from_score(value: Any, *, metric_name: str, field_name: str) -> Decimal:
    try:
        number = Decimal(str(value))
    except Exception as exc:
        raise ForgeMathAuthorityInputError(
            "score field is not decimal-compatible",
            details={"metric_name": metric_name, "field_name": field_name, "value": value},
        ) from exc
    if number < Decimal("0") or number > Decimal("1"):
        raise ForgeMathAuthorityInputError(
            "score field outside admitted range",
            details={"metric_name": metric_name, "field_name": field_name, "value": str(number)},
        )
    return number


def decimal_string(value: Decimal) -> str:
    return str(value.quantize(SCORE_SCALE, rounding=ROUND_HALF_EVEN))


def _metric_scores(report_payload: dict[str, Any]) -> dict[str, Decimal]:
    entries = report_payload.get("calibrated_scores")
    if not isinstance(entries, list):
        raise ForgeMathAuthorityInputError("calibrated_scores must be a list")

    scores: dict[str, Decimal] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ForgeMathAuthorityInputError("calibrated_scores entries must be objects")
        metric_name = entry.get("metric_name")
        if not isinstance(metric_name, str) or not metric_name:
            raise ForgeMathAuthorityInputError("calibrated score entry is missing metric_name")
        if metric_name in scores:
            raise ForgeMathAuthorityInputError(
                "duplicate calibrated metric is not admitted",
                details={"metric_name": metric_name},
            )
        scores[metric_name] = _decimal_from_score(
            entry.get("calibrated_score"),
            metric_name=metric_name,
            field_name="calibrated_score",
        )

    missing = sorted(set(REQUIRED_METRICS) - set(scores))
    if missing:
        raise ForgeMathAuthorityInputError(
            "eval calibration report missing required ForgeMath lane metrics",
            details={"lane_id": LANE_ID, "missing_metrics": missing},
        )
    return scores


def canonical_confidence_score(report_payload: dict[str, Any]) -> Decimal:
    scores = _metric_scores(report_payload)
    numerator = sum(scores[name] * weight for name, weight in REQUIRED_METRICS.items())
    denominator = sum(REQUIRED_METRICS.values())
    value = numerator / denominator
    if value < Decimal("0"):
        return Decimal("0")
    if value > Decimal("1"):
        return Decimal("1")
    return value


def confidence_band(score: Decimal) -> str:
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "high_confidence"
    if score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "medium_confidence"
    if score > Decimal("0"):
        return "low_confidence"
    return "unknown"


def threshold_decision(score: Decimal) -> str:
    if score >= HIGH_CONFIDENCE_THRESHOLD:
        return "allow_candidate"
    if score >= MEDIUM_CONFIDENCE_THRESHOLD:
        return "review_required"
    return "reject_candidate"


def _source_eval_calibration_report_ref(report_payload: dict[str, Any]) -> str:
    report_id = report_payload.get("calibration_report_id")
    if not isinstance(report_id, str) or not report_id.strip():
        raise ForgeMathAuthorityInputError("eval calibration report is missing calibration_report_id")
    parts = report_id.strip().split(":")
    if len(parts) >= 3:
        try:
            source_uuid = str(UUID(parts[1]))
            return f"eval_calibration_report:{source_uuid}:v1"
        except ValueError:
            pass
    source_uuid = str(uuid5(NAMESPACE_URL, f"eval-cal-node:calibration-report:{report_id.strip()}"))
    return f"eval_calibration_report:{source_uuid}:v1"


def _canonical_result_uuid(source_ref: str, source_hash: str, score: Decimal) -> str:
    seed = f"forgemath:{LANE_ID}:v{LANE_VERSION}:{source_ref}:{source_hash}:{decimal_string(score)}"
    return str(uuid5(NAMESPACE_URL, seed))


def build_forgemath_lane_evaluation_ref_payload(report_payload: dict[str, Any]) -> dict[str, Any]:
    """Build ForgeMath's canonical lane-evaluation reference payload.

    ForgeMath owns the final deterministic calculation and threshold decision.
    eval-cal-node supplies bounded calibrated inputs only.
    """

    validate_eval_calibration_report_payload(report_payload)

    if report_payload.get("validation_state") != "passed":
        raise ForgeMathAuthorityInputError(
            "ForgeMath only admits passed eval calibration reports",
            details={"validation_state": report_payload.get("validation_state")},
        )

    score = canonical_confidence_score(report_payload)
    source_ref = _source_eval_calibration_report_ref(report_payload)
    source_hash = payload_sha256(report_payload)
    result_uuid = _canonical_result_uuid(source_ref, source_hash, score)
    band = confidence_band(score)
    decision = threshold_decision(score)
    proposal_allowed = decision == "allow_candidate" and band == "high_confidence"
    rollback_required = decision == "reject_candidate"

    payload = {
        "schema_version": FORGEMATH_LANE_EVALUATION_REF_SCHEMA_VERSION,
        "lane_id": LANE_ID,
        "lane_version": LANE_VERSION,
        "source_eval_calibration_report_ref": source_ref,
        "source_artifact_hash": source_hash,
        "canonical_evaluation_ref": f"forgemath_lane_evaluation:{result_uuid}:v1",
        "canonical_score_ref": f"forgemath_canonical_score:{result_uuid}:{decimal_string(score)}:v1",
        "threshold_decision_ref": f"forgemath_threshold_decision:{result_uuid}:{decision}:v1",
        "proposal_candidate_allowed": proposal_allowed,
        "rollback_required": rollback_required,
        "non_recalculation_notice": NON_RECALCULATION_NOTICE,
    }
    validate_forgemath_lane_evaluation_ref_payload(payload)
    return payload


def build_trace_bundle(report_payload: dict[str, Any]) -> dict[str, Any]:
    """Return the bounded local trace used by tests and operator proof logs.

    The contract payload is intentionally reference-only. This trace is local
    ForgeMath evidence and is not a downstream recalculation surface.
    """

    score = canonical_confidence_score(report_payload)
    return {
        "lane_id": LANE_ID,
        "lane_version": LANE_VERSION,
        "canonical_confidence_score": decimal_string(score),
        "confidence_band": confidence_band(score),
        "threshold_decision": threshold_decision(score),
        "required_metrics": sorted(REQUIRED_METRICS),
        "score_scale": str(SCORE_SCALE),
    }


def write_forgemath_lane_evaluation_ref_payload(payload: dict[str, Any], output_dir: Path) -> Path:
    validate_forgemath_lane_evaluation_ref_payload(payload)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / OUTPUT_FILENAME
    output_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output_path


def evaluate_calibration_report_file(input_path: Path, output_dir: Path) -> dict[str, Any]:
    report_payload = _read_json_object(input_path)
    lane_ref_payload = build_forgemath_lane_evaluation_ref_payload(report_payload)
    output_path = write_forgemath_lane_evaluation_ref_payload(lane_ref_payload, output_dir)
    return {
        "artifact_family": "forgemath_lane_evaluation_ref",
        "artifact_version": 1,
        "output_path": str(output_path),
        "output_hash": payload_sha256(lane_ref_payload),
        "validation_state": "passed",
        "trace": build_trace_bundle(report_payload),
        "payload": lane_ref_payload,
    }


def evaluate_calibration_report_file_or_raise(input_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    try:
        return evaluate_calibration_report_file(Path(input_path), Path(output_dir))
    except (ForgeMathAuthorityInputError, EvaluationSpineContractError):
        raise
    except Exception as exc:
        raise ForgeMathAuthorityInputError(
            "unexpected ForgeMath authority failure",
            details={"input_path": str(input_path), "output_dir": str(output_dir), "error": str(exc)},
        ) from exc
