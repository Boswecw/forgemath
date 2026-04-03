from decimal import Decimal
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.api.evaluation_router import create_input_bundle, create_lane_execution
from app.schemas.evaluation import CompatibilityBinding, InputBundleCreate
from app.schemas.execution import LaneExecutionCreate
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


def _seed_execution_bindings(
    db,
    *,
    lane_id: str,
    variable_names: list[str],
    parameter_payload: dict,
    threshold_payload: dict,
    runtime_overrides: dict | None = None,
):
    runtime_overrides = runtime_overrides or {}
    lane_spec = registry_service.create_lane_spec(
        db,
        LaneSpecCreate(
            lane_id=lane_id,
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase6-test",
            lane_family="canonical_numeric",
            trace_tier="tier_1_full",
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
            created_by="phase6-test",
            payload={"variables": variable_names},
        ),
    )
    parameter_set = registry_service.create_parameter_set(
        db,
        ParameterSetCreate(
            parameter_set_id=f"{lane_id}-parameters",
            lane_id=lane_id,
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase6-test",
            payload=parameter_payload,
        ),
    )
    threshold_set = registry_service.create_threshold_set(
        db,
        ThresholdSetCreate(
            threshold_set_id=f"{lane_id}-thresholds",
            lane_id=lane_id,
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase6-test",
            payload=threshold_payload,
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
            created_by="phase6-test",
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
            created_by="phase6-test",
            payload={"behavior": "governed-degraded"},
        ),
    )
    runtime_profile = registry_service.create_runtime_profile(
        db,
        RuntimeProfileCreate(
            runtime_profile_id=f"{lane_id}-runtime",
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase6-test",
            numeric_precision_mode=runtime_overrides.get("numeric_precision_mode", "decimal128"),
            rounding_mode=runtime_overrides.get("rounding_mode", "half_even"),
            sort_policy_id=runtime_overrides.get("sort_policy_id", "stable-total-order"),
            serialization_policy_id=runtime_overrides.get(
                "serialization_policy_id",
                "canonical-json-v1",
            ),
            timezone_policy=runtime_overrides.get("timezone_policy", "UTC"),
            seed_policy=runtime_overrides.get("seed_policy", "fixed-seed"),
            non_determinism_allowed_flag=runtime_overrides.get(
                "non_determinism_allowed_flag",
                False,
            ),
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
            created_by="phase6-test",
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


def _create_input_bundle(db, bindings, inline_values: dict, *, input_bundle_id: str = "bundle-001"):
    return create_input_bundle(
        InputBundleCreate(
            input_bundle_id=input_bundle_id,
            scope_id=bindings["scope"].scope_id,
            scope_version=bindings["scope"].version,
            provenance_class="operator_collected",
            collection_timestamp=datetime(2026, 4, 2, 12, 0, tzinfo=timezone.utc),
            admissibility_notes="frozen for canonical execution",
            normalization_scope="local_governance_surface",
            source_artifact_refs=[{"kind": "ticket", "ref": "INC-42"}],
            inline_values=inline_values,
            frozen_flag=True,
            created_by="phase6-test",
        ),
        db,
    )


def _compatibility_binding(bindings, *, variable_registry_id: str | None = None):
    lane_spec = bindings["lane_spec"]
    return CompatibilityBinding(
        variable_registry_id=variable_registry_id or bindings["variable_registry"].variable_registry_id,
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
            submodule_build_version="forge-math-phase6",
        ),
    )


def _execution_request(
    bindings,
    *,
    compatibility_state: str = "resolved_hard_compatible",
    lane_evaluation_id: str | None = None,
    variable_registry_id: str | None = None,
    supersedes_evaluation_id: str | None = None,
):
    return LaneExecutionCreate(
        lane_evaluation_id=lane_evaluation_id,
        supersedes_evaluation_id=supersedes_evaluation_id,
        supersession_class="parameter_supersession" if supersedes_evaluation_id else None,
        supersession_reason="governed canonical execution supersedes prior active lineage" if supersedes_evaluation_id else None,
        supersession_timestamp=datetime(2026, 4, 2, 13, 0, tzinfo=timezone.utc) if supersedes_evaluation_id else None,
        lane_id=bindings["lane_spec"].lane_id,
        lane_spec_version=bindings["lane_spec"].version,
        compatibility_resolution_state=compatibility_state,
        runtime_profile_id=bindings["runtime_profile"].runtime_profile_id,
        runtime_profile_version=bindings["runtime_profile"].version,
        input_bundle_id="bundle-001",
        compatibility_binding=_compatibility_binding(
            bindings,
            variable_registry_id=variable_registry_id,
        ),
        created_by="phase6-test",
    )


def _generic_bands():
    return {
        "bands": [
            {"label": "low", "min_inclusive": 0.0, "max_exclusive": 0.25},
            {"label": "moderate", "min_inclusive": 0.25, "max_exclusive": 0.50},
            {"label": "high", "min_inclusive": 0.50, "max_exclusive": 0.75},
            {"label": "critical", "min_inclusive": 0.75, "max_inclusive": 1.0},
        ]
    }


def test_execute_verification_burden_persists_canonical_truth(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
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
        },
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "verification_minutes": 40,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="exec-vb-001"),
        db,
    )

    assert created.lane_evaluation_id == "exec-vb-001"
    assert created.result_status == "computed_strict"
    assert created.replay_state == "replay_safe"
    assert created.evaluation.deterministic_admission_state == "admitted_canonical_deterministic"
    assert created.evaluation.output_values[0].output_field_name == "verification_burden_raw"
    assert created.evaluation.output_values[0].numeric_value == Decimal("0.39")
    assert created.evaluation.output_values[1].enum_value == "moderate"
    assert len(created.evaluation.factor_values) == 6
    assert len(created.evaluation.trace_bundle.trace_events) == 8


