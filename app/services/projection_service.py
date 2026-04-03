from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.schemas.projection import (
    LaneEvaluationDetailModel,
    LaneEvaluationSummaryModel,
    LaneFactorInspectionModel,
    LaneFactorProjectionItem,
    LaneReplayDiagnosticModel,
    LaneTraceInspectionModel,
    LaneTraceProjectionItem,
)
from app.services import evaluation_service, lifecycle_service, runtime_admission_service
from app.services.registry_service import GovernanceValidationError


def _projection_metadata(detail: Any) -> dict[str, Any]:
    payload = detail.compatibility_binding_payload or {}
    tuple_payload = payload.get("compatibility_tuple")
    if not isinstance(tuple_payload, dict):
        raise GovernanceValidationError(
            "projection composition requires a persisted compatibility tuple payload."
        )

    projection_schema_version = tuple_payload.get("projection_schema_version")
    if not isinstance(projection_schema_version, int) or projection_schema_version <= 0:
        raise GovernanceValidationError(
            "projection composition requires a positive projection_schema_version in the compatibility tuple."
        )

    compatibility_tuple_hash = getattr(detail, "compatibility_tuple_hash", None)
    if not compatibility_tuple_hash:
        raise GovernanceValidationError(
            "projection composition requires source_compatibility_tuple_hash."
        )

    return {
        "projection_schema_version": projection_schema_version,
        "source_evaluation_id": detail.lane_evaluation_id,
        "source_compatibility_tuple_hash": compatibility_tuple_hash,
    }


def get_lane_evaluation_summary_model(
    db: Session,
    lane_evaluation_id: str,
) -> LaneEvaluationSummaryModel:
    detail = evaluation_service.get_lane_evaluation_detail(db, lane_evaluation_id)
    metadata = _projection_metadata(detail)
    return LaneEvaluationSummaryModel(
        lane_evaluation_id=detail.lane_evaluation_id,
        lane_id=detail.lane_id,
        lane_spec_version=detail.lane_spec_version,
        evaluation_status=detail.result_status,
        result_status=detail.result_status,
        compatibility_resolution_state=detail.compatibility_resolution_state,
        deterministic_admission_state=detail.deterministic_admission_state,
        runtime_profile_id=detail.runtime_profile_id,
        replay_state=detail.replay_state,
        stale_state=detail.stale_state,
        recomputation_action=detail.recomputation_action,
        superseded_by_evaluation_id=detail.superseded_by_evaluation_id,
        created_at=detail.created_at,
        **metadata,
    )


def get_lane_evaluation_detail_model(
    db: Session,
    lane_evaluation_id: str,
) -> LaneEvaluationDetailModel:
    detail = evaluation_service.get_lane_evaluation_detail(db, lane_evaluation_id)
    metadata = _projection_metadata(detail)
    return LaneEvaluationDetailModel(
        lane_evaluation_id=detail.lane_evaluation_id,
        lane_id=detail.lane_id,
        lane_spec_version=detail.lane_spec_version,
        evaluation_status=detail.result_status,
        result_status=detail.result_status,
        compatibility_resolution_state=detail.compatibility_resolution_state,
        deterministic_admission_state=detail.deterministic_admission_state,
        runtime_profile_id=detail.runtime_profile_id,
        replay_state=detail.replay_state,
        stale_state=detail.stale_state,
        recomputation_action=detail.recomputation_action,
        superseded_by_evaluation_id=detail.superseded_by_evaluation_id,
        created_at=detail.created_at,
        input_bundle_id=detail.input_bundle_id,
        trace_bundle_id=detail.trace_bundle_id,
        trace_tier=detail.trace_bundle.trace_tier,
        runtime_validation_reason_code=detail.runtime_validation_reason_code,
        runtime_validation_reason_detail=detail.runtime_validation_reason_detail,
        determinism_certificate_ref=detail.determinism_certificate_ref,
        bit_exact_eligible=detail.bit_exact_eligible,
        lifecycle_reason_code=detail.lifecycle_reason_code,
        lifecycle_reason_detail=detail.lifecycle_reason_detail,
        supersession_reason=detail.supersession_reason,
        supersession_timestamp=detail.supersession_timestamp,
        supersession_class=detail.supersession_class,
        source_trace_bundle_id=detail.trace_bundle.trace_bundle_id,
        **metadata,
    )


