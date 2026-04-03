from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import (
    CompatibilityResolutionState,
    LaneFamily,
    OutputPosture,
    PolicyBundleKind,
    ReplayState,
    ResultStatus,
    TraceTier,
)
from app.models.evaluation import (
    IncidentRecord,
    InputBundle,
    LaneEvaluation,
    LaneFactorValue,
    LaneOutputValue,
    ReplayQueueEvent,
    TraceBundle,
    TraceEvent,
)
from app.models.governance import PolicyBundle
from app.schemas.evaluation import (
    IncidentRecordCreate,
    InputBundleCreate,
    LaneEvaluationCreate,
    LaneEvaluationDetailRead,
    LaneFactorValueRead,
    LaneOutputValueRead,
    LaneEvaluationSummaryRead,
    ReplayQueueEventCreate,
    TraceBundleRead,
    TraceEventRead,
)
from app.services.registry_service import (
    GovernanceConflictError,
    GovernanceNotFoundError,
    GovernanceValidationError,
    _clean_identifier,
    _clean_optional_text,
    get_lane_spec,
    get_parameter_set,
    get_policy_bundle,
    get_runtime_profile,
    get_scope_registry,
    get_threshold_set,
    get_variable_registry,
)


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash_payload(payload: Any) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


TRACE_TIER_RANK = {
    TraceTier.TIER_1_FULL.value: 1,
    TraceTier.TIER_2_STANDARD.value: 2,
    TraceTier.TIER_3_RECONSTRUCTION.value: 3,
}


def _get_or_404(db: Session, model: type, pk_field: str, pk_value: str):
    record = db.scalar(select(model).where(getattr(model, pk_field) == pk_value))
    if record is None:
        raise GovernanceNotFoundError(f"{model.__name__} {pk_value} was not found.")
    return record


def _ensure_unique_id(db: Session, model: type, pk_field: str, pk_value: str) -> None:
    existing = db.scalar(select(model).where(getattr(model, pk_field) == pk_value))
    if existing is not None:
        raise GovernanceConflictError(f"{model.__name__} {pk_value} already exists.")


def _require_active_binding(record: Any, label: str) -> None:
    if getattr(record, "superseded_at", None) is not None:
        raise GovernanceValidationError(f"{label} must be active for canonical evaluation writes.")


def _validate_lane_spec(record: Any, lane_id: str, lane_family: str) -> None:
    _require_active_binding(record, f"LaneSpec {lane_id} version {record.version}")
    if not record.is_admissible:
        raise GovernanceValidationError(
            f"LaneSpec {lane_id} version {record.version} is not admissible."
        )
    if record.lane_family != lane_family:
        raise GovernanceValidationError("lane_family must match the bound lane spec.")


def _validate_runtime_profile(record: Any, runtime_profile_id: str) -> None:
    _require_active_binding(record, f"RuntimeProfile {runtime_profile_id} version {record.version}")
    if record.non_determinism_allowed_flag:
        raise GovernanceValidationError(
            "Canonical evaluations require a deterministic runtime profile."
        )


def _validate_policy_bundle_kind(record: PolicyBundle, expected_kind: PolicyBundleKind, label: str) -> None:
    _require_active_binding(record, label)
    if record.policy_kind != expected_kind.value:
        raise GovernanceValidationError(f"{label} must have policy_kind={expected_kind.value}.")


def _required_trace_tier(lane_family: str, result_status: str, lane_spec_trace_tier: str) -> str:
    if lane_family == LaneFamily.HYBRID_GATE.value:
        return TraceTier.TIER_1_FULL.value
    if result_status in {
        ResultStatus.COMPUTED_STRICT.value,
        ResultStatus.COMPUTED_DEGRADED.value,
        ResultStatus.BLOCKED.value,
    }:
        return TraceTier.TIER_1_FULL.value
    return lane_spec_trace_tier