def test_execute_recurrence_pressure_preserves_bounded_migration_replay_posture(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="recurrence_pressure",
        variable_names=[
            "recurrence_count_30d",
            "recurrence_count_90d",
            "same_system_recurrence_count",
            "cross_system_count",
            "post_control_recurrence_count",
        ],
        parameter_payload={
            "weights": {
                "w30": 0.25,
                "w90": 0.15,
                "wsame": 0.20,
                "wcross": 0.20,
                "wpost": 0.20,
            },
            "saturation": {
                "k30": 0.40,
                "k90": 0.20,
                "ksame": 0.50,
                "kcross": 0.60,
                "kpost": 0.70,
            },
        },
        threshold_payload={
            "bands": [
                {"label": "localized", "min_inclusive": 0.0, "max_exclusive": 0.25},
                {"label": "emerging", "min_inclusive": 0.25, "max_exclusive": 0.50},
                {"label": "repeating", "min_inclusive": 0.50, "max_exclusive": 0.75},
                {"label": "structural", "min_inclusive": 0.75, "max_inclusive": 1.0},
            ]
        },
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "recurrence_count_30d": 2,
            "recurrence_count_90d": 5,
            "same_system_recurrence_count": 1,
            "cross_system_count": 1,
            "post_control_recurrence_count": 0,
        },
    )

    created = create_lane_execution(
        _execution_request(
            bindings,
            lane_evaluation_id="exec-rp-001",
            compatibility_state="resolved_with_bounded_migration",
        ),
        db,
    )

    assert created.lane_evaluation_id == "exec-rp-001"
    assert created.replay_state == "replay_safe_with_bounded_migration"
    assert created.evaluation.output_values[0].numeric_value == Decimal("0.4014173836336462826566941478")
    assert created.evaluation.output_values[1].enum_value == "emerging"
    assert len(created.evaluation.factor_values) == 5


def test_execute_exposure_factor_persists_expected_score(db):
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
                "alpha_pub": 0.30,
                "alpha_op": 0.15,
                "alpha_persist": 0.25,
                "alpha_approve": 0.15,
                "alpha_cross": 0.20,
                "alpha_boundary": 0.15,
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
            "persistence_truth_flag": 0,
            "approval_surface_flag": 1,
            "cross_system_flag": 0,
            "local_cloud_boundary_flag": 1,
            "severity_band": "high",
        },
    )

    created = create_lane_execution(
        _execution_request(bindings, lane_evaluation_id="exec-ef-001"),
        db,
    )

    assert created.lane_evaluation_id == "exec-ef-001"
    assert created.evaluation.output_values[0].numeric_value == Decimal("0.7301125")
    assert created.evaluation.output_values[1].enum_value == "high"
    assert len(created.evaluation.factor_values) == 7
    assert created.evaluation.trace_bundle.trace_tier == "tier_1_full"


def test_lane_execution_rejects_missing_required_input(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
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
        },
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert "Missing: verification_minutes" in exc_info.value.detail


def test_lane_execution_rejects_unsupported_lane(db):
    body = LaneExecutionCreate(
        lane_evaluation_id="exec-ps-001",
        lane_id="priority_score",
        lane_spec_version=1,
        compatibility_resolution_state="resolved_hard_compatible",
        runtime_profile_id="priority-runtime",
        runtime_profile_version=1,
        input_bundle_id="bundle-001",
        compatibility_binding=CompatibilityBinding(
            variable_registry_id="priority-vars",
            parameter_set_id="priority-params",
            threshold_set_id="priority-thresholds",
            null_policy_bundle_id="priority-null",
            degraded_mode_policy_bundle_id="priority-degraded",
            compatibility_tuple=CompatibilityTuple(
                lane_spec_version=1,
                variable_registry_version=1,
                parameter_set_version=1,
                threshold_registry_version=1,
                null_policy_version=1,
                degraded_mode_policy_version=1,
                trace_schema_version=1,
                projection_schema_version=1,
                submodule_build_version="forge-math-phase6",
            ),
        ),
        created_by="phase6-test",
    )

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(body, db)

    assert exc_info.value.status_code == 400
    assert "not supported by the bounded Phase 6 execution substrate" in exc_info.value.detail


