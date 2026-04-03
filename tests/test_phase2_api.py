from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.api.evaluation_router import (
    create_incident_record,
    create_input_bundle,
    create_lane_evaluation,
    create_replay_queue_event,
    get_incident_record,
    get_lane_evaluation,
    get_replay_queue_event,
)
from app.models.evaluation import InputBundle
from app.schemas.evaluation import (
    CompatibilityBinding,
    IncidentRecordCreate,
    InputBundleCreate,
    IncidentSeverity,
    LaneEvaluationCreate,
    LaneFactorValueCreate,
    LaneOutputValueCreate,
    ReplayQueueEventCreate,
    TraceBundleCreate,
    TraceEventCreate,
)
from app.schemas.governance import (
    CompatibilityTuple,
    LaneSpecCreate,
    ParameterSetCreate,
    PolicyBundleCreate,
    RuntimeProfileCreate,
    ScopeRegistryCreate,
    ThresholdSetCreate,
    VariableRegistryCreate,
)
from app.services import evaluation_service, registry_service


def _seed_phase1_bindings(db, *, lane_id: str = "verification_burden", lane_family: str = "canonical_numeric", trace_tier: str = "tier_1_full"):
    lane_spec = registry_service.create_lane_spec(
        db,
        LaneSpecCreate(
            lane_id=lane_id,
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase2-test",
            lane_family=lane_family,
            trace_tier=trace_tier,
            is_admissible=True,
            payload={"contract_version": "v1", "lane_id": lane_id},
        ),
    )
    variable_registry = registry_service.create_variable_registry(
        db,
        VariableRegistryCreate(
            variable_registry_id=f"{lane_id}-variables",
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase2-test",
            payload={"variables": ["implementation_minutes"]},
        ),
    )
    parameter_set = registry_service.create_parameter_set(
        db,
        ParameterSetCreate(
            parameter_set_id=f"{lane_id}-parameters",
            lane_id=lane_id,
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase2-test",
            payload={"weights": {"w_I": 0.15}},
        ),
    )
    threshold_set = registry_service.create_threshold_set(
        db,
        ThresholdSetCreate(
            threshold_set_id=f"{lane_id}-thresholds",
            lane_id=lane_id,
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase2-test",
            payload={"bands": {"low": [0.0, 0.25]}},
        ),
    )
    null_policy = registry_service.create_policy_bundle(
        db,
        PolicyBundleCreate(
            policy_bundle_id=f"{lane_id}-null-policy",
            policy_kind="null_policy",
            lane_id=lane_id,
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase2-test",
            payload={"behavior": "governed-null"},
        ),
    )
    degraded_policy = registry_service.create_policy_bundle(
        db,
        PolicyBundleCreate(
            policy_bundle_id=f"{lane_id}-degraded-policy",
            policy_kind="degraded_mode_policy",
            lane_id=lane_id,
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase2-test",
            payload={"behavior": "governed-degraded"},
        ),
    )
    runtime_profile = registry_service.create_runtime_profile(
        db,
        RuntimeProfileCreate(
            runtime_profile_id=f"{lane_id}-runtime",
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase2-test",
            numeric_precision_mode="decimal128",
            rounding_mode="half_even",
            sort_policy_id="stable-total-order",
            serialization_policy_id="canonical-json-v1",
            timezone_policy="UTC",
            seed_policy="fixed-seed",
            non_determinism_allowed_flag=False,
        ),
    )
    scope = registry_service.create_scope_registry(
        db,
        ScopeRegistryCreate(
            scope_id=f"{lane_id}-scope",
            scope_class="local",
            display_name=f"{lane_id} local scope",
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase2-test",
            payload={"domain": "local"},
        ),
    )
    return {
        "lane_spec": lane_spec,
        "variable_registry": variable_registry,
        "parameter_set": parameter_set,
        "threshold_set": threshold_set,
        "null_policy": null_policy,
        "degraded_policy": degraded_policy,
        "runtime_profile": runtime_profile,
        "scope": scope,
    }


def _create_input_bundle(db, bindings, *, input_bundle_id: str = "bundle-001"):
    return create_input_bundle(
        InputBundleCreate(
            input_bundle_id=input_bundle_id,
            scope_id=bindings["scope"].scope_id,
            scope_version=bindings["scope"].version,
            provenance_class="operator_collected",
            collection_timestamp=datetime(2026, 4, 2, 12, 0, tzinfo=timezone.utc),
            admissibility_notes="frozen for canonical evaluation",
            normalization_scope="local_governance_surface",
            source_artifact_refs=[{"kind": "ticket", "ref": "INC-1"}],
            inline_values={"implementation_minutes": 12},
            frozen_flag=True,
            created_by="phase2-test",
        ),
        db,
    )