def _validate_trace_tier(body: LaneEvaluationCreate, lane_spec_trace_tier: str) -> None:
    required_tier = _required_trace_tier(
        body.lane_family.value,
        body.result_status.value,
        lane_spec_trace_tier,
    )
    actual_tier = body.trace_bundle.trace_tier.value
    if TRACE_TIER_RANK[actual_tier] > TRACE_TIER_RANK[required_tier]:
        raise GovernanceValidationError(
            f"trace_tier {actual_tier} is insufficient; required tier is {required_tier}."
        )
    if actual_tier == TraceTier.TIER_3_RECONSTRUCTION.value and body.trace_bundle.reconstructable_flag is False:
        raise GovernanceValidationError(
            "tier_3_reconstruction trace bundles must be reconstructable."
        )
    if actual_tier == TraceTier.TIER_1_FULL.value and not body.trace_bundle.trace_events:
        raise GovernanceValidationError("tier_1_full trace bundles require at least one trace event.")


def _validate_output_values(body: LaneEvaluationCreate) -> None:
    primary_output_count = sum(1 for output in body.output_values if output.is_primary_output)
    if body.result_status in {ResultStatus.COMPUTED_STRICT, ResultStatus.COMPUTED_DEGRADED}:
        if not body.output_values:
            raise GovernanceValidationError("computed evaluations require output_values.")
        if primary_output_count != 1:
            raise GovernanceValidationError("computed evaluations require exactly one primary output.")

    if body.lane_family == LaneFamily.HYBRID_GATE:
        has_non_scalar_posture = any(
            output.output_posture in {OutputPosture.CLASSIFIED, OutputPosture.GATED}
            or output.text_value is not None
            or output.enum_value is not None
            for output in body.output_values
        )
        if not has_non_scalar_posture:
            raise GovernanceValidationError(
                "hybrid_gate lanes require at least one classified or gated non-scalar output."
            )


def _validate_factor_values(body: LaneEvaluationCreate) -> None:
    if body.result_status in {ResultStatus.COMPUTED_STRICT, ResultStatus.COMPUTED_DEGRADED}:
        if not body.factor_values:
            raise GovernanceValidationError("computed evaluations require factor_values.")


def _validate_compatibility_posture(body: LaneEvaluationCreate) -> None:
    state = body.compatibility_resolution_state
    if state == CompatibilityResolutionState.BLOCKED_INCOMPATIBLE:
        if body.result_status not in {ResultStatus.BLOCKED, ResultStatus.AUDIT_ONLY, ResultStatus.INVALID}:
            raise GovernanceValidationError(
                "blocked_incompatible compatibility may only produce blocked, audit_only, or invalid results."
            )
        if body.replay_state not in {ReplayState.AUDIT_READABLE_ONLY, ReplayState.NOT_REPLAYABLE}:
            raise GovernanceValidationError(
                "blocked_incompatible compatibility may not be replay_safe."
            )
    if state == CompatibilityResolutionState.AUDIT_ONLY and body.result_status == ResultStatus.COMPUTED_STRICT:
        raise GovernanceValidationError("audit_only compatibility cannot produce computed_strict results.")