def test_lane_execution_rejects_missing_binding(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
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
        },
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "verification_minutes": 40,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(
            _execution_request(bindings, variable_registry_id="missing-variable-registry"),
            db,
        )

    assert exc_info.value.status_code == 404
    assert "VariableRegistry missing-variable-registry version 1 was not found." in exc_info.value.detail


def test_lane_execution_rejects_duplicate_active_current_truth_without_supersession(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
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
        },
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "verification_minutes": 40,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )
    create_lane_execution(_execution_request(bindings, lane_evaluation_id="exec-vb-001"), db)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings, lane_evaluation_id="exec-vb-002"), db)

    assert exc_info.value.status_code == 400
    assert "active governed_canonical_execution evaluation already exists" in exc_info.value.detail


def test_lane_execution_allows_explicit_supersession_of_active_current_truth(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
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
        },
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "verification_minutes": 40,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )
    create_lane_execution(_execution_request(bindings, lane_evaluation_id="exec-vb-001"), db)

    created = create_lane_execution(
        _execution_request(
            bindings,
            lane_evaluation_id="exec-vb-002",
            supersedes_evaluation_id="exec-vb-001",
        ),
        db,
    )

    assert created.lane_evaluation_id == "exec-vb-002"
    assert created.evaluation.superseded_by_evaluation_id is None

    prior = evaluation_service.get_lane_evaluation_detail(db, "exec-vb-001")
    assert prior.superseded_by_evaluation_id == "exec-vb-002"
    assert prior.recomputation_action == "preserve_as_audit_only"
    assert prior.supersession_class == "parameter_supersession"


def test_lane_execution_repeatability_preserves_hash_stability(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
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
        },
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "verification_minutes": 40,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )

    first = create_lane_execution(_execution_request(bindings, lane_evaluation_id="exec-vb-repeat-001"), db)
    second = create_lane_execution(
        _execution_request(
            bindings,
            lane_evaluation_id="exec-vb-repeat-002",
            supersedes_evaluation_id="exec-vb-repeat-001",
        ),
        db,
    )

    assert second.raw_output_hash == first.raw_output_hash
    assert second.evaluation.trace_bundle.trace_bundle_hash == first.evaluation.trace_bundle.trace_bundle_hash
    assert [
        (
            output.output_field_name,
            output.output_posture,
            output.numeric_value,
            output.enum_value,
            output.value_range_class,
        )
        for output in second.evaluation.output_values
    ] == [
        (
            output.output_field_name,
            output.output_posture,
            output.numeric_value,
            output.enum_value,
            output.value_range_class,
        )
        for output in first.evaluation.output_values
    ]
    assert [
        (
            factor.factor_name,
            factor.raw_value,
            factor.normalized_value,
            factor.weighted_value,
        )
        for factor in second.evaluation.factor_values
    ] == [
        (
            factor.factor_name,
            factor.raw_value,
            factor.normalized_value,
            factor.weighted_value,
        )
        for factor in first.evaluation.factor_values
    ]


def test_lane_execution_rejects_invalid_parameter_contract_semantics(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
            "weights": {
                "w_I": 0.20,
                "w_V": 0.25,
                "w_R": 0.25,
                "w_X": 0.10,
                "w_D": 0.10,
                "w_U": 0.20,
            },
            "caps": {
                "I_cap": 60,
                "V_cap": 80,
                "R_cap": 40,
                "X_cap": 4,
                "D_cap": 60,
            },
        },
        threshold_payload=_generic_bands(),
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "verification_minutes": 40,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert "does not satisfy the supported execution contract" in exc_info.value.detail


def test_lane_execution_rejects_invalid_threshold_topology(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
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
        },
        threshold_payload={
            "bands": [
                {"label": "low", "min_inclusive": 0.0, "max_exclusive": 0.25},
                {"label": "moderate", "min_inclusive": 0.30, "max_exclusive": 0.50},
                {"label": "high", "min_inclusive": 0.50, "max_exclusive": 0.75},
                {"label": "critical", "min_inclusive": 0.75, "max_inclusive": 1.0},
            ]
        },
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "verification_minutes": 40,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert "does not satisfy the supported execution contract" in exc_info.value.detail


def test_lane_execution_rejects_runtime_inadmissible_profile(db):
    bindings = _seed_execution_bindings(
        db,
        lane_id="verification_burden",
        variable_names=[
            "implementation_minutes",
            "verification_minutes",
            "rework_minutes",
            "interruption_count",
            "downstream_fix_minutes",
            "uncertainty_band",
        ],
        parameter_payload={
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
        },
        threshold_payload=_generic_bands(),
        runtime_overrides={"rounding_mode": "half_up"},
    )
    _create_input_bundle(
        db,
        bindings,
        {
            "implementation_minutes": 30,
            "verification_minutes": 40,
            "rework_minutes": 10,
            "interruption_count": 2,
            "downstream_fix_minutes": 15,
            "uncertainty_band": "moderate",
        },
    )

    with pytest.raises(HTTPException) as exc_info:
        create_lane_execution(_execution_request(bindings), db)

    assert exc_info.value.status_code == 400
    assert "Phase 6 execution substrate requires the deterministic runtime policy set" in exc_info.value.detail
