from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from app.contracts.evaluation_spine import (
    EvaluationSpineContractError,
    validate_eval_calibration_report_payload,
    validate_forgemath_lane_evaluation_ref_payload,
)
from app.services.evaluation_spine_authority import (
    ForgeMathAuthorityInputError,
    build_forgemath_lane_evaluation_ref_payload,
    build_trace_bundle,
    evaluate_calibration_report_file,
    payload_sha256,
)

HASH_D = "sha256:" + "d" * 64


def eval_calibration_report_payload() -> dict:
    return {
        "schema_version": "eval_cal_node.calibration_report.v1",
        "calibration_report_id": "eval-calibration:550e8400-e29b-41d4-a716-446655440000:v1",
        "source_forge_eval_evidence_bundle_ref": "forge_eval_evidence_bundle:550e8400-e29b-41d4-a716-446655440000:v1",
        "source_artifact_hash": HASH_D,
        "repository_id": "forge-eval",
        "score_normalization_version": "eval-cal-node.phase04.weighted-evidence.v1",
        "calibrated_scores": [
            {
                "metric_name": "source_validation_state",
                "raw_score": 1.0,
                "calibrated_score": 1.0,
                "weight": 0.5,
            },
            {
                "metric_name": "artifact_coverage",
                "raw_score": 1.0,
                "calibrated_score": 1.0,
                "weight": 0.3,
            },
            {
                "metric_name": "validation_reference_coverage",
                "raw_score": 1.0,
                "calibrated_score": 1.0,
                "weight": 0.2,
            },
            {
                "metric_name": "weighted_confidence_candidate",
                "raw_score": 1.0,
                "calibrated_score": 1.0,
                "weight": 1.0,
            },
        ],
        "confidence_band_candidate": "high_confidence",
        "threshold_crossings": [
            {
                "threshold_id": "minimum_high_confidence_candidate",
                "crossed": True,
                "direction": "above",
            }
        ],
        "validation_state": "passed",
        "normalization_notes": [
            "Phase 04 calibration uses deterministic bounded score candidates only.",
            "ForgeMath remains the downstream math authority; eval-cal-node does not issue final lane decisions.",
        ],
    }


def test_phase05_validates_eval_calibration_report_contract() -> None:
    result = validate_eval_calibration_report_payload(eval_calibration_report_payload())

    assert result["consumer_repo_id"] == "forgemath"
    assert result["artifact_family"] == "eval_calibration_report"
    assert result["validation_state"] == "passed"


def test_phase05_builds_contract_core_lane_evaluation_ref_payload() -> None:
    report = eval_calibration_report_payload()

    payload = build_forgemath_lane_evaluation_ref_payload(report)

    assert payload["schema_version"] == "forgemath.lane_evaluation_ref.v1"
    assert payload["lane_id"] == "self_healing_candidate_confidence_v1"
    assert payload["lane_version"] == 1
    assert payload["source_eval_calibration_report_ref"] == (
        "eval_calibration_report:550e8400-e29b-41d4-a716-446655440000:v1"
    )
    assert payload["source_artifact_hash"] == payload_sha256(report)
    assert re.match(r"^forgemath_lane_evaluation:[0-9a-f-]{36}:v1$", payload["canonical_evaluation_ref"])
    assert ":1.000000:v1" in payload["canonical_score_ref"]
    assert ":allow_candidate:v1" in payload["threshold_decision_ref"]
    assert payload["proposal_candidate_allowed"] is True
    assert payload["rollback_required"] is False
    assert validate_forgemath_lane_evaluation_ref_payload(payload)["validation_state"] == "passed"


def test_phase05_authority_trace_uses_decimal_string_outputs() -> None:
    trace = build_trace_bundle(eval_calibration_report_payload())

    assert trace["canonical_confidence_score"] == "1.000000"
    assert trace["confidence_band"] == "high_confidence"
    assert trace["threshold_decision"] == "allow_candidate"
    assert trace["score_scale"] == "0.000001"


def test_phase05_lane_evaluation_is_deterministic_for_same_input() -> None:
    report = eval_calibration_report_payload()

    first = build_forgemath_lane_evaluation_ref_payload(report)
    second = build_forgemath_lane_evaluation_ref_payload(copy.deepcopy(report))

    assert first == second
    assert payload_sha256(first) == payload_sha256(second)


def test_phase05_medium_confidence_requires_review_without_rollback() -> None:
    report = eval_calibration_report_payload()
    for entry in report["calibrated_scores"]:
        if entry["metric_name"] == "validation_reference_coverage":
            entry["calibrated_score"] = 0.0
            entry["raw_score"] = 0.0
        if entry["metric_name"] == "weighted_confidence_candidate":
            entry["calibrated_score"] = 0.8
            entry["raw_score"] = 0.8

    payload = build_forgemath_lane_evaluation_ref_payload(report)
    trace = build_trace_bundle(report)

    assert trace["canonical_confidence_score"] == "0.800000"
    assert trace["confidence_band"] == "medium_confidence"
    assert trace["threshold_decision"] == "review_required"
    assert payload["proposal_candidate_allowed"] is False
    assert payload["rollback_required"] is False


def test_phase05_low_confidence_rejects_and_requires_rollback() -> None:
    report = eval_calibration_report_payload()
    for entry in report["calibrated_scores"]:
        if entry["metric_name"] == "source_validation_state":
            entry["calibrated_score"] = 0.0
            entry["raw_score"] = 0.0
        if entry["metric_name"] == "validation_reference_coverage":
            entry["calibrated_score"] = 0.0
            entry["raw_score"] = 0.0
        if entry["metric_name"] == "weighted_confidence_candidate":
            entry["calibrated_score"] = 0.3
            entry["raw_score"] = 0.3

    payload = build_forgemath_lane_evaluation_ref_payload(report)
    trace = build_trace_bundle(report)

    assert trace["canonical_confidence_score"] == "0.300000"
    assert trace["threshold_decision"] == "reject_candidate"
    assert payload["proposal_candidate_allowed"] is False
    assert payload["rollback_required"] is True


def test_phase05_file_runner_writes_valid_lane_evaluation_ref(tmp_path: Path) -> None:
    input_path = tmp_path / "eval_calibration_report.contract.json"
    input_path.write_text(json.dumps(eval_calibration_report_payload()), encoding="utf-8")

    result = evaluate_calibration_report_file(input_path, tmp_path / "out")
    output_path = Path(result["output_path"])

    assert output_path.name == "forgemath_lane_evaluation_ref.contract.json"
    assert output_path.exists()
    persisted = json.loads(output_path.read_text(encoding="utf-8"))
    assert persisted == result["payload"]
    assert validate_forgemath_lane_evaluation_ref_payload(persisted)["validation_state"] == "passed"
    assert result["trace"]["canonical_confidence_score"] == "1.000000"


def test_phase05_fails_closed_when_required_metric_missing() -> None:
    report = eval_calibration_report_payload()
    report["calibrated_scores"] = [
        item for item in report["calibrated_scores"] if item["metric_name"] != "artifact_coverage"
    ]

    with pytest.raises(ForgeMathAuthorityInputError):
        build_forgemath_lane_evaluation_ref_payload(report)


def test_phase05_fails_closed_when_eval_calibration_contract_is_invalid() -> None:
    report = eval_calibration_report_payload()
    report["validation_state"] = "not_valid"

    with pytest.raises(EvaluationSpineContractError):
        build_forgemath_lane_evaluation_ref_payload(report)
