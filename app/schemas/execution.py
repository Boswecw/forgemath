from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.enums import (
    CompatibilityResolutionState,
    DeterministicAdmissionState,
    ReplayState,
    ResultStatus,
    StaleState,
    SupersessionClass,
)
from app.schemas.evaluation import CompatibilityBinding, LaneEvaluationDetailRead


class ExecutionReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class LaneExecutionCreate(BaseModel):
    lane_evaluation_id: str | None = Field(default=None, min_length=1, max_length=36)
    supersedes_evaluation_id: str | None = Field(default=None, min_length=1, max_length=36)
    supersession_class: SupersessionClass | None = None
    supersession_reason: str | None = None
    supersession_timestamp: datetime | None = None
    lane_id: str = Field(min_length=1, max_length=255)
    lane_spec_version: int = Field(gt=0)
    compatibility_resolution_state: CompatibilityResolutionState
    runtime_profile_id: str = Field(min_length=1, max_length=255)
    runtime_profile_version: int = Field(gt=0)
    input_bundle_id: str = Field(min_length=1, max_length=36)
    execution_mode: str = Field(min_length=1, max_length=64)
    scope_id: str | None = Field(default=None, max_length=255)
    scope_version: int | None = Field(default=None, gt=0)
    compatibility_binding: CompatibilityBinding
    created_by: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_execution_posture(self) -> "LaneExecutionCreate":
        if self.scope_id is not None and self.scope_version is None:
            raise ValueError("scope_version is required when scope_id is provided.")
        if self.compatibility_resolution_state not in {
            CompatibilityResolutionState.RESOLVED_HARD_COMPATIBLE,
            CompatibilityResolutionState.RESOLVED_WITH_BOUNDED_MIGRATION,
        }:
            raise ValueError(
                "canonical lane execution requires compatibility_resolution_state to be "
                "resolved_hard_compatible or resolved_with_bounded_migration."
            )
        if self.compatibility_binding.compatibility_tuple.lane_spec_version != self.lane_spec_version:
            raise ValueError(
                "compatibility tuple lane_spec_version must match the execution request lane_spec_version."
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
                "execution supersession requires supersession_class, supersession_reason, and supersession_timestamp."
            )
        if not has_supersession_target and has_supersession_metadata:
            raise ValueError("supersession metadata is only valid when supersedes_evaluation_id is provided.")
        return self


class LaneExecutionResultRead(ExecutionReadModel):
    lane_evaluation_id: str
    lane_id: str
    result_status: ResultStatus
    compatibility_resolution_state: CompatibilityResolutionState
    deterministic_admission_state: DeterministicAdmissionState
    replay_state: ReplayState
    stale_state: StaleState
    trace_bundle_id: str
    raw_output_hash: str | None
    created_at: datetime
    evaluation: LaneEvaluationDetailRead