def _compatibility_binding(bindings):
    lane_spec = bindings["lane_spec"]
    return CompatibilityBinding(
        variable_registry_id=bindings["variable_registry"].variable_registry_id,
        parameter_set_id=bindings["parameter_set"].parameter_set_id,
        threshold_set_id=bindings["threshold_set"].threshold_set_id,
        null_policy_bundle_id=bindings["null_policy"].policy_bundle_id,
        degraded_mode_policy_bundle_id=bindings["degraded_policy"].policy_bundle_id,
        compatibility_tuple=CompatibilityTuple(
            lane_spec_version=lane_spec.version,
            variable_registry_version=bindings["variable_registry"].version,
            parameter_set_version=bindings["parameter_set"].version,
            threshold_registry_version=bindings["threshold_set"].version,
            null_policy_version=bindings["null_policy"].version,
            degraded_mode_policy_version=bindings["degraded_policy"].version,
            trace_schema_version=1,
            projection_schema_version=1,
            submodule_build_version="forge-math-phase2",
        ),
    )


def _evaluation_create(bindings, *, lane_evaluation_id: str = "eval-001", result_status: str = "computed_strict", compatibility_state: str = "resolved_hard_compatible", replay_state: str = "replay_safe", trace_tier: str = "tier_1_full", lane_family: str | None = None, supersedes_evaluation_id: str | None = None, raw_output_hash: str | None = "abc123", outputs: list[LaneOutputValueCreate] | None = None, factors: list[LaneFactorValueCreate] | None = None):
    lane_spec = bindings["lane_spec"]
    family = lane_family or lane_spec.lane_family
    output_values = outputs if outputs is not None else [
        LaneOutputValueCreate(
            output_field_name="vb_score",
            output_posture="raw",
            numeric_value=0.42,
            is_primary_output=True,
        )
    ]
    factor_values = factors if factors is not None else [
        LaneFactorValueCreate(
            factor_name="implementation_minutes",
            raw_value=12.0,
            normalized_value=0.24,
            weighted_value=0.12,
            provenance_class="bundle_inline_value",
            volatility_class="stable",
        )
    ]
    return LaneEvaluationCreate(
        lane_evaluation_id=lane_evaluation_id,
        supersedes_evaluation_id=supersedes_evaluation_id,
        lane_id=lane_spec.lane_id,
        lane_spec_version=lane_spec.version,
        lane_family=family,
        execution_mode="governed_manual_ingest",
        result_status=result_status,
        compatibility_resolution_state=compatibility_state,
        runtime_profile_id=bindings["runtime_profile"].runtime_profile_id,
        runtime_profile_version=bindings["runtime_profile"].version,
        input_bundle_id="bundle-001",
        replay_state=replay_state,
        stale_state="fresh",
        raw_output_hash=raw_output_hash,
        compatibility_binding=_compatibility_binding(bindings),
        output_values=output_values,
        factor_values=factor_values,
        trace_bundle=TraceBundleCreate(
            trace_bundle_id=f"trace-{lane_evaluation_id}",
            trace_tier=trace_tier,
            trace_schema_version=1,
            reconstructable_flag=trace_tier == "tier_3_reconstruction",
            trace_events=[
                TraceEventCreate(
                    trace_step_order=0,
                    trace_event_type="bundle_bound",
                    trace_payload_ref="trace://bundle-bound",
                    trace_summary="Frozen bundle bound to evaluation.",
                )
            ],
        ),
        created_by="phase2-test",
    )


def test_create_lane_evaluation_and_fetch_detail(db):
    bindings = _seed_phase1_bindings(db)
    bundle = _create_input_bundle(db, bindings)
    assert bundle.input_bundle_id == "bundle-001"

    created = create_lane_evaluation(_evaluation_create(bindings), db)
    assert created.lane_evaluation_id == "eval-001"
    assert created.trace_bundle.trace_bundle_id == "trace-eval-001"
    assert created.scope_id == bindings["scope"].scope_id
    assert len(created.output_values) == 1
    assert len(created.factor_values) == 1

    fetched = get_lane_evaluation("eval-001", db)
    assert fetched.compatibility_tuple_hash == created.compatibility_tuple_hash
    assert fetched.trace_bundle.trace_events[0].trace_event_type == "bundle_bound"


