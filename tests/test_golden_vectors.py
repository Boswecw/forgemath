"""
Golden-vector tests for ForgeMath Phase 6 execution substrate.

Each test pins a specific set of known inputs to exact expected outputs.
These tests are the canonical verification record for the bounded Phase 6
arithmetic. Any change to output values, factor values, or trace summary
format without a corresponding governance record indicates a breaking
change to the deterministic execution substrate.

Covers:
  - Per-factor raw/normalized/weighted value pinning (verification_burden)
  - Trace summary format stability (_decimal_to_str edge cases)
  - Score clamping at unit ceiling (_clamp_unit > 1.0, exposure_factor)
"""

from decimal import Decimal
from datetime import datetime, timezone

import pytest

from app.api.evaluation_router import create_lane_execution
from tests.test_phase6_execution import (
    _create_input_bundle,
    _execution_request,
    _generic_bands,
    _seed_execution_bindings,
)


# ---------------------------------------------------------------------------
# Golden Vector 1 — verification_burden factor-level pinning
# ---------------------------------------------------------------------------

_VB_PARAMETER_PAYLOAD = {
    "weights": {
        "w_I": 0.15,
        "w_V": 0.25,
        "w_R": 0.25,
        "w_X": 0.10,
        "w_D": 0.10,
        "w_U": 0.15,
    },
    "caps": {
        "I_cap": 60,
        "V_cap": 80,
        "R_cap": 40,
        "X_cap": 4,
        "D_cap": 60,
    },
}

_VB_INPUT_VALUES = {
    "implementation_minutes": 30,
    "verification_minutes": 40,
    "rework_minutes": 10,
    "interruption_count": 2,
    "downstream_fix_minutes": 15,
    "uncertainty_band": "moderate",
}

_VB_VARIABLE_NAMES = [
    "implementation_minutes",
    "verification_minutes",
    "rework_minutes",
    "interruption_count",
    "downstream_fix_minutes",
    "uncertainty_band",
]


def test_verification_burden_factor_level_golden_vector(db):
    """
    Pins all 6 factor-level raw/normalized/weighted values for a canonical
    verification_burden execution. If any stored value differs from these
    expected Decimals, the deterministic execution substrate has changed
    without a governance record.

    Expected arithmetic:
      implementation_minutes:  raw=30, norm=30/60=0.5,   weighted=0.5*0.15=0.075
      verification_minutes:    raw=40, norm=40/80=0.5,   weighted=0.5*0.25=0.125
      rework_minutes:          raw=10, norm=10/40=0.25,  weighted=0.25*0.25=0.0625
      interruption_count:      raw=2,  norm=2/4=0.5,     weighted=0.5*0.10=0.05
      downstream_fix_minutes:  raw=15, norm=15/60=0.25,  weighted=0.25*0.10=0.025
      uncertainty_band:        raw=0.35(moderate),       weighted=0.35*0.15=0.0525
      total = 0.39  →  band = "moderate"
    """
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=_VB_VARIABLE_NAMES,
        parameter_payload=_VB_PARAMETER_PAYLOAD,
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(db, bindings, _VB_INPUT_VALUES)

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="gv-vb-001"),
        db,
    )

    factor_by_name = {f.factor_name: f for f in created.evaluation.factor_values}

    # --- implementation_minutes ---
    f = factor_by_name["implementation_minutes"]
    assert f.raw_value == Decimal("30")
    assert f.normalized_value == Decimal("0.5")
    assert f.weighted_value == Decimal("0.075")
    assert f.provenance_class == "input_bundle_inline_value"
    assert f.volatility_class == "observed_duration_minutes"

    # --- verification_minutes ---
    f = factor_by_name["verification_minutes"]
    assert f.raw_value == Decimal("40")
    assert f.normalized_value == Decimal("0.5")
    assert f.weighted_value == Decimal("0.125")

    # --- rework_minutes ---
    f = factor_by_name["rework_minutes"]
    assert f.raw_value == Decimal("10")
    assert f.normalized_value == Decimal("0.25")
    assert f.weighted_value == Decimal("0.0625")

    # --- interruption_count ---
    f = factor_by_name["interruption_count"]
    assert f.raw_value == Decimal("2")
    assert f.normalized_value == Decimal("0.5")
    assert f.weighted_value == Decimal("0.05")
    assert f.volatility_class == "observed_count"

    # --- downstream_fix_minutes ---
    f = factor_by_name["downstream_fix_minutes"]
    assert f.raw_value == Decimal("15")
    assert f.normalized_value == Decimal("0.25")
    assert f.weighted_value == Decimal("0.025")

    # --- uncertainty_band ---
    f = factor_by_name["uncertainty_band"]
    assert f.raw_value == Decimal("0.35")
    assert f.normalized_value == Decimal("0.35")
    assert f.weighted_value == Decimal("0.0525")
    assert f.provenance_class == "input_bundle_inline_band_mapping"
    assert f.volatility_class == "ordinal_band"

    # --- pinned output score ---
    assert created.evaluation.output_values[0].numeric_value == Decimal("0.39")
    assert created.evaluation.output_values[1].enum_value == "moderate"


