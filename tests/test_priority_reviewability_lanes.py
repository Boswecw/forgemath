from decimal import Decimal

import pytest
from fastapi import HTTPException

from app.api.evaluation_router import create_lane_execution
from tests.test_phase6_execution import (
    _create_input_bundle,
    _execution_request,
    _generic_bands,
    _seed_execution_bindings,
)


PRIORITY_VARIABLES = ["RP", "VB", "EF", "RGR", "CE", "GV", "control_gap_present", "IG"]
PRIORITY_PARAMETERS = {
    "weights": {
        "lambda_1": "0.18",
        "lambda_2": "0.14",
        "lambda_3": "0.14",
        "lambda_4": "0.22",
        "lambda_5": "0.10",
        "lambda_6": "0.10",
        "lambda_7": "0.07",
        "lambda_8": "0.05",
    }
}
PRIORITY_INPUTS = {
    "RP": "0.8",
    "VB": "0.6",
    "EF": "0.5",
    "RGR": "0.7",
    "CE": "0.2",
    "GV": "0.4",
    "control_gap_present": 1,
    "IG": "0.4",
}

REVIEWABILITY_VARIABLES = [
    "m_evidence",
    "m_lineage",
    "m_compat",
    "m_replay",
    "m_degraded",
    "m_invalid",
]
REVIEWABILITY_PARAMETERS = {
    "coefficients": {
        "beta_evidence": "0.30",
        "beta_lineage": "0.25",
        "beta_compat": "0.30",
        "beta_replay": "0.25",
        "beta_degraded": "0.15",
        "beta_invalid": "0.25",
    }
}


def _seed_priority(db):
    return _seed_execution_bindings(
        db,
        lane_id="priority_score",
        variable_names=PRIORITY_VARIABLES,
        parameter_payload=PRIORITY_PARAMETERS,
        threshold_payload=_generic_bands(),
    )


def _seed_reviewability(db, *, lane_family: str = "hybrid_gate"):
    return _seed_execution_bindings(
        db,
        lane_id="reviewability",
        variable_names=REVIEWABILITY_VARIABLES,
        parameter_payload=REVIEWABILITY_PARAMETERS,
        threshold_payload=_generic_bands(),
        lane_family=lane_family,
    )


def _output_by_name(created):
    return {output.output_field_name: output for output in created.evaluation.output_values}


def test_priority_score_golden_vector_persists_exact_factors_and_trace(db):
    bindings = _seed_priority(db)
    _create_input_bundle(db, bindings, PRIORITY_INPUTS)

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="priority-golden-001"),
        db,
    )

    outputs = _output_by_name(created)
    factors = {factor.factor_name: factor for factor in created.evaluation.factor_values}
    assert created.result_status == "computed_strict"
    assert created.evaluation.lane_family == "canonical_numeric"
    assert outputs["priority_score_raw"].numeric_value == Decimal("0.642")
    assert outputs["priority_score_band"].enum_value == "high"
    assert factors["CE"].normalized_value == Decimal("0.8")
    assert factors["CE"].weighted_value == Decimal("0.08")
    assert factors["GV"].normalized_value == Decimal("0.6")
    assert factors["control_gap_present"].weighted_value == Decimal("0.07")
    assert factors["IG"].weighted_value == Decimal("-0.02")
    assert any(
        event.trace_payload_ref == "trace://lane/priority_score/factor/IG"
        and "subtracted with contribution -0.02" in event.trace_summary
        for event in created.evaluation.trace_bundle.trace_events
    )


@pytest.mark.parametrize("field_name,bad_value", [("RP", "1.01"), ("CE", "-0.01"), ("IG", True)])
def test_priority_score_rejects_out_of_contract_unit_inputs(db, field_name, bad_value):
    bindings = _seed_priority(db)
    values = {**PRIORITY_INPUTS, field_name: bad_value}
    _create_input_bundle(db, bindings, values)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert field_name in exc_info.value.detail


def test_reviewability_strict_posture_is_hybrid_and_replay_safe(db):
    bindings = _seed_reviewability(db)
    _create_input_bundle(db, bindings, {name: 0 for name in REVIEWABILITY_VARIABLES})

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="reviewability-strict-001"),
        db,
    )

    outputs = _output_by_name(created)
    assert created.result_status == "computed_strict"
    assert created.replay_state == "replay_safe"
    assert created.raw_output_hash is not None
    assert created.evaluation.lane_family == "hybrid_gate"
    assert outputs["reviewability_raw"].numeric_value == Decimal("1")
    assert outputs["reviewability_posture"].enum_value == "reviewable"
    assert outputs["reviewability_reason_set"].text_value == "none"