def get_lane_factor_inspection_model(
    db: Session,
    lane_evaluation_id: str,
) -> LaneFactorInspectionModel:
    detail = evaluation_service.get_lane_evaluation_detail(db, lane_evaluation_id)
    metadata = _projection_metadata(detail)
    factors = [
        LaneFactorProjectionItem(
            factor_name=item.factor_name,
            raw_value=item.raw_value,
            normalized_value=item.normalized_value,
            weighted_value=item.weighted_value,
            omitted_flag=item.omitted_flag,
            omission_reason=item.omission_reason,
            provenance_class=item.provenance_class,
            volatility_class=item.volatility_class,
        )
        for item in detail.factor_values
    ]
    return LaneFactorInspectionModel(
        lane_evaluation_id=detail.lane_evaluation_id,
        lane_id=detail.lane_id,
        result_status=detail.result_status,
        deterministic_admission_state=detail.deterministic_admission_state,
        replay_state=detail.replay_state,
        stale_state=detail.stale_state,
        factors=factors,
        **metadata,
    )


def get_lane_trace_inspection_model(
    db: Session,
    lane_evaluation_id: str,
) -> LaneTraceInspectionModel:
    detail = evaluation_service.get_lane_evaluation_detail(db, lane_evaluation_id)
    metadata = _projection_metadata(detail)
    trace_items = [
        LaneTraceProjectionItem(
            trace_step_order=item.trace_step_order,
            trace_event_type=item.trace_event_type,
            trace_payload_ref=item.trace_payload_ref,
            trace_summary=item.trace_summary,
        )
        for item in detail.trace_bundle.trace_events
    ]
    return LaneTraceInspectionModel(
        trace_bundle_id=detail.trace_bundle.trace_bundle_id,
        lane_evaluation_id=detail.lane_evaluation_id,
        lane_id=detail.lane_id,
        result_status=detail.result_status,
        deterministic_admission_state=detail.deterministic_admission_state,
        trace_tier=detail.trace_bundle.trace_tier,
        trace_events=trace_items,
        source_trace_bundle_id=detail.trace_bundle.trace_bundle_id,
        **metadata,
    )


def get_lane_replay_diagnostic_model(
    db: Session,
    lane_evaluation_id: str,
) -> LaneReplayDiagnosticModel:
    detail = evaluation_service.get_lane_evaluation_detail(db, lane_evaluation_id)
    metadata = _projection_metadata(detail)
    lifecycle = lifecycle_service.get_lane_evaluation_lifecycle(db, lane_evaluation_id)
    runtime_admission = runtime_admission_service.get_runtime_admission(db, lane_evaluation_id)
    return LaneReplayDiagnosticModel(
        lane_evaluation_id=detail.lane_evaluation_id,
        lane_id=detail.lane_id,
        result_status=detail.result_status,
        compatibility_resolution_state=detail.compatibility_resolution_state,
        deterministic_admission_state=runtime_admission.deterministic_admission_state,
        replay_state=lifecycle.replay_state,
        stale_state=lifecycle.stale_state,
        recomputation_action=lifecycle.recomputation_action,
        lifecycle_reason_code=lifecycle.lifecycle_reason_code,
        lifecycle_reason_detail=lifecycle.lifecycle_reason_detail,
        runtime_validation_reason_code=runtime_admission.runtime_validation_reason_code,
        runtime_validation_reason_detail=runtime_admission.runtime_validation_reason_detail,
        determinism_certificate_ref=runtime_admission.determinism_certificate_ref,
        bit_exact_eligible=runtime_admission.bit_exact_eligible,
        superseded_by_evaluation_id=detail.superseded_by_evaluation_id,
        **metadata,
    )
