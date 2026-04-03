import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.api.evaluation_router import (
    get_lane_evaluation_detail_projection,
    get_lane_evaluation_summary_projection,
    get_lane_factor_projection,
    get_lane_replay_diagnostic_projection,
    get_lane_trace_projection,
)
from app.models.evaluation import TraceBundle
from app.services import evaluation_service
from tests.test_phase2_api import _create_input_bundle, _evaluation_create, _seed_phase1_bindings


def test_projection_surfaces_preserve_metadata_and_authority_posture(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings))

    summary = get_lane_evaluation_summary_projection("eval-001", db)
    detail = get_lane_evaluation_detail_projection("eval-001", db)
    factors = get_lane_factor_projection("eval-001", db)
    trace = get_lane_trace_projection("eval-001", db)
    replay = get_lane_replay_diagnostic_projection("eval-001", db)

    assert summary.projection_schema_version == 1
    assert summary.source_evaluation_id == "eval-001"
    assert summary.evaluation_status == "computed_strict"
    assert summary.result_status == "computed_strict"
    assert summary.deterministic_admission_state == "admitted_canonical_deterministic"

    assert detail.trace_tier == "tier_1_full"
    assert detail.runtime_validation_reason_code == "runtime_profile_validated_for_canonical_admission"
    assert detail.determinism_certificate_ref.startswith("determinism-cert://")
    assert detail.source_trace_bundle_id == "trace-eval-001"

    assert len(factors.factors) == 1
    assert factors.factors[0].factor_name == "implementation_minutes"
    assert factors.replay_state == "replay_safe"

    assert trace.trace_bundle_id == "trace-eval-001"
    assert len(trace.trace_events) == 1
    assert trace.trace_events[0].trace_event_type == "bundle_bound"

    assert replay.replay_state == "replay_safe"
    assert replay.stale_state == "fresh"
    assert replay.runtime_validation_reason_code == "runtime_profile_validated_for_canonical_admission"
    assert replay.source_compatibility_tuple_hash == summary.source_compatibility_tuple_hash


def test_projection_summary_preserves_supersession_visibility(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings, lane_evaluation_id="eval-001"))
    evaluation_service.create_lane_evaluation(
        db,
        _evaluation_create(
            bindings,
            lane_evaluation_id="eval-002",
            supersedes_evaluation_id="eval-001",
        ),
    )

    summary = get_lane_evaluation_summary_projection("eval-001", db)
    detail = get_lane_evaluation_detail_projection("eval-001", db)

    assert summary.superseded_by_evaluation_id == "eval-002"
    assert detail.supersession_class == "parameter_supersession"
    assert detail.supersession_reason == "new governed evaluation supersedes prior lineage"


def test_projection_surfaces_preserve_blocked_posture(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(
        db,
        _evaluation_create(
            bindings,
            lane_evaluation_id="eval-blocked-001",
            result_status="blocked",
            compatibility_state="blocked_incompatible",
            replay_state="not_replayable",
            raw_output_hash=None,
            outputs=[],
            factors=[],
        ),
    )

    summary = get_lane_evaluation_summary_projection("eval-blocked-001", db)
    replay = get_lane_replay_diagnostic_projection("eval-blocked-001", db)

    assert summary.result_status == "blocked"
    assert summary.compatibility_resolution_state == "blocked_incompatible"
    assert replay.replay_state == "not_replayable"
    assert replay.recomputation_action == "preserve_as_audit_only"


def test_projection_trace_fails_closed_when_source_truth_is_missing(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings))

    trace_bundle = db.scalar(
        select(TraceBundle).where(TraceBundle.lane_evaluation_id == "eval-001")
    )
    assert trace_bundle is not None
    db.delete(trace_bundle)
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        get_lane_trace_projection("eval-001", db)

    assert exc_info.value.status_code == 404


def test_projection_summary_fails_closed_for_missing_evaluation(db):
    with pytest.raises(HTTPException) as exc_info:
        get_lane_evaluation_summary_projection("missing-eval", db)

    assert exc_info.value.status_code == 404