def test_verification_burden_trace_summary_format_stability(db):
    """
    Pins trace summary strings produced by _decimal_to_str() for known values.
    The trace summaries form part of the trace_bundle_hash. Any change to
    numeric formatting logic (e.g. normalize() behavior or format() spec)
    will change these summaries and thus the bundle hash, which is a breaking
    change requiring a migration record.
    """
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=_VB_VARIABLE_NAMES,
        parameter_payload=_VB_PARAMETER_PAYLOAD,
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(db, bindings, _VB_INPUT_VALUES)

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="gv-vb-fmt-001"),
        db,
    )

    events_by_type_ref = {
        e.trace_payload_ref: e.trace_summary
        for e in created.evaluation.trace_bundle.trace_events
    }

    impl_summary = events_by_type_ref[
        "trace://lane/verification_burden/factor/implementation_minutes"
    ]
    assert impl_summary == (
        "Factor implementation_minutes normalized to 0.5 and weighted to 0.075."
    )

    uncertainty_summary = events_by_type_ref[
        "trace://lane/verification_burden/factor/uncertainty_band"
    ]
    assert uncertainty_summary == (
        "Factor uncertainty_band mapped to 0.35 and weighted to 0.0525."
    )

    output_summary = events_by_type_ref[
        "trace://lane/verification_burden/output/verification_burden_raw"
    ]
    assert output_summary == (
        "Primary raw output 0.39 classified into band moderate."
    )


# ---------------------------------------------------------------------------
# Golden Vector 2 — exposure_factor score clamped at unit ceiling
# ---------------------------------------------------------------------------

def test_exposure_factor_score_clamped_at_unit_ceiling(db):
    """
    Verifies that _clamp_unit() saturates at 1.0 when the raw arithmetic
    result exceeds 1.0.

    With alpha_pub=1.0 and all flags=1:
      product = (1 - 1.0*1) * (1 - 0*1) * ... = 0.0
      (1 - product) = 1.0
      severity_uplift("critical") = 0.25
      raw score = 1.0 + 0.25 = 1.25  →  _clamp_unit(1.25) = 1.0

    If the clamp is removed or broken, the stored numeric_value would be
    1.25 (or fail band resolution, since 1.25 > 1.0 is outside [0, 1]).
    """
    bindings = _seed_execution_bindings(
        db,
        lane_id="exposure_factor",
        variable_names=[
            "public_exposure_flag",
            "operator_surface_flag",
            "persistence_truth_flag",
            "approval_surface_flag",
            "cross_system_flag",
            "local_cloud_boundary_flag",
            "severity_band",
        ],
        parameter_payload={
            "coefficients": {
                "alpha_pub": 1.0,
                "alpha_op": 0.0,
                "alpha_persist": 0.0,
                "alpha_approve": 0.0,
                "alpha_cross": 0.0,
                "alpha_boundary": 0.0,
            }
        },
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "public_exposure_flag": 1,
            "operator_surface_flag": 1,
            "persistence_truth_flag": 1,
            "approval_surface_flag": 1,
            "cross_system_flag": 1,
            "local_cloud_boundary_flag": 1,
            "severity_band": "critical",
        },
    )

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="gv-ef-clamp-001"),
        db,
    )

    assert created.result_status == "computed_strict"
    assert created.evaluation.deterministic_admission_state == "admitted_canonical_deterministic"

    # Score must be clamped to 1.0, not the raw arithmetic result of 1.25
    assert created.evaluation.output_values[0].output_field_name == "exposure_factor_raw"
    assert created.evaluation.output_values[0].numeric_value == Decimal("1")
    assert created.evaluation.output_values[1].enum_value == "critical"

    # Verify the output trace summary reflects the clamped value
    output_event = next(
        e
        for e in created.evaluation.trace_bundle.trace_events
        if e.trace_payload_ref == "trace://lane/exposure_factor/output/exposure_factor_raw"
    )
    assert "Primary raw output 1 classified into band critical." == output_event.trace_summary

    # public_exposure_flag factor: raw=1, weighted=1.0*1=1, normalized=1
    factor_by_name = {f.factor_name: f for f in created.evaluation.factor_values}
    pub = factor_by_name["public_exposure_flag"]
    assert pub.raw_value == Decimal("1")
    assert pub.weighted_value == Decimal("1")
    assert pub.normalized_value == Decimal("1")

    # All-zero-coefficient flags contribute zero weighted value
    op = factor_by_name["operator_surface_flag"]
    assert op.weighted_value == Decimal("0")