def test_reviewability_degraded_only_emits_computed_degraded(db):
    bindings = _seed_reviewability(db)
    values = {name: 0 for name in REVIEWABILITY_VARIABLES}
    values["m_degraded"] = 1
    _create_input_bundle(db, bindings, values)

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="reviewability-degraded-001"),
        db,
    )

    outputs = _output_by_name(created)
    assert created.result_status == "computed_degraded"
    assert created.replay_state == "replay_safe"
    assert created.evaluation.recomputation_action == "optional_recompute"
    assert created.raw_output_hash is not None
    assert outputs["reviewability_raw"].numeric_value == Decimal("0.85")
    assert outputs["reviewability_posture"].enum_value == "degraded"
    assert outputs["reviewability_reason_set"].text_value == "degraded_evidence_posture"


def test_reviewability_hard_gate_blocks_even_with_numeric_posture(db):
    bindings = _seed_reviewability(db)
    values = {name: 0 for name in REVIEWABILITY_VARIABLES}
    values.update({"m_evidence": 1, "m_lineage": 1, "m_degraded": 1})
    _create_input_bundle(db, bindings, values)

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="reviewability-blocked-001"),
        db,
    )

    outputs = _output_by_name(created)
    assert created.result_status == "blocked"
    assert created.replay_state == "audit_readable_only"
    assert created.raw_output_hash is None
    assert created.evaluation.recomputation_action == "preserve_as_audit_only"
    assert outputs["reviewability_raw"].numeric_value == Decimal("0.44625")
    assert outputs["reviewability_posture"].enum_value == "blocked"
    assert outputs["reviewability_reason_set"].text_value == (
        "required_evidence_missing,lineage_broken,degraded_evidence_posture"
    )
    assert any(
        event.trace_event_type == "posture_derived"
        and "result_status=blocked" in event.trace_summary
        for event in created.evaluation.trace_bundle.trace_events
    )

    repeated = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="reviewability-blocked-002"),
        db,
    )
    assert repeated.result_status == "blocked"
    assert repeated.lane_evaluation_id == "reviewability-blocked-002"


def test_reviewability_rejects_canonical_numeric_lane_family(db):
    bindings = _seed_reviewability(db, lane_family="canonical_numeric")
    _create_input_bundle(db, bindings, {name: 0 for name in REVIEWABILITY_VARIABLES})

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert "requires lane_family=hybrid_gate" in exc_info.value.detail


@pytest.mark.parametrize(
    "lane_id,variable_names,parameter_payload,input_values,lane_family",
    (
        (
            "priority_score",
            PRIORITY_VARIABLES,
            {
                **PRIORITY_PARAMETERS,
                "weights": {**PRIORITY_PARAMETERS["weights"], "lambda_1": "1.01"},
            },
            PRIORITY_INPUTS,
            "canonical_numeric",
        ),
        (
            "reviewability",
            REVIEWABILITY_VARIABLES,
            {
                **REVIEWABILITY_PARAMETERS,
                "coefficients": {
                    **REVIEWABILITY_PARAMETERS["coefficients"],
                    "beta_invalid": "-0.01",
                },
            },
            {name: 0 for name in REVIEWABILITY_VARIABLES},
            "hybrid_gate",
        ),
    ),
)
def test_new_lane_parameter_contracts_fail_closed(
    db,
    lane_id,
    variable_names,
    parameter_payload,
    input_values,
    lane_family,
):
    bindings = _seed_execution_bindings(
        db,
        lane_id=lane_id,
        variable_names=variable_names,
        parameter_payload=parameter_payload,
        threshold_payload=_generic_bands(),
        lane_family=lane_family,
    )
    _create_input_bundle(db, bindings, input_values)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert "does not satisfy the supported execution contract" in exc_info.value.detail


def test_priority_score_rejects_caller_supplied_formula_fields(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="priority_score",
        variable_names=PRIORITY_VARIABLES,
        parameter_payload={**PRIORITY_PARAMETERS, "expression": "RP + VB"},
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(db, bindings, PRIORITY_INPUTS)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert "does not satisfy the supported execution contract" in exc_info.value.detail


@pytest.mark.parametrize("field_name", REVIEWABILITY_VARIABLES)
def test_reviewability_rejects_non_binary_issue_flags(db, field_name):
    bindings = _seed_reviewability(db)
    values = {name: 0 for name in REVIEWABILITY_VARIABLES}
    values[field_name] = "0.5"
    _create_input_bundle(db, bindings, values)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert f"{field_name} must be boolean or 0/1" in exc_info.value.detail