def _validate_compatibility_binding(db: Session, body: LaneEvaluationCreate) -> dict[str, Any]:
    binding = body.compatibility_binding
    compatibility_tuple = binding.compatibility_tuple
    if compatibility_tuple.lane_spec_version != body.lane_spec_version:
        raise GovernanceValidationError(
            "compatibility tuple lane_spec_version must match the lane evaluation lane_spec_version."
        )
    if compatibility_tuple.trace_schema_version != body.trace_bundle.trace_schema_version:
        raise GovernanceValidationError(
            "compatibility tuple trace_schema_version must match the trace bundle trace_schema_version."
        )

    variable_registry = get_variable_registry(
        db,
        binding.variable_registry_id,
        compatibility_tuple.variable_registry_version,
    )
    _require_active_binding(
        variable_registry,
        f"VariableRegistry {binding.variable_registry_id} version {compatibility_tuple.variable_registry_version}",
    )

    parameter_set = get_parameter_set(
        db,
        binding.parameter_set_id,
        compatibility_tuple.parameter_set_version,
    )
    _require_active_binding(
        parameter_set,
        f"ParameterSet {binding.parameter_set_id} version {compatibility_tuple.parameter_set_version}",
    )

    threshold_set = get_threshold_set(
        db,
        binding.threshold_set_id,
        compatibility_tuple.threshold_registry_version,
    )
    _require_active_binding(
        threshold_set,
        f"ThresholdSet {binding.threshold_set_id} version {compatibility_tuple.threshold_registry_version}",
    )

    null_policy = get_policy_bundle(
        db,
        binding.null_policy_bundle_id,
        compatibility_tuple.null_policy_version,
    )
    _validate_policy_bundle_kind(
        null_policy,
        PolicyBundleKind.NULL_POLICY,
        f"PolicyBundle {binding.null_policy_bundle_id} version {compatibility_tuple.null_policy_version}",
    )

    degraded_policy = get_policy_bundle(
        db,
        binding.degraded_mode_policy_bundle_id,
        compatibility_tuple.degraded_mode_policy_version,
    )
    _validate_policy_bundle_kind(
        degraded_policy,
        PolicyBundleKind.DEGRADED_MODE_POLICY,
        (
            f"PolicyBundle {binding.degraded_mode_policy_bundle_id} version "
            f"{compatibility_tuple.degraded_mode_policy_version}"
        ),
    )

    payload = binding.model_dump(mode="json")
    payload["compatibility_tuple_hash"] = binding.canonical_hash()
    return payload


