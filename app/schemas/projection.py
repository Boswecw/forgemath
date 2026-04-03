from __future__ import annotations

from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import (
    CompatibilityResolutionState,
    DeterministicAdmissionState,
    ReplayState,
    RecomputationAction,
    ResultStatus,
    StaleState,
    SupersessionClass,
    TraceTier,
)


class ProjectionReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectionMetadata(ProjectionReadModel):
    projection_schema_version: int = Field(gt=0)
    source_evaluation_id: str
    source_compatibility_tuple_hash: str


class LaneEvaluationSummaryModel(ProjectionMetadata):
    lane_evaluation_id: str
    lane_id: str
    lane_spec_version: int
    evaluation_status: ResultStatus
    result_status: ResultStatus
    compatibility_resolution_state: CompatibilityResolutionState
    deterministic_admission_state: DeterministicAdmissionState
    runtime_profile_id: str
    replay_state: ReplayState
    stale_state: StaleState
    recomputation_action: RecomputationAction
    superseded_by_evaluation_id: str | None
    created_at: datetime


class LaneEvaluationDetailModel(LaneEvaluationSummaryModel):
    input_bundle_id: str
    trace_bundle_id: str
    trace_tier: TraceTier
    runtime_validation_reason_code: str
    runtime_validation_reason_detail: str | None
    determinism_certificate_ref: str | None
    bit_exact_eligible: bool
    lifecycle_reason_code: str
    lifecycle_reason_detail: str | None
    supersession_reason: str | None
    supersession_timestamp: datetime | None
    supersession_class: SupersessionClass | None
    source_trace_bundle_id: str


class LaneFactorProjectionItem(ProjectionReadModel):
    factor_name: str
    raw_value: Decimal | None
    normalized_value: Decimal | None
    weighted_value: Decimal | None
    omitted_flag: bool
    omission_reason: str | None
    provenance_class: str | None
    volatility_class: str | None


class LaneFactorInspectionModel(ProjectionMetadata):
    lane_evaluation_id: str
    lane_id: str
    result_status: ResultStatus
    deterministic_admission_state: DeterministicAdmissionState
    replay_state: ReplayState
    stale_state: StaleState
    factors: list[LaneFactorProjectionItem] = Field(default_factory=list)


class LaneTraceProjectionItem(ProjectionReadModel):
    trace_step_order: int
    trace_event_type: str
    trace_payload_ref: str
    trace_summary: str


class LaneTraceInspectionModel(ProjectionMetadata):
    trace_bundle_id: str
    lane_evaluation_id: str
    lane_id: str
    result_status: ResultStatus
    deterministic_admission_state: DeterministicAdmissionState
    trace_tier: TraceTier
    trace_events: list[LaneTraceProjectionItem] = Field(default_factory=list)
    source_trace_bundle_id: str


class LaneReplayDiagnosticModel(ProjectionMetadata):
    lane_evaluation_id: str
    lane_id: str
    result_status: ResultStatus
    compatibility_resolution_state: CompatibilityResolutionState
    deterministic_admission_state: DeterministicAdmissionState
    replay_state: ReplayState
    stale_state: StaleState
    recomputation_action: RecomputationAction
    lifecycle_reason_code: str
    lifecycle_reason_detail: str | None
    runtime_validation_reason_code: str
    runtime_validation_reason_detail: str | None
    determinism_certificate_ref: str | None
    bit_exact_eligible: bool
    superseded_by_evaluation_id: str | None
