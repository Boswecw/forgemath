from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
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
    enum_values,
)
from app.models.governance import ImmutablePersistedMixin, new_uuid, utcnow


def _sql_in(enum_cls: type) -> str:
    return "(" + ", ".join(f"'{value}'" for value in enum_values(enum_cls)) + ")"


class InputBundle(ImmutablePersistedMixin, Base):
    __tablename__ = "forgemath_input_bundles"

    input_bundle_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    scope_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    scope_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provenance_class: Mapped[str] = mapped_column(String(255), nullable=False)
    collection_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    admissibility_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalization_scope: Mapped[str] = mapped_column(String(255), nullable=False)
    deterministic_input_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    source_artifact_refs: Mapped[list[dict[str, Any]] | dict[str, Any]] = mapped_column(JSON, nullable=False)
    inline_values: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    frozen_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint(
            "scope_version IS NULL OR scope_version > 0",
            name="ck_forgemath_input_bundles_scope_version_positive",
        ),
    )


class LaneEvaluation(ImmutablePersistedMixin, Base):
    __tablename__ = "forgemath_lane_evaluations"

    lane_evaluation_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    lane_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    lane_spec_version: Mapped[int] = mapped_column(Integer, nullable=False)
    lane_family: Mapped[str] = mapped_column(String(32), nullable=False)
    execution_mode: Mapped[str] = mapped_column(String(64), nullable=False)
    result_status: Mapped[str] = mapped_column(String(32), nullable=False)
    compatibility_resolution_state: Mapped[str] = mapped_column(String(48), nullable=False)
    runtime_profile_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    runtime_profile_version: Mapped[int] = mapped_column(Integer, nullable=False)
    input_bundle_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("forgemath_input_bundles.input_bundle_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    trace_bundle_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True)
    replay_state: Mapped[str] = mapped_column(String(48), nullable=False)
    stale_state: Mapped[str] = mapped_column(String(48), nullable=False)
    superseded_by_evaluation_id: Mapped[str | None] = mapped_column(String(36), nullable=True, unique=True)
    raw_output_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    compatibility_tuple_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    compatibility_binding_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    scope_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    scope_version: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    __table_args__ = (
        CheckConstraint("lane_spec_version > 0", name="ck_forgemath_lane_evaluations_lane_spec_version_positive"),
        CheckConstraint(
            "runtime_profile_version > 0",
            name="ck_forgemath_lane_evaluations_runtime_profile_version_positive",
        ),
        CheckConstraint(
            "scope_version IS NULL OR scope_version > 0",
            name="ck_forgemath_lane_evaluations_scope_version_positive",
        ),
        CheckConstraint(
            f"lane_family IN {_sql_in(LaneFamily)}",
            name="ck_forgemath_lane_evaluations_lane_family",
        ),
        CheckConstraint(
            f"result_status IN {_sql_in(ResultStatus)}",
            name="ck_forgemath_lane_evaluations_result_status",
        ),
        CheckConstraint(
            f"compatibility_resolution_state IN {_sql_in(CompatibilityResolutionState)}",
            name="ck_forgemath_lane_evaluations_compatibility_resolution_state",
        ),
        CheckConstraint(
            f"replay_state IN {_sql_in(ReplayState)}",
            name="ck_forgemath_lane_evaluations_replay_state",
        ),
        CheckConstraint(
            f"stale_state IN {_sql_in(StaleState)}",
            name="ck_forgemath_lane_evaluations_stale_state",
        ),
    )

    @classmethod
    def lifecycle_mutable_fields(cls) -> set[str]:
        return {"superseded_by_evaluation_id"}


class LaneOutputValue(ImmutablePersistedMixin, Base):
    __tablename__ = "forgemath_lane_output_values"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    lane_evaluation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("forgemath_lane_evaluations.lane_evaluation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    output_field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    output_posture: Mapped[str] = mapped_column(String(32), nullable=False)
    numeric_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    text_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    enum_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    value_range_class: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_primary_output: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        CheckConstraint(
            f"output_posture IN {_sql_in(OutputPosture)}",
            name="ck_forgemath_lane_output_values_output_posture",
        ),
    )


class LaneFactorValue(ImmutablePersistedMixin, Base):
    __tablename__ = "forgemath_lane_factor_values"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    lane_evaluation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("forgemath_lane_evaluations.lane_evaluation_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    factor_name: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    normalized_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    weighted_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    omitted_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    omission_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_class: Mapped[str | None] = mapped_column(String(255), nullable=True)
    volatility_class: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)


class TraceBundle(ImmutablePersistedMixin, Base):
    __tablename__ = "forgemath_trace_bundles"

    trace_bundle_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    lane_evaluation_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("forgemath_lane_evaluations.lane_evaluation_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    trace_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    trace_schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    trace_bundle_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    reconstructable_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        CheckConstraint("trace_schema_version > 0", name="ck_forgemath_trace_bundles_trace_schema_version_positive"),
        CheckConstraint(
            f"trace_tier IN {_sql_in(TraceTier)}",
            name="ck_forgemath_trace_bundles_trace_tier",
        ),
    )


class TraceEvent(ImmutablePersistedMixin, Base):
    __tablename__ = "forgemath_trace_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    trace_bundle_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("forgemath_trace_bundles.trace_bundle_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    trace_step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    trace_event_type: Mapped[str] = mapped_column(String(255), nullable=False)
    trace_payload_ref: Mapped[str] = mapped_column(String(1024), nullable=False)
    trace_summary: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint(
            "trace_bundle_id",
            "trace_step_order",
            name="uq_forgemath_trace_events_trace_bundle_order",
        ),
        CheckConstraint("trace_step_order >= 0", name="ck_forgemath_trace_events_trace_step_order_nonnegative"),
    )


class ReplayQueueEvent(ImmutablePersistedMixin, Base):
    __tablename__ = "forgemath_replay_queue_events"

    replay_event_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    triggering_reason: Mapped[str] = mapped_column(Text, nullable=False)
    priority_class: Mapped[str] = mapped_column(String(32), nullable=False)
    budget_class: Mapped[str] = mapped_column(String(48), nullable=False)
    operator_review_required_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    related_lane_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    related_scope_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    related_input_bundle_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("forgemath_input_bundles.input_bundle_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    related_lane_evaluation_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("forgemath_lane_evaluations.lane_evaluation_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        CheckConstraint(
            f"priority_class IN {_sql_in(PriorityClass)}",
            name="ck_forgemath_replay_queue_events_priority_class",
        ),
        CheckConstraint(
            f"budget_class IN {_sql_in(BudgetClass)}",
            name="ck_forgemath_replay_queue_events_budget_class",
        ),
    )


class IncidentRecord(ImmutablePersistedMixin, Base):
    __tablename__ = "forgemath_incident_records"

    incident_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    incident_class: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(64), nullable=False)
    affected_scope_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    affected_lane_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_truth_impact_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    related_lane_evaluation_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("forgemath_lane_evaluations.lane_evaluation_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        CheckConstraint(
            f"incident_class IN {_sql_in(IncidentClass)}",
            name="ck_forgemath_incident_records_incident_class",
        ),
    )
