from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.enums import (
    BudgetClass,
    CompatibilityResolutionState,
    IncidentClass,
    LaneFamily,
    OutputPosture,
    PriorityClass,
    ReplayState,
    ResultStatus,
    StaleState,
    TraceTier,
)
from app.schemas.governance import CompatibilityTuple


class EvaluationReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class IncidentSeverity(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class InputBundleCreate(BaseModel):
    input_bundle_id: str = Field(min_length=1, max_length=36)
    scope_id: str | None = Field(default=None, max_length=255)
    scope_version: int | None = Field(default=None, gt=0)
    provenance_class: str = Field(min_length=1, max_length=255)
    collection_timestamp: datetime
    admissibility_notes: str | None = None
    normalization_scope: str = Field(min_length=1, max_length=255)
    source_artifact_refs: list[dict[str, Any]] | dict[str, Any] = Field(default_factory=list)
    inline_values: dict[str, Any] = Field(default_factory=dict)
    frozen_flag: bool = True
    created_by: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_payload_presence(self) -> "InputBundleCreate":
        if not self.source_artifact_refs and not self.inline_values:
            raise ValueError("input bundle requires source_artifact_refs or inline_values.")
        return self


class InputBundleRead(EvaluationReadModel):
    input_bundle_id: str
    scope_id: str | None
    scope_version: int | None
    provenance_class: str
    collection_timestamp: datetime
    admissibility_notes: str | None
    normalization_scope: str
    deterministic_input_hash: str
    source_artifact_refs: list[dict[str, Any]] | dict[str, Any]
    inline_values: dict[str, Any]
    frozen_flag: bool
    created_at: datetime
    created_by: str | None


class CompatibilityBinding(BaseModel):
    variable_registry_id: str = Field(min_length=1, max_length=255)
    parameter_set_id: str = Field(min_length=1, max_length=255)
    threshold_set_id: str = Field(min_length=1, max_length=255)
    null_policy_bundle_id: str = Field(min_length=1, max_length=255)
    degraded_mode_policy_bundle_id: str = Field(min_length=1, max_length=255)
    prior_registry_id: str | None = Field(default=None, max_length=255)
    decay_registry_id: str | None = Field(default=None, max_length=255)
    compatibility_tuple: CompatibilityTuple

    def canonical_hash(self) -> str:
        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()


class LaneOutputValueCreate(BaseModel):
    output_field_name: str = Field(min_length=1, max_length=255)
    output_posture: OutputPosture
    numeric_value: float | None = None
    text_value: str | None = None
    enum_value: str | None = Field(default=None, max_length=255)
    value_range_class: str | None = Field(default=None, max_length=255)
    is_primary_output: bool = False

    @model_validator(mode="after")
    def validate_value_presence(self) -> "LaneOutputValueCreate":
        if self.numeric_value is None and self.text_value is None and self.enum_value is None:
            raise ValueError("output value requires numeric_value, text_value, or enum_value.")
        return self


class LaneOutputValueRead(EvaluationReadModel):
    id: str
    lane_evaluation_id: str
    output_field_name: str
    output_posture: OutputPosture
    numeric_value: float | None
    text_value: str | None
    enum_value: str | None
    value_range_class: str | None
    is_primary_output: bool
    created_at: datetime


class LaneFactorValueCreate(BaseModel):
    factor_name: str = Field(min_length=1, max_length=255)
    raw_value: float | None = None
    normalized_value: float | None = None
    weighted_value: float | None = None
    omitted_flag: bool = False
    omission_reason: str | None = None
    provenance_class: str | None = Field(default=None, max_length=255)
    volatility_class: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_factor_payload(self) -> "LaneFactorValueCreate":
        if self.omitted_flag:
            if not self.omission_reason:
                raise ValueError("omitted factors require omission_reason.")
            return self
        if self.raw_value is None:
            raise ValueError("non-omitted factors require raw_value.")
        return self


class LaneFactorValueRead(EvaluationReadModel):
    id: str
    lane_evaluation_id: str
    factor_name: str
    raw_value: float | None
    normalized_value: float | None
    weighted_value: float | None
    omitted_flag: bool
    omission_reason: str | None
    provenance_class: str | None
    volatility_class: str | None
    created_at: datetime


class TraceEventCreate(BaseModel):
    trace_step_order: int = Field(ge=0)
    trace_event_type: str = Field(min_length=1, max_length=255)
    trace_payload_ref: str = Field(min_length=1, max_length=1024)
    trace_summary: str = Field(min_length=1)


class TraceEventRead(EvaluationReadModel):
    id: str
    trace_bundle_id: str
    trace_step_order: int
    trace_event_type: str
    trace_payload_ref: str
    trace_summary: str
    created_at: datetime


class TraceBundleCreate(BaseModel):
    trace_bundle_id: str = Field(min_length=1, max_length=36)
    trace_tier: TraceTier
    trace_schema_version: int = Field(gt=0)
    reconstructable_flag: bool = False
    trace_events: list[TraceEventCreate] = Field(default_factory=list)


class TraceBundleRead(EvaluationReadModel):
    trace_bundle_id: str
    lane_evaluation_id: str
    trace_tier: TraceTier
    trace_schema_version: int
    trace_bundle_hash: str
    reconstructable_flag: bool
    created_at: datetime
    trace_events: list[TraceEventRead] = Field(default_factory=list)


class LaneEvaluationCreate(BaseModel):
    lane_evaluation_id: str = Field(min_length=1, max_length=36)
    supersedes_evaluation_id: str | None = Field(default=None, max_length=36)
    lane_id: str = Field(min_length=1, max_length=255)
    lane_spec_version: int = Field(gt=0)
    lane_family: LaneFamily
    execution_mode: str = Field(min_length=1, max_length=64)
    result_status: ResultStatus
    compatibility_resolution_state: CompatibilityResolutionState
    runtime_profile_id: str = Field(min_length=1, max_length=255)
    runtime_profile_version: int = Field(gt=0)
    input_bundle_id: str = Field(min_length=1, max_length=36)
    replay_state: ReplayState
    stale_state: StaleState
    raw_output_hash: str | None = Field(default=None, min_length=1, max_length=64)
    scope_id: str | None = Field(default=None, max_length=255)
    scope_version: int | None = Field(default=None, gt=0)
    compatibility_binding: CompatibilityBinding
    output_values: list[LaneOutputValueCreate] = Field(default_factory=list)
    factor_values: list[LaneFactorValueCreate] = Field(default_factory=list)
    trace_bundle: TraceBundleCreate
    created_by: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_summary_fields(self) -> "LaneEvaluationCreate":
        if self.raw_output_hash is None and self.result_status in {
            ResultStatus.COMPUTED_STRICT,
            ResultStatus.COMPUTED_DEGRADED,
        }:
            raise ValueError("computed evaluations require raw_output_hash.")
        return self


class LaneEvaluationSummaryRead(EvaluationReadModel):
    lane_evaluation_id: str
    lane_id: str
    lane_spec_version: int
    lane_family: LaneFamily
    execution_mode: str
    result_status: ResultStatus
    compatibility_resolution_state: CompatibilityResolutionState
    runtime_profile_id: str
    runtime_profile_version: int
    input_bundle_id: str
    trace_bundle_id: str
    replay_state: ReplayState
    stale_state: StaleState
    superseded_by_evaluation_id: str | None
    raw_output_hash: str | None
    compatibility_tuple_hash: str
    scope_id: str | None
    scope_version: int | None
    created_at: datetime
    created_by: str | None


class LaneEvaluationDetailRead(LaneEvaluationSummaryRead):
    compatibility_binding_payload: dict[str, Any]
    output_values: list[LaneOutputValueRead] = Field(default_factory=list)
    factor_values: list[LaneFactorValueRead] = Field(default_factory=list)
    trace_bundle: TraceBundleRead


class ReplayQueueEventCreate(BaseModel):
    replay_event_id: str = Field(min_length=1, max_length=36)
    triggering_reason: str = Field(min_length=1)
    priority_class: PriorityClass
    budget_class: BudgetClass
    operator_review_required_flag: bool = False
    status: str = Field(min_length=1, max_length=64)
    related_lane_id: str | None = Field(default=None, max_length=255)
    related_scope_id: str | None = Field(default=None, max_length=255)
    related_input_bundle_id: str | None = Field(default=None, max_length=36)
    related_lane_evaluation_id: str | None = Field(default=None, max_length=36)


class ReplayQueueEventRead(EvaluationReadModel):
    replay_event_id: str
    triggering_reason: str
    priority_class: PriorityClass
    budget_class: BudgetClass
    operator_review_required_flag: bool
    status: str
    related_lane_id: str | None
    related_scope_id: str | None
    related_input_bundle_id: str | None
    related_lane_evaluation_id: str | None
    created_at: datetime


class IncidentRecordCreate(BaseModel):
    incident_id: str = Field(min_length=1, max_length=36)
    incident_class: IncidentClass
    severity: IncidentSeverity
    affected_scope_id: str | None = Field(default=None, max_length=255)
    affected_lane_id: str | None = Field(default=None, max_length=255)
    summary: str = Field(min_length=1)
    canonical_truth_impact_flag: bool = False
    related_lane_evaluation_id: str | None = Field(default=None, max_length=36)


class IncidentRecordRead(EvaluationReadModel):
    incident_id: str
    incident_class: IncidentClass
    severity: IncidentSeverity
    affected_scope_id: str | None
    affected_lane_id: str | None
    summary: str
    canonical_truth_impact_flag: bool
    related_lane_evaluation_id: str | None
    created_at: datetime