def create_input_bundle(db: Session, body: InputBundleCreate) -> InputBundle:
    input_bundle_id = _clean_identifier(body.input_bundle_id, "input_bundle_id")
    _ensure_unique_id(db, InputBundle, "input_bundle_id", input_bundle_id)
    if not body.frozen_flag:
        raise GovernanceValidationError("canonical input bundles must be created frozen.")
    created_by = _clean_optional_text(body.created_by)
    scope_id = _clean_optional_text(body.scope_id)
    if scope_id is not None:
        if body.scope_version is None:
            raise GovernanceValidationError("scope_version is required when scope_id is provided.")
        scope_binding = get_scope_registry(db, scope_id, body.scope_version)
        _require_active_binding(scope_binding, f"ScopeRegistry {scope_id} version {body.scope_version}")
    payload_hash = _hash_payload(
        {
            "scope_id": scope_id,
            "scope_version": body.scope_version,
            "provenance_class": body.provenance_class,
            "collection_timestamp": body.collection_timestamp.isoformat(),
            "normalization_scope": body.normalization_scope,
            "source_artifact_refs": body.source_artifact_refs,
            "inline_values": body.inline_values,
        }
    )
    existing_hash = db.scalar(
        select(InputBundle).where(InputBundle.deterministic_input_hash == payload_hash)
    )
    if existing_hash is not None:
        raise GovernanceConflictError(
            "an equivalent frozen input bundle already exists for this deterministic payload."
        )
    record = InputBundle(
        input_bundle_id=input_bundle_id,
        scope_id=scope_id,
        scope_version=body.scope_version,
        provenance_class=_clean_identifier(body.provenance_class, "provenance_class"),
        collection_timestamp=body.collection_timestamp,
        admissibility_notes=_clean_optional_text(body.admissibility_notes),
        normalization_scope=_clean_identifier(body.normalization_scope, "normalization_scope"),
        deterministic_input_hash=payload_hash,
        source_artifact_refs=body.source_artifact_refs,
        inline_values=body.inline_values,
        frozen_flag=True,
        created_by=created_by,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_input_bundles(db: Session) -> list[InputBundle]:
    return list(db.scalars(select(InputBundle).order_by(InputBundle.created_at.desc())).all())


def get_input_bundle(db: Session, input_bundle_id: str) -> InputBundle:
    return _get_or_404(db, InputBundle, "input_bundle_id", _clean_identifier(input_bundle_id, "input_bundle_id"))


def create_lane_evaluation(db: Session, body: LaneEvaluationCreate) -> LaneEvaluation:
    lane_evaluation_id = _clean_identifier(body.lane_evaluation_id, "lane_evaluation_id")
    _ensure_unique_id(db, LaneEvaluation, "lane_evaluation_id", lane_evaluation_id)
    _ensure_unique_id(db, TraceBundle, "trace_bundle_id", _clean_identifier(body.trace_bundle.trace_bundle_id, "trace_bundle_id"))

    lane_spec = get_lane_spec(db, body.lane_id, body.lane_spec_version)
    _validate_lane_spec(lane_spec, body.lane_id, body.lane_family.value)

    runtime_profile = get_runtime_profile(db, body.runtime_profile_id, body.runtime_profile_version)
    _validate_runtime_profile(runtime_profile, body.runtime_profile_id)

    input_bundle = get_input_bundle(db, body.input_bundle_id)
    if not input_bundle.frozen_flag:
        raise GovernanceValidationError("canonical evaluations require a frozen input bundle.")

    evaluation_scope_id = _clean_optional_text(body.scope_id)
    evaluation_scope_version = body.scope_version
    if evaluation_scope_id is not None:
        if evaluation_scope_version is None:
            raise GovernanceValidationError("scope_version is required when scope_id is provided.")
        scope_binding = get_scope_registry(db, evaluation_scope_id, evaluation_scope_version)
        _require_active_binding(
            scope_binding,
            f"ScopeRegistry {evaluation_scope_id} version {evaluation_scope_version}",
        )

    if input_bundle.scope_id is not None:
        if evaluation_scope_id is None:
            evaluation_scope_id = input_bundle.scope_id
            evaluation_scope_version = input_bundle.scope_version
        elif input_bundle.scope_id != evaluation_scope_id or input_bundle.scope_version != evaluation_scope_version:
            raise GovernanceValidationError(
                "lane evaluation scope linkage must match the frozen input bundle scope linkage."
            )

    compatibility_binding_payload = _validate_compatibility_binding(db, body)
    _validate_compatibility_posture(body)
    _validate_trace_tier(body, lane_spec.trace_tier)
    _validate_output_values(body)
    _validate_factor_values(body)

    previous_evaluation = None
    supersedes_evaluation_id = _clean_optional_text(body.supersedes_evaluation_id)
    if supersedes_evaluation_id is not None:
        previous_evaluation = get_lane_evaluation(db, supersedes_evaluation_id)
        if previous_evaluation.lane_id != body.lane_id:
            raise GovernanceValidationError("superseded lane evaluation must belong to the same lane_id.")
        if previous_evaluation.superseded_by_evaluation_id is not None:
            raise GovernanceValidationError("superseded lane evaluation is already closed by lineage.")

    trace_bundle_hash = _hash_payload(
        {
            "trace_bundle_id": body.trace_bundle.trace_bundle_id,
            "trace_tier": body.trace_bundle.trace_tier.value,
            "trace_schema_version": body.trace_bundle.trace_schema_version,
            "reconstructable_flag": body.trace_bundle.reconstructable_flag,
            "trace_events": [event.model_dump(mode="json") for event in body.trace_bundle.trace_events],
        }
    )
    compatibility_tuple_hash = compatibility_binding_payload["compatibility_tuple_hash"]

    evaluation = LaneEvaluation(
        lane_evaluation_id=lane_evaluation_id,
        lane_id=_clean_identifier(body.lane_id, "lane_id"),
        lane_spec_version=body.lane_spec_version,
        lane_family=body.lane_family.value,
        execution_mode=_clean_identifier(body.execution_mode, "execution_mode"),
        result_status=body.result_status.value,
        compatibility_resolution_state=body.compatibility_resolution_state.value,
        runtime_profile_id=_clean_identifier(body.runtime_profile_id, "runtime_profile_id"),
        runtime_profile_version=body.runtime_profile_version,
        input_bundle_id=input_bundle.input_bundle_id,
        trace_bundle_id=_clean_identifier(body.trace_bundle.trace_bundle_id, "trace_bundle_id"),
        replay_state=body.replay_state.value,
        stale_state=body.stale_state.value,
        raw_output_hash=_clean_optional_text(body.raw_output_hash),
        compatibility_tuple_hash=compatibility_tuple_hash,
        compatibility_binding_payload=compatibility_binding_payload,
        scope_id=evaluation_scope_id,
        scope_version=evaluation_scope_version,
        created_by=_clean_optional_text(body.created_by),
    )
    db.add(evaluation)

    trace_bundle = TraceBundle(
        trace_bundle_id=evaluation.trace_bundle_id,
        lane_evaluation_id=lane_evaluation_id,
        trace_tier=body.trace_bundle.trace_tier.value,
        trace_schema_version=body.trace_bundle.trace_schema_version,
        trace_bundle_hash=trace_bundle_hash,
        reconstructable_flag=body.trace_bundle.reconstructable_flag,
    )
    db.add(trace_bundle)

    for output in body.output_values:
        db.add(
            LaneOutputValue(
                lane_evaluation_id=lane_evaluation_id,
                output_field_name=_clean_identifier(output.output_field_name, "output_field_name"),
                output_posture=output.output_posture.value,
                numeric_value=output.numeric_value,
                text_value=_clean_optional_text(output.text_value),
                enum_value=_clean_optional_text(output.enum_value),
                value_range_class=_clean_optional_text(output.value_range_class),
                is_primary_output=output.is_primary_output,
            )
        )

    for factor in body.factor_values:
        db.add(
            LaneFactorValue(
                lane_evaluation_id=lane_evaluation_id,
                factor_name=_clean_identifier(factor.factor_name, "factor_name"),
                raw_value=factor.raw_value,
                normalized_value=factor.normalized_value,
                weighted_value=factor.weighted_value,
                omitted_flag=factor.omitted_flag,
                omission_reason=_clean_optional_text(factor.omission_reason),
                provenance_class=_clean_optional_text(factor.provenance_class),
                volatility_class=_clean_optional_text(factor.volatility_class),
            )
        )

    for event in body.trace_bundle.trace_events:
        db.add(
            TraceEvent(
                trace_bundle_id=trace_bundle.trace_bundle_id,
                trace_step_order=event.trace_step_order,
                trace_event_type=_clean_identifier(event.trace_event_type, "trace_event_type"),
                trace_payload_ref=_clean_identifier(event.trace_payload_ref, "trace_payload_ref"),
                trace_summary=_clean_identifier(event.trace_summary, "trace_summary"),
            )
        )

    if previous_evaluation is not None:
        previous_evaluation.superseded_by_evaluation_id = lane_evaluation_id

    db.commit()
    return get_lane_evaluation(db, lane_evaluation_id)


def _build_trace_bundle_read(db: Session, lane_evaluation_id: str) -> TraceBundleRead:
    trace_bundle = db.scalar(
        select(TraceBundle).where(TraceBundle.lane_evaluation_id == lane_evaluation_id)
    )
    if trace_bundle is None:
        raise GovernanceNotFoundError(
            f"TraceBundle for lane evaluation {lane_evaluation_id} was not found."
        )
    trace_events = list(
        db.scalars(
            select(TraceEvent)
            .where(TraceEvent.trace_bundle_id == trace_bundle.trace_bundle_id)
            .order_by(TraceEvent.trace_step_order.asc())
        ).all()
    )
    trace_bundle_read = TraceBundleRead.model_validate(trace_bundle)
    return trace_bundle_read.model_copy(
        update={"trace_events": [TraceEventRead.model_validate(item) for item in trace_events]}
    )


def list_lane_evaluations(db: Session) -> list[LaneEvaluationSummaryRead]:
    evaluations = list(
        db.scalars(select(LaneEvaluation).order_by(LaneEvaluation.created_at.desc())).all()
    )
    return [LaneEvaluationSummaryRead.model_validate(record) for record in evaluations]


def get_lane_evaluation(db: Session, lane_evaluation_id: str) -> LaneEvaluation:
    return _get_or_404(
        db,
        LaneEvaluation,
        "lane_evaluation_id",
        _clean_identifier(lane_evaluation_id, "lane_evaluation_id"),
    )


def get_lane_evaluation_detail(db: Session, lane_evaluation_id: str) -> LaneEvaluationDetailRead:
    evaluation = get_lane_evaluation(db, lane_evaluation_id)
    outputs = list(
        db.scalars(
            select(LaneOutputValue)
            .where(LaneOutputValue.lane_evaluation_id == evaluation.lane_evaluation_id)
            .order_by(LaneOutputValue.created_at.asc())
        ).all()
    )
    factors = list(
        db.scalars(
            select(LaneFactorValue)
            .where(LaneFactorValue.lane_evaluation_id == evaluation.lane_evaluation_id)
            .order_by(LaneFactorValue.created_at.asc())
        ).all()
    )
    summary = LaneEvaluationSummaryRead.model_validate(evaluation)
    return LaneEvaluationDetailRead(
        **summary.model_dump(),
        compatibility_binding_payload=evaluation.compatibility_binding_payload,
        output_values=[LaneOutputValueRead.model_validate(item) for item in outputs],
        factor_values=[LaneFactorValueRead.model_validate(item) for item in factors],
        trace_bundle=_build_trace_bundle_read(db, evaluation.lane_evaluation_id),
    )


def create_replay_queue_event(db: Session, body: ReplayQueueEventCreate) -> ReplayQueueEvent:
    replay_event_id = _clean_identifier(body.replay_event_id, "replay_event_id")
    _ensure_unique_id(db, ReplayQueueEvent, "replay_event_id", replay_event_id)
    related_input_bundle_id = _clean_optional_text(body.related_input_bundle_id)
    related_lane_evaluation_id = _clean_optional_text(body.related_lane_evaluation_id)
    if related_input_bundle_id is not None:
        get_input_bundle(db, related_input_bundle_id)
    if related_lane_evaluation_id is not None:
        get_lane_evaluation(db, related_lane_evaluation_id)

    record = ReplayQueueEvent(
        replay_event_id=replay_event_id,
        triggering_reason=_clean_identifier(body.triggering_reason, "triggering_reason"),
        priority_class=body.priority_class.value,
        budget_class=body.budget_class.value,
        operator_review_required_flag=body.operator_review_required_flag,
        status=_clean_identifier(body.status, "status"),
        related_lane_id=_clean_optional_text(body.related_lane_id),
        related_scope_id=_clean_optional_text(body.related_scope_id),
        related_input_bundle_id=related_input_bundle_id,
        related_lane_evaluation_id=related_lane_evaluation_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_replay_queue_events(db: Session) -> list[ReplayQueueEvent]:
    return list(
        db.scalars(select(ReplayQueueEvent).order_by(ReplayQueueEvent.created_at.desc())).all()
    )


def get_replay_queue_event(db: Session, replay_event_id: str) -> ReplayQueueEvent:
    return _get_or_404(
        db,
        ReplayQueueEvent,
        "replay_event_id",
        _clean_identifier(replay_event_id, "replay_event_id"),
    )


def create_incident_record(db: Session, body: IncidentRecordCreate) -> IncidentRecord:
    incident_id = _clean_identifier(body.incident_id, "incident_id")
    _ensure_unique_id(db, IncidentRecord, "incident_id", incident_id)
    related_lane_evaluation_id = _clean_optional_text(body.related_lane_evaluation_id)
    if related_lane_evaluation_id is not None:
        get_lane_evaluation(db, related_lane_evaluation_id)

    record = IncidentRecord(
        incident_id=incident_id,
        incident_class=body.incident_class.value,
        severity=body.severity.value,
        affected_scope_id=_clean_optional_text(body.affected_scope_id),
        affected_lane_id=_clean_optional_text(body.affected_lane_id),
        summary=_clean_identifier(body.summary, "summary"),
        canonical_truth_impact_flag=body.canonical_truth_impact_flag,
        related_lane_evaluation_id=related_lane_evaluation_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_incident_records(db: Session) -> list[IncidentRecord]:
    return list(db.scalars(select(IncidentRecord).order_by(IncidentRecord.created_at.desc())).all())


def get_incident_record(db: Session, incident_id: str) -> IncidentRecord:
    return _get_or_404(
        db,
        IncidentRecord,
        "incident_id",
        _clean_identifier(incident_id, "incident_id"),
    )
