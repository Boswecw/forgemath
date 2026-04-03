from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import select

from app.api.evaluation_router import (
    get_lane_evaluation_lifecycle,
    get_lane_evaluation_lineage,
    transition_lane_evaluation_lifecycle,
)
from app.models.evaluation import TraceBundle
from app.schemas.evaluation import LaneEvaluationLifecycleTransitionCreate
from app.schemas.governance import PolicyBundleCreate
from app.services import evaluation_service, registry_service
from tests.test_phase2_api import _create_input_bundle, _evaluation_create, _seed_phase1_bindings


def test_lifecycle_read_exposes_creation_event_and_current_posture(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings))

    lifecycle = get_lane_evaluation_lifecycle("eval-001", db)
    assert lifecycle.replay_state == "replay_safe"
    assert lifecycle.stale_state == "fresh"
    assert lifecycle.recomputation_action == "no_recompute_needed"
    assert lifecycle.lifecycle_events[0].event_type == "evaluation_created"
    assert lifecycle.lifecycle_events[0].reason_code == "initial_state_recorded"


def test_policy_superseded_transition_records_stale_lifecycle_event(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings))

    registry_service.create_policy_bundle(
        db,
        PolicyBundleCreate(
            policy_bundle_id=bindings["null_policy"].policy_bundle_id,
            policy_kind="null_policy",
            lane_id=bindings["lane_spec"].lane_id,
            version=2,
            effective_from=datetime(2026, 4, 2, 13, 0, tzinfo=timezone.utc),
            created_by="phase3-test",
            supersedes_version=1,
            retired_reason="bounded governed policy supersession",
            payload={"behavior": "governed-null-v2"},
        ),
    )

    lifecycle = transition_lane_evaluation_lifecycle(
        "eval-001",
        LaneEvaluationLifecycleTransitionCreate(
            replay_state="audit_readable_only",
            stale_state="stale_policy_superseded",
            recomputation_action="mandatory_recompute",
            lifecycle_reason_code="policy_bundle_superseded",
            lifecycle_reason_detail="Bound null policy bundle version 1 is no longer active.",
            created_by="phase3-test",
        ),
        db,
    )

    assert lifecycle.stale_state == "stale_policy_superseded"
    assert lifecycle.replay_state == "audit_readable_only"
    assert lifecycle.recomputation_action == "mandatory_recompute"
    assert lifecycle.lifecycle_events[-1].event_type == "lifecycle_transition"


def test_transition_rejects_replay_safe_when_required_trace_binding_is_missing(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(
        db,
        _evaluation_create(
            bindings,
            lane_evaluation_id="eval-audit-001",
            replay_state="audit_readable_only",
        ),
    )

    trace_bundle = db.scalar(
        select(TraceBundle).where(TraceBundle.lane_evaluation_id == "eval-audit-001")
    )
    assert trace_bundle is not None
    db.delete(trace_bundle)
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        transition_lane_evaluation_lifecycle(
            "eval-audit-001",
            LaneEvaluationLifecycleTransitionCreate(
                replay_state="replay_safe",
                stale_state="fresh",
                recomputation_action="no_recompute_needed",
                lifecycle_reason_code="manual_replay_reassessment",
                created_by="phase3-test",
            ),
            db,
        )

    assert exc_info.value.status_code == 400
    assert "trace bundle" in exc_info.value.detail.lower()


def test_transition_rejects_fresh_when_input_invalidation_is_present(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings))

    with pytest.raises(HTTPException) as exc_info:
        transition_lane_evaluation_lifecycle(
            "eval-001",
            LaneEvaluationLifecycleTransitionCreate(
                replay_state="replay_safe",
                stale_state="fresh",
                recomputation_action="optional_recompute",
                lifecycle_reason_code="input_bundle_invalidated",
                lifecycle_reason_detail="Operator flagged the frozen input bundle as invalid.",
                input_bundle_invalidated=True,
                created_by="phase3-test",
            ),
            db,
        )

    assert exc_info.value.status_code == 400
    assert "fresh" in exc_info.value.detail


def test_supersession_transition_rejects_misaligned_stale_state(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings, lane_evaluation_id="eval-001"))
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings, lane_evaluation_id="eval-002"))

    with pytest.raises(HTTPException) as exc_info:
        transition_lane_evaluation_lifecycle(
            "eval-001",
            LaneEvaluationLifecycleTransitionCreate(
                replay_state="audit_readable_only",
                stale_state="stale_upstream_changed",
                recomputation_action="preserve_as_audit_only",
                lifecycle_reason_code="semantic_supersession_recorded",
                related_evaluation_id="eval-002",
                supersession_class="semantic_supersession",
                supersession_reason="Semantic supersession requires stale_semantics_changed.",
                supersession_timestamp=datetime(2026, 4, 2, 14, 0, tzinfo=timezone.utc),
                created_by="phase3-test",
            ),
            db,
        )

    assert exc_info.value.status_code == 400
    assert "stale_semantics_changed" in exc_info.value.detail or "lane spec" in exc_info.value.detail


def test_lineage_read_preserves_superseded_history(db):
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

    lineage = get_lane_evaluation_lineage("eval-002", db)
    assert [item.lane_evaluation_id for item in lineage.lineage] == ["eval-001", "eval-002"]

    prior_lifecycle = get_lane_evaluation_lifecycle("eval-001", db)
    assert prior_lifecycle.superseded_by_evaluation_id == "eval-002"
    assert prior_lifecycle.recomputation_action == "preserve_as_audit_only"