def test_evaluation_rejects_unfrozen_input_bundle(db):
    bindings = _seed_phase1_bindings(db)
    db.add(
        InputBundle(
            input_bundle_id="bundle-001",
            scope_id=bindings["scope"].scope_id,
            scope_version=bindings["scope"].version,
            provenance_class="operator_collected",
            collection_timestamp=datetime(2026, 4, 2, tzinfo=timezone.utc),
            admissibility_notes="not frozen",
            normalization_scope="local_governance_surface",
            deterministic_input_hash="bundlehash001",
            source_artifact_refs=[{"kind": "ticket", "ref": "INC-1"}],
            inline_values={"implementation_minutes": 12},
            frozen_flag=False,
            created_by="phase2-test",
        )
    )
    db.commit()

    with pytest.raises(HTTPException) as exc_info:
        create_lane_evaluation(_evaluation_create(bindings), db)

    assert exc_info.value.status_code == 400
    assert "frozen input bundle" in exc_info.value.detail


def test_evaluation_rejects_blocked_incompatible_strict_result(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_evaluation(
            _evaluation_create(
                bindings,
                compatibility_state="blocked_incompatible",
                replay_state="not_replayable",
            ),
            db,
        )

    assert exc_info.value.status_code == 400
    assert "blocked_incompatible" in exc_info.value.detail


def test_evaluation_rejects_insufficient_trace_tier(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_evaluation(
            _evaluation_create(
                bindings,
                trace_tier="tier_3_reconstruction",
            ),
            db,
        )

    assert exc_info.value.status_code == 400
    assert "trace_tier" in exc_info.value.detail


def test_hybrid_gate_lane_rejects_scalar_only_output(db):
    bindings = _seed_phase1_bindings(db, lane_id="reviewability", lane_family="hybrid_gate")
    _create_input_bundle(db, bindings)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_evaluation(
            _evaluation_create(
                bindings,
                lane_evaluation_id="eval-hybrid-001",
                lane_family="hybrid_gate",
                outputs=[
                    LaneOutputValueCreate(
                        output_field_name="rv_score",
                        output_posture="raw",
                        numeric_value=0.9,
                        is_primary_output=True,
                    )
                ],
            ),
            db,
        )

    assert exc_info.value.status_code == 400
    assert "hybrid_gate" in exc_info.value.detail


def test_blocked_evaluation_and_lineage_visibility_are_preserved(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)

    blocked = create_lane_evaluation(
        _evaluation_create(
            bindings,
            lane_evaluation_id="eval-blocked-001",
            result_status="blocked",
            compatibility_state="blocked_incompatible",
            replay_state="not_replayable",
            raw_output_hash=None,
            outputs=[
                LaneOutputValueCreate(
                    output_field_name="reviewability_gate",
                    output_posture="gated",
                    text_value="blocked_due_to_compatibility",
                    is_primary_output=True,
                )
            ],
            factors=[],
        ),
        db,
    )
    assert blocked.result_status == "blocked"
    assert blocked.compatibility_resolution_state == "blocked_incompatible"

    superseding = create_lane_evaluation(
        _evaluation_create(
            bindings,
            lane_evaluation_id="eval-blocked-002",
            result_status="audit_only",
            compatibility_state="audit_only",
            replay_state="audit_readable_only",
            raw_output_hash=None,
            supersedes_evaluation_id="eval-blocked-001",
            outputs=[
                LaneOutputValueCreate(
                    output_field_name="reviewability_gate",
                    output_posture="classified",
                    enum_value="audit_only",
                    is_primary_output=True,
                )
            ],
            factors=[],
        ),
        db,
    )
    previous = evaluation_service.get_lane_evaluation(db, "eval-blocked-001")
    assert previous.superseded_by_evaluation_id == superseding.lane_evaluation_id


def test_create_replay_queue_and_incident_records(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    create_lane_evaluation(_evaluation_create(bindings), db)

    replay = create_replay_queue_event(
        ReplayQueueEventCreate(
            replay_event_id="replay-001",
            triggering_reason="lane spec superseded",
            priority_class="standard",
            budget_class="daily_standard_budget",
            operator_review_required_flag=True,
            status="queued",
            related_lane_id=bindings["lane_spec"].lane_id,
            related_scope_id=bindings["scope"].scope_id,
            related_input_bundle_id="bundle-001",
            related_lane_evaluation_id="eval-001",
        ),
        db,
    )
    assert replay.replay_event_id == "replay-001"

    incident = create_incident_record(
        IncidentRecordCreate(
            incident_id="incident-001",
            incident_class="compatibility_resolution_failure",
            severity=IncidentSeverity.HIGH,
            affected_scope_id=bindings["scope"].scope_id,
            affected_lane_id=bindings["lane_spec"].lane_id,
            summary="Compatibility tuple did not resolve for strict execution.",
            canonical_truth_impact_flag=True,
            related_lane_evaluation_id="eval-001",
        ),
        db,
    )
    assert incident.incident_id == "incident-001"

    assert get_replay_queue_event("replay-001", db).status == "queued"
    assert get_incident_record("incident-001", db).incident_class == "compatibility_resolution_failure"
