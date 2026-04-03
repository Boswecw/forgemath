from __future__ import annotations

from decimal import Decimal
from datetime import datetime
from enum import StrEnum
from hashlib import sha256
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.enums import (
    BudgetClass,
    CompatibilityResolutionState,
    DeterministicAdmissionState,
    IncidentClass,
    LaneFamily,
    OutputPosture,
    PriorityClass,
    RecomputationAction,
    ReplayState,
    ResultStatus,
    StaleState,
    SupersessionClass,
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
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

    variable_registry_id: str = Field(min_length=1, max_length=255)
    parameter_set_id: str = Field(min_length=1, max_length=255)
    threshold_set_id: str = Field(min_length=1, max_length=255)
    null_policy_bundle_id: str = Field(min_length=1, max_length=255)
    degraded_mode_policy_bundle_id: str = Field(min_length=1, max_length=255)
    prior_registry_id: str | None = Field(default=None, max_length=255)
    decay_registry_id: str | None = Field(default=None, max_length=255)
    compatibility_tuple: CompatibilityTuple

    @model_validator(mode="after")
    def validate_optional_registry_pairs(self) -> "CompatibilityBinding":
        optional_pairs = (
            (
                self.prior_registry_id,
                self.compatibility_tuple.prior_registry_version,
                "prior_registry",
            ),
            (
                self.decay_registry_id,
                self.compatibility_tuple.decay_registry_version,
                "decay_registry",
            ),
        )
        for registry_id, registry_version, label in optional_pairs:
            if (registry_id is None) != (registry_version is None):
                raise ValueError(f"{label}_id and {label}_version must be provided together.")
        return self

    def canonical_hash(self) -> str:
        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()


class LaneOutputValueCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output_field_name: str = Field(min_length=1, max_length=255)
    output_posture: OutputPosture
    numeric_value: Decimal | None = None
    text_value: str | None = None
    enum_value: str | None = Field(default=None, max_length=255)
    value_range_class: str | None = Field(default=None, max_length=255)
    is_primary_output: bool = False

    @model_validator(mode="after")
    def validate_value_presence(self) -> "LaneOutputValueCreate":
        populated_values = sum(
            value is not None for value in (self.numeric_value, self.text_value, self.enum_value)
        )
        if populated_values != 1:
            raise ValueError("output value requires exactly one of numeric_value, text_value, or enum_value.")
        if self.output_posture == OutputPosture.RAW:
            if self.numeric_value is None:
                raise ValueError("raw output posture requires numeric_value.")
        elif self.numeric_value is not None:
            raise ValueError("non-raw output posture may not persist numeric_value.")
        return self


class LaneOutputValueRead(EvaluationReadModel):
    id: str
    lane_evaluation_id: str
    output_field_name: str
    output_posture: OutputPosture
    numeric_value: Decimal | None
    text_value: str | None
    enum_value: str | None
    value_range_class: str | None
    is_primary_output: bool
    created_at: datetime


class LaneFactorValueCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    factor_name: str = Field(min_length=1, max_length=255)
    raw_value: Decimal | None = None
    normalized_value: Decimal | None = None
    weighted_value: Decimal | None = None
    omitted_flag: bool = False
    omission_reason: str | None = None
    provenance_class: str | None = Field(default=None, max_length=255)
    volatility_class: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_factor_payload(self) -> "LaneFactorValueCreate":
        if self.omitted_flag:
            if not self.omission_reason:
                raise ValueError("omitted factors require omission_reason.")
            if any(value is not None for value in (self.raw_value, self.normalized_value, self.weighted_value)):
                raise ValueError("omitted factors may not persist raw_value, normalized_value, or weighted_value.")
            return self
        if self.omission_reason is not None:
            raise ValueError("non-omitted factors may not persist omission_reason.")
        missing = [
            field_name
            for field_name, value in (
                ("raw_value", self.raw_value),
                ("normalized_value", self.normalized_value),
                ("weighted_value", self.weighted_value),
                ("provenance_class", self.provenance_class),
                ("volatility_class", self.volatility_class),
            )
            if value is None
        ]
        if missing:
            raise ValueError(
                "non-omitted factors require "
                + ", ".join(missing)
                + "."
            )
        return self


class LaneFactorValueRead(EvaluationReadModel):
    id: str
    lane_evaluation_id: str
    factor_name: str
    raw_value: Decimal | None
    normalized_value: Decimal | None
    weighted_value: Decimal | None
    omitted_flag: bool
    omission_reason: str | None
    provenance_class: str | None
    volatility_class: str | None
    created_at: datetime


class TraceEventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

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
    model_config = ConfigDict(extra="forbid")

    lane_evaluation_id: str = Field(min_length=1, max_length=36)
    supersedes_evaluation_id: str | None = Field(default=None, max_length=36)
    supersession_class: SupersessionClass | None = None
    supersession_reason: str | None = None
    supersession_timestamp: datetime | None = None
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
    recomputation_action: RecomputationAction
    lifecycle_reason_code: str = Field(min_length=1, max_length=255)
    lifecycle_reason_detail: str | None = None
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
        has_supersession_target = self.supersedes_evaluation_id is not None
        has_supersession_metadata = any(
            item is not None
            for item in (
                self.supersession_class,
                self.supersession_reason,
                self.supersession_timestamp,
            )
        )
        if has_supersession_target and not all(
            item is not None
            for item in (
                self.supersession_class,
                self.supersession_reason,
                self.supersession_timestamp,
            )
        ):
            raise ValueError(
                "superseding evaluation creation requires supersession_class, supersession_reason, "
                "and supersession_timestamp."
            )
        if not has_supersession_target and has_supersession_metadata:
            raise ValueError("supersession metadata is only valid when supersedes_evaluation_id is provided.")
        return self


class ManualLaneEvaluationCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    lane_evaluation_id: str = Field(min_length=1, max_length=36)
    supersedes_evaluation_id: str | None = Field(default=None, max_length=36)
    supersession_class: SupersessionClass | None = None
    supersession_reason: str | None = None
    supersession_timestamp: datetime | None = None
    lane_id: str = Field(min_length=1, max_length=255)
    lane_spec_version: int = Field(gt=0)
    lane_family: LaneFamily
    result_status: ResultStatus
    compatibility_resolution_state: CompatibilityResolutionState
    runtime_profile_id: str = Field(min_length=1, max_length=255)
    runtime_profile_version: int = Field(gt=0)
    input_bundle_id: str = Field(min_length=1, max_length=36)
    replay_state: ReplayState
    stale_state: StaleState
    recomputation_action: RecomputationAction
    lifecycle_reason_code: str = Field(min_length=1, max_length=255)
    lifecycle_reason_detail: str | None = None
    scope_id: str | None = Field(default=None, max_length=255)
    scope_version: int | None = Field(default=None, gt=0)
    compatibility_binding: CompatibilityBinding
    trace_bundle: TraceBundleCreate
    created_by: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_manual_ingest_posture(self) -> "ManualLaneEvaluationCreate":
        if self.result_status not in {
            ResultStatus.BLOCKED,
            ResultStatus.AUDIT_ONLY,
            ResultStatus.INVALID,
        }:
            raise ValueError(
                "manual lane evaluation ingestion may only persist blocked, audit_only, or invalid results."
            )
        if self.replay_state in {
            ReplayState.REPLAY_SAFE,
            ReplayState.REPLAY_SAFE_WITH_BOUNDED_MIGRATION,
        }:
            raise ValueError(
                "manual lane evaluation ingestion may not claim replay_safe or replay_safe_with_bounded_migration."
            )
        has_supersession_target = self.supersedes_evaluation_id is not None
        has_supersession_metadata = any(
            item is not None
            for item in (
                self.supersession_class,
                self.supersession_reason,
                self.supersession_timestamp,
            )
        )
        if has_supersession_target and not all(
            item is not None
            for item in (
                self.supersession_class,
                self.supersession_reason,
                self.supersession_timestamp,
            )
        ):
            raise ValueError(
                "manual supersession requires supersession_class, supersession_reason, and supersession_timestamp."
            )
        if not has_supersession_target and has_supersession_metadata:
            raise ValueError("supersession metadata is only valid when supersedes_evaluation_id is provided.")
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
    recomputation_action: RecomputationAction
    deterministic_admission_state: DeterministicAdmissionState
    runtime_validation_reason_code: str
    runtime_validation_reason_detail: str | None
    determinism_certificate_ref: str | None
    bit_exact_eligible: bool
    superseded_by_evaluation_id: str | None
    supersession_reason: str | None
    supersession_timestamp: datetime | None
    supersession_class: SupersessionClass | None
    lifecycle_reason_code: str
    lifecycle_reason_detail: str | None
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


class RuntimeAdmissionEventRead(EvaluationReadModel):
    event_id: str
    lane_evaluation_id: str
    runtime_profile_id: str
    runtime_profile_version: int
    admission_outcome: DeterministicAdmissionState
    reason_code: str
    reason_detail: str | None
    determinism_certificate_ref: str | None
    bit_exact_eligible: bool
    created_at: datetime
    created_by: str | None


class LaneEvaluationRuntimeAdmissionRead(EvaluationReadModel):
    lane_evaluation_id: str
    runtime_profile_id: str
    runtime_profile_version: int
    deterministic_admission_state: DeterministicAdmissionState
    runtime_validation_reason_code: str
    runtime_validation_reason_detail: str | None
    determinism_certificate_ref: str | None
    bit_exact_eligible: bool
    current_runtime_profile_present: bool
    current_runtime_profile_active: bool
    current_runtime_profile_non_deterministic: bool | None
    runtime_admission_events: list[RuntimeAdmissionEventRead] = Field(default_factory=list)


class LaneEvaluationLifecycleEventRead(EvaluationReadModel):
    event_id: str
    lane_evaluation_id: str
    event_type: str
    prior_replay_state: ReplayState | None
    new_replay_state: ReplayState
    prior_stale_state: StaleState | None
    new_stale_state: StaleState
    prior_recomputation_action: RecomputationAction | None
    new_recomputation_action: RecomputationAction
    reason_code: str
    reason_detail: str | None
    related_evaluation_id: str | None
    created_at: datetime
    created_by: str | None


class LaneEvaluationLifecycleRead(EvaluationReadModel):
    lane_evaluation_id: str
    lane_id: str
    result_status: ResultStatus
    compatibility_resolution_state: CompatibilityResolutionState
    replay_state: ReplayState
    stale_state: StaleState
    recomputation_action: RecomputationAction
    superseded_by_evaluation_id: str | None
    supersession_reason: str | None
    supersession_timestamp: datetime | None
    supersession_class: SupersessionClass | None
    lifecycle_reason_code: str
    lifecycle_reason_detail: str | None
    created_at: datetime
    created_by: str | None
    lifecycle_events: list[LaneEvaluationLifecycleEventRead] = Field(default_factory=list)


class LaneEvaluationLifecycleTransitionCreate(BaseModel):
    replay_state: ReplayState
    stale_state: StaleState
    recomputation_action: RecomputationAction
    lifecycle_reason_code: str = Field(min_length=1, max_length=255)
    lifecycle_reason_detail: str | None = None
    related_evaluation_id: str | None = Field(default=None, max_length=36)
    supersession_class: SupersessionClass | None = None
    supersession_reason: str | None = None
    supersession_timestamp: datetime | None = None
    input_bundle_invalidated: bool = False
    created_by: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_supersession_bundle(self) -> "LaneEvaluationLifecycleTransitionCreate":
        has_related = self.related_evaluation_id is not None
        has_supersession_metadata = any(
            item is not None
            for item in (
                self.supersession_class,
                self.supersession_reason,
                self.supersession_timestamp,
            )
        )
        if has_related and not all(
            item is not None
            for item in (
                self.supersession_class,
                self.supersession_reason,
                self.supersession_timestamp,
            )
        ):
            raise ValueError(
                "supersession transitions require supersession_class, supersession_reason, "
                "and supersession_timestamp."
            )
        if not has_related and has_supersession_metadata:
            raise ValueError("supersession metadata requires related_evaluation_id.")
        return self


class LaneEvaluationLineageRead(EvaluationReadModel):
    anchor_lane_evaluation_id: str
    lane_id: str
    lineage: list[LaneEvaluationSummaryRead] = Field(default_factory=list)


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
