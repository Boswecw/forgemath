from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import (
    CompatibilityResolutionState,
    RecomputationAction,
    ReplayState,
    ResultStatus,
    StaleState,
    SupersessionClass,
)
from app.models.evaluation import (
    EvaluationLifecycleEvent,
    InputBundle,
    LaneEvaluation,
    TraceBundle,
)
from app.models.governance import (
    LaneSpec,
    ParameterSet,
    PolicyBundle,
    RuntimeProfile,
    ThresholdSet,
    VariableRegistry,
)
from app.schemas.evaluation import (
    LaneEvaluationCreate,
    LaneEvaluationLifecycleEventRead,
    LaneEvaluationLifecycleRead,
    LaneEvaluationLifecycleTransitionCreate,
    LaneEvaluationLineageRead,
    LaneEvaluationSummaryRead,
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
    get_threshold_set,
    get_variable_registry,
)


STALE_RANK = {
    StaleState.FRESH.value: 0,
    StaleState.STALE_UPSTREAM_CHANGED.value: 1,
    StaleState.STALE_POLICY_SUPERSEDED.value: 2,
    StaleState.STALE_SEMANTICS_CHANGED.value: 3,
    StaleState.STALE_DETERMINISM_RETIRED.value: 4,
    StaleState.STALE_INPUT_INVALIDATED.value: 5,
}


@dataclass
class EvaluationBindings:
    lane_spec: LaneSpec | None
    variable_registry: VariableRegistry | None
    parameter_set: ParameterSet | None
    threshold_set: ThresholdSet | None
    null_policy: PolicyBundle | None
    degraded_policy: PolicyBundle | None
    prior_registry: VariableRegistry | None
    decay_registry: VariableRegistry | None
    runtime_profile: RuntimeProfile | None
    input_bundle: InputBundle | None
    trace_bundle: TraceBundle | None


def _get_or_none(fetcher, *args):
    try:
        return fetcher(*args)
    except GovernanceNotFoundError:
        return None


def _compatibility_payload(evaluation: LaneEvaluation) -> dict[str, Any]:
    payload = evaluation.compatibility_binding_payload or {}
    tuple_payload = payload.get("compatibility_tuple")
    if not isinstance(tuple_payload, dict):
        raise GovernanceValidationError(
            "lane evaluation compatibility_binding_payload is incomplete."
        )
    return payload


def _compatibility_tuple(payload: dict[str, Any]) -> dict[str, Any]:
    tuple_payload = payload.get("compatibility_tuple")
    if not isinstance(tuple_payload, dict):
        raise GovernanceValidationError(
            "lane evaluation compatibility tuple is incomplete."
        )
    return tuple_payload


def _binding_id(payload: dict[str, Any], field_name: str) -> str | None:
    value = payload.get(field_name)
    if value is None:
        return None
    normalized = _clean_optional_text(str(value))
    return normalized


def _binding_version(tuple_payload: dict[str, Any], field_name: str) -> int | None:
    value = tuple_payload.get(field_name)
    if value is None:
        return None
    if not isinstance(value, int) or value <= 0:
        raise GovernanceValidationError(f"{field_name} must be a positive integer in compatibility binding payload.")
    return value


def _get_bindings(db: Session, evaluation: LaneEvaluation) -> EvaluationBindings:
    payload = _compatibility_payload(evaluation)
    tuple_payload = _compatibility_tuple(payload)

    prior_registry_id = _binding_id(payload, "prior_registry_id")
    decay_registry_id = _binding_id(payload, "decay_registry_id")
    prior_registry_version = _binding_version(tuple_payload, "prior_registry_version")
    decay_registry_version = _binding_version(tuple_payload, "decay_registry_version")

    return EvaluationBindings(
        lane_spec=_get_or_none(get_lane_spec, db, evaluation.lane_id, evaluation.lane_spec_version),
        variable_registry=_get_or_none(
            get_variable_registry,
            db,
            _binding_id(payload, "variable_registry_id"),
            _binding_version(tuple_payload, "variable_registry_version"),
        ),
        parameter_set=_get_or_none(
            get_parameter_set,
            db,
            _binding_id(payload, "parameter_set_id"),
            _binding_version(tuple_payload, "parameter_set_version"),
        ),
        threshold_set=_get_or_none(
            get_threshold_set,
            db,
            _binding_id(payload, "threshold_set_id"),
            _binding_version(tuple_payload, "threshold_registry_version"),
        ),
        null_policy=_get_or_none(
            get_policy_bundle,
            db,
            _binding_id(payload, "null_policy_bundle_id"),
            _binding_version(tuple_payload, "null_policy_version"),
        ),
        degraded_policy=_get_or_none(
            get_policy_bundle,
            db,
            _binding_id(payload, "degraded_mode_policy_bundle_id"),
            _binding_version(tuple_payload, "degraded_mode_policy_version"),
        ),
        prior_registry=(
            _get_or_none(get_variable_registry, db, prior_registry_id, prior_registry_version)
            if prior_registry_id is not None and prior_registry_version is not None
            else None
        ),
        decay_registry=(
            _get_or_none(get_variable_registry, db, decay_registry_id, decay_registry_version)
            if decay_registry_id is not None and decay_registry_version is not None
            else None
        ),
        runtime_profile=_get_or_none(
            get_runtime_profile,
            db,
            evaluation.runtime_profile_id,
            evaluation.runtime_profile_version,
        ),
        input_bundle=db.scalar(
            select(InputBundle).where(InputBundle.input_bundle_id == evaluation.input_bundle_id)
        ),
        trace_bundle=db.scalar(
            select(TraceBundle).where(TraceBundle.lane_evaluation_id == evaluation.lane_evaluation_id)
        ),
    )


def _required_binding_records(bindings: EvaluationBindings) -> dict[str, Any]:
    return {
        "lane_spec": bindings.lane_spec,
        "variable_registry": bindings.variable_registry,
        "parameter_set": bindings.parameter_set,
        "threshold_set": bindings.threshold_set,
        "null_policy": bindings.null_policy,
        "degraded_policy": bindings.degraded_policy,
        "runtime_profile": bindings.runtime_profile,
        "input_bundle": bindings.input_bundle,
    }


def _validate_lifecycle_bindings(bindings: EvaluationBindings) -> None:
    missing = [label for label, record in _required_binding_records(bindings).items() if record is None]
    if missing:
        raise GovernanceValidationError(
            "lifecycle transition cannot be derived because required bindings are missing: "
            + ", ".join(sorted(missing))
            + "."
        )


def _is_superseded(record: Any) -> bool:
    return record is not None and getattr(record, "superseded_at", None) is not None


def _has_upstream_change(bindings: EvaluationBindings) -> bool:
    upstream_bindings = (
        bindings.variable_registry,
        bindings.parameter_set,
        bindings.threshold_set,
        bindings.prior_registry,
        bindings.decay_registry,
    )
    return any(_is_superseded(item) for item in upstream_bindings if item is not None)


def _has_policy_supersession(bindings: EvaluationBindings) -> bool:
    return any(_is_superseded(item) for item in (bindings.null_policy, bindings.degraded_policy) if item is not None)


def _has_semantic_supersession(bindings: EvaluationBindings) -> bool:
    return _is_superseded(bindings.lane_spec)


def _has_determinism_retirement(bindings: EvaluationBindings) -> bool:
    if bindings.runtime_profile is None:
        return True
    return _is_superseded(bindings.runtime_profile) or bindings.runtime_profile.non_determinism_allowed_flag


def _effective_stale_state(
    current_stale_state: str,
    requested_stale_state: str,
) -> str:
    if STALE_RANK[requested_stale_state] >= STALE_RANK[current_stale_state]:
        return requested_stale_state
    return current_stale_state


def _validate_replay_posture(
    *,
    evaluation: LaneEvaluation,
    bindings: EvaluationBindings,
    replay_state: str,
    compatibility_resolution_state: str,
    result_status: str,
) -> None:
    if replay_state in {
        ReplayState.REPLAY_SAFE.value,
        ReplayState.REPLAY_SAFE_WITH_BOUNDED_MIGRATION.value,
    }:
        if result_status in {ResultStatus.AUDIT_ONLY.value, ResultStatus.INVALID.value}:
            raise GovernanceValidationError(
                "audit_only and invalid results may not claim replay-safe posture."
            )
        if evaluation.raw_output_hash is None:
            raise GovernanceValidationError(
                "replay-safe posture requires raw_output_hash to persist the canonical output artifact."
            )
        if bindings.input_bundle is None or not bindings.input_bundle.frozen_flag:
            raise GovernanceValidationError(
                "replay-safe posture requires a frozen input bundle."
            )
        if bindings.trace_bundle is None:
            raise GovernanceValidationError(
                "replay-safe posture requires an attached trace bundle."
            )
        _validate_lifecycle_bindings(bindings)

    if replay_state == ReplayState.REPLAY_SAFE.value:
        if compatibility_resolution_state != CompatibilityResolutionState.RESOLVED_HARD_COMPATIBLE.value:
            raise GovernanceValidationError(
                "replay_safe requires compatibility_resolution_state=resolved_hard_compatible."
            )
    if replay_state == ReplayState.REPLAY_SAFE_WITH_BOUNDED_MIGRATION.value:
        if compatibility_resolution_state != CompatibilityResolutionState.RESOLVED_WITH_BOUNDED_MIGRATION.value:
            raise GovernanceValidationError(
                "replay_safe_with_bounded_migration requires "
                "compatibility_resolution_state=resolved_with_bounded_migration."
            )


def _validate_recomputation_action(
    *,
    stale_state: str,
    recomputation_action: str,
    compatibility_resolution_state: str,
    result_status: str,
    replay_state: str,
    is_superseded: bool,
) -> None:
    allowed: set[str]
    if stale_state == StaleState.FRESH.value:
        allowed = {RecomputationAction.NO_RECOMPUTE_NEEDED.value}
        if compatibility_resolution_state == CompatibilityResolutionState.RESOLVED_WITH_BOUNDED_MIGRATION.value:
            allowed.add(RecomputationAction.OPTIONAL_RECOMPUTE.value)
        if replay_state == ReplayState.REPLAY_SAFE_WITH_BOUNDED_MIGRATION.value:
            allowed.add(RecomputationAction.OPTIONAL_RECOMPUTE.value)
        if result_status == ResultStatus.COMPUTED_DEGRADED.value:
            allowed.add(RecomputationAction.OPTIONAL_RECOMPUTE.value)
        if result_status in {ResultStatus.AUDIT_ONLY.value, ResultStatus.INVALID.value}:
            allowed.add(RecomputationAction.PRESERVE_AS_AUDIT_ONLY.value)
        if replay_state in {ReplayState.AUDIT_READABLE_ONLY.value, ReplayState.NOT_REPLAYABLE.value}:
            allowed.add(RecomputationAction.PRESERVE_AS_AUDIT_ONLY.value)
    elif stale_state == StaleState.STALE_UPSTREAM_CHANGED.value:
        allowed = {
            RecomputationAction.OPTIONAL_RECOMPUTE.value,
            RecomputationAction.MANDATORY_RECOMPUTE.value,
        }
    else:
        allowed = {
            RecomputationAction.MANDATORY_RECOMPUTE.value,
            RecomputationAction.PRESERVE_AS_AUDIT_ONLY.value,
        }

    if is_superseded:
        allowed.add(RecomputationAction.PRESERVE_AS_AUDIT_ONLY.value)

    if recomputation_action not in allowed:
        raise GovernanceValidationError(
            "recomputation_action is incompatible with the requested lifecycle posture."
        )


def _validate_stale_transition(
    *,
    evaluation: LaneEvaluation,
    bindings: EvaluationBindings,
    body: LaneEvaluationLifecycleTransitionCreate,
) -> None:
    if STALE_RANK[body.stale_state.value] < STALE_RANK[evaluation.stale_state]:
        raise GovernanceValidationError(
            "lifecycle transitions may not reduce stale-state severity."
        )

    has_existing_supersession = evaluation.superseded_by_evaluation_id is not None
    has_requested_supersession = body.related_evaluation_id is not None

    if body.stale_state == StaleState.FRESH:
        if evaluation.stale_state != StaleState.FRESH.value:
            raise GovernanceValidationError("stale evaluations may not be reset to fresh.")
        if body.input_bundle_invalidated:
            raise GovernanceValidationError(
                "fresh may not be claimed when the frozen input bundle is invalidated."
            )
        if _has_determinism_retirement(bindings):
            raise GovernanceValidationError(
                "fresh may not be claimed when the deterministic runtime profile is retired."
            )
        if _has_semantic_supersession(bindings):
            raise GovernanceValidationError(
                "fresh may not be claimed when the lane spec has been superseded."
            )
        if _has_policy_supersession(bindings):
            raise GovernanceValidationError(
                "fresh may not be claimed when bound policy bundles are superseded."
            )
        if _has_upstream_change(bindings):
            raise GovernanceValidationError(
                "fresh may not be claimed when bound upstream registries are superseded."
            )
        if has_existing_supersession and evaluation.supersession_class != SupersessionClass.PROJECTION_SUPERSESSION.value:
            raise GovernanceValidationError(
                "fresh may not be claimed once a non-projection supersession is recorded."
            )
        if (
            has_requested_supersession
            and body.supersession_class != SupersessionClass.PROJECTION_SUPERSESSION
        ):
            raise GovernanceValidationError(
                "fresh may not be claimed for non-projection supersession transitions."
            )
        return

    if body.stale_state == StaleState.STALE_INPUT_INVALIDATED:
        if not body.input_bundle_invalidated:
            raise GovernanceValidationError(
                "stale_input_invalidated requires explicit input_bundle_invalidated evidence."
            )
        return

    if body.stale_state == StaleState.STALE_POLICY_SUPERSEDED:
        if body.supersession_class == SupersessionClass.POLICY_SUPERSESSION:
            return
        if not _has_policy_supersession(bindings):
            raise GovernanceValidationError(
                "stale_policy_superseded requires superseded bound policy bundles."
            )
        return

    if body.stale_state == StaleState.STALE_SEMANTICS_CHANGED:
        if body.supersession_class == SupersessionClass.SEMANTIC_SUPERSESSION:
            return
        if not _has_semantic_supersession(bindings):
            raise GovernanceValidationError(
                "stale_semantics_changed requires a superseded lane spec binding."
            )
        return

    if body.stale_state == StaleState.STALE_DETERMINISM_RETIRED:
        if not _has_determinism_retirement(bindings):
            raise GovernanceValidationError(
                "stale_determinism_retired requires a retired deterministic runtime profile."
            )
        return

    if body.stale_state == StaleState.STALE_UPSTREAM_CHANGED:
        if body.supersession_class == SupersessionClass.SEMANTIC_SUPERSESSION:
            raise GovernanceValidationError(
                "semantic_supersession requires stale_state=stale_semantics_changed."
            )
        if body.supersession_class == SupersessionClass.POLICY_SUPERSESSION:
            raise GovernanceValidationError(
                "policy_supersession requires stale_state=stale_policy_superseded."
            )
        if body.supersession_class in {
            SupersessionClass.INPUT_SUPERSESSION,
            SupersessionClass.PARAMETER_SUPERSESSION,
            SupersessionClass.PROJECTION_SUPERSESSION,
        }:
            return
        if not _has_upstream_change(bindings):
            raise GovernanceValidationError(
                "stale_upstream_changed requires superseded upstream registry bindings."
            )
        return


def _validate_supersession_transition(
    db: Session,
    evaluation: LaneEvaluation,
    body: LaneEvaluationLifecycleTransitionCreate,
) -> None:
    related_evaluation_id = _clean_optional_text(body.related_evaluation_id)
    if related_evaluation_id is None:
        return

    if related_evaluation_id == evaluation.lane_evaluation_id:
        raise GovernanceValidationError("lane evaluation may not supersede itself.")

    related_evaluation = db.scalar(
        select(LaneEvaluation).where(LaneEvaluation.lane_evaluation_id == related_evaluation_id)
    )
    if related_evaluation is None:
        raise GovernanceNotFoundError(
            f"LaneEvaluation {related_evaluation_id} was not found."
        )
    if related_evaluation.lane_id != evaluation.lane_id:
        raise GovernanceValidationError(
            "supersession lineage requires the related evaluation to share the same lane_id."
        )

    existing_link = evaluation.superseded_by_evaluation_id
    if existing_link is not None and existing_link != related_evaluation_id:
        raise GovernanceConflictError(
            "lane evaluation already has a different superseding evaluation recorded."
        )

    if body.supersession_class is None or body.supersession_reason is None or body.supersession_timestamp is None:
        raise GovernanceValidationError(
            "supersession transitions require supersession_class, supersession_reason, and supersession_timestamp."
        )

    if existing_link == related_evaluation_id:
        if evaluation.supersession_class != body.supersession_class.value:
            raise GovernanceConflictError("supersession_class is already fixed for this lineage link.")
        if evaluation.supersession_reason != _clean_optional_text(body.supersession_reason):
            raise GovernanceConflictError("supersession_reason is already fixed for this lineage link.")
        if evaluation.supersession_timestamp != body.supersession_timestamp:
            raise GovernanceConflictError("supersession_timestamp is already fixed for this lineage link.")


def _append_lifecycle_event(
    db: Session,
    *,
    evaluation: LaneEvaluation,
    event_type: str,
    prior_replay_state: str | None,
    prior_stale_state: str | None,
    prior_recomputation_action: str | None,
    reason_code: str,
    reason_detail: str | None,
    related_evaluation_id: str | None,
    created_by: str | None,
) -> None:
    db.add(
        EvaluationLifecycleEvent(
            lane_evaluation_id=evaluation.lane_evaluation_id,
            event_type=_clean_identifier(event_type, "event_type"),
            prior_replay_state=prior_replay_state,
            new_replay_state=evaluation.replay_state,
            prior_stale_state=prior_stale_state,
            new_stale_state=evaluation.stale_state,
            prior_recomputation_action=prior_recomputation_action,
            new_recomputation_action=evaluation.recomputation_action,
            reason_code=_clean_identifier(reason_code, "reason_code"),
            reason_detail=_clean_optional_text(reason_detail),
            related_evaluation_id=_clean_optional_text(related_evaluation_id),
            created_by=_clean_optional_text(created_by),
        )
    )


def _supersession_stale_state(supersession_class: SupersessionClass) -> str:
    if supersession_class == SupersessionClass.POLICY_SUPERSESSION:
        return StaleState.STALE_POLICY_SUPERSEDED.value
    if supersession_class == SupersessionClass.SEMANTIC_SUPERSESSION:
        return StaleState.STALE_SEMANTICS_CHANGED.value
    if supersession_class == SupersessionClass.PROJECTION_SUPERSESSION:
        return StaleState.FRESH.value
    return StaleState.STALE_UPSTREAM_CHANGED.value


def validate_evaluation_creation_lifecycle(body: LaneEvaluationCreate) -> None:
    replay_state = body.replay_state.value
    compatibility_state = body.compatibility_resolution_state.value
    result_status = body.result_status.value
    stale_state = body.stale_state.value
    recomputation_action = body.recomputation_action.value

    if replay_state == ReplayState.REPLAY_SAFE.value:
        if compatibility_state != CompatibilityResolutionState.RESOLVED_HARD_COMPATIBLE.value:
            raise GovernanceValidationError(
                "replay_safe requires compatibility_resolution_state=resolved_hard_compatible."
            )
    if replay_state == ReplayState.REPLAY_SAFE_WITH_BOUNDED_MIGRATION.value:
        if compatibility_state != CompatibilityResolutionState.RESOLVED_WITH_BOUNDED_MIGRATION.value:
            raise GovernanceValidationError(
                "replay_safe_with_bounded_migration requires "
                "compatibility_resolution_state=resolved_with_bounded_migration."
            )
    if replay_state in {
        ReplayState.REPLAY_SAFE.value,
        ReplayState.REPLAY_SAFE_WITH_BOUNDED_MIGRATION.value,
    } and result_status in {ResultStatus.AUDIT_ONLY.value, ResultStatus.INVALID.value}:
        raise GovernanceValidationError(
            "audit_only and invalid results may not claim replay-safe posture."
        )

    _validate_recomputation_action(
        stale_state=stale_state,
        recomputation_action=recomputation_action,
        compatibility_resolution_state=compatibility_state,
        result_status=result_status,
        replay_state=replay_state,
        is_superseded=False,
    )


def record_evaluation_created_event(db: Session, evaluation: LaneEvaluation) -> None:
    _append_lifecycle_event(
        db,
        evaluation=evaluation,
        event_type="evaluation_created",
        prior_replay_state=None,
        prior_stale_state=None,
        prior_recomputation_action=None,
        reason_code=evaluation.lifecycle_reason_code,
        reason_detail=evaluation.lifecycle_reason_detail,
        related_evaluation_id=None,
        created_by=evaluation.created_by,
    )


def record_supersession_from_new_evaluation(
    db: Session,
    *,
    prior_evaluation: LaneEvaluation,
    successor_evaluation_id: str,
    supersession_class: SupersessionClass,
    supersession_reason: str,
    supersession_timestamp: datetime,
    created_by: str | None,
) -> None:
    if prior_evaluation.superseded_by_evaluation_id is not None:
        raise GovernanceConflictError("superseded lane evaluation is already closed by lineage.")

    next_stale_state = _effective_stale_state(
        prior_evaluation.stale_state,
        _supersession_stale_state(supersession_class),
    )
    prior_replay_state = prior_evaluation.replay_state
    prior_stale = prior_evaluation.stale_state
    prior_recompute = prior_evaluation.recomputation_action

    prior_evaluation.superseded_by_evaluation_id = _clean_identifier(
        successor_evaluation_id,
        "successor_evaluation_id",
    )
    prior_evaluation.supersession_class = supersession_class.value
    prior_evaluation.supersession_reason = _clean_identifier(
        supersession_reason,
        "supersession_reason",
    )
    prior_evaluation.supersession_timestamp = supersession_timestamp
    prior_evaluation.stale_state = next_stale_state
    prior_evaluation.recomputation_action = RecomputationAction.PRESERVE_AS_AUDIT_ONLY.value
    prior_evaluation.lifecycle_reason_code = "superseded_by_evaluation"
    prior_evaluation.lifecycle_reason_detail = prior_evaluation.supersession_reason

    _append_lifecycle_event(
        db,
        evaluation=prior_evaluation,
        event_type="supersession_recorded",
        prior_replay_state=prior_replay_state,
        prior_stale_state=prior_stale,
        prior_recomputation_action=prior_recompute,
        reason_code=prior_evaluation.lifecycle_reason_code,
        reason_detail=prior_evaluation.lifecycle_reason_detail,
        related_evaluation_id=successor_evaluation_id,
        created_by=created_by,
    )


def _get_lifecycle_events(db: Session, lane_evaluation_id: str) -> list[EvaluationLifecycleEvent]:
    return list(
        db.scalars(
            select(EvaluationLifecycleEvent)
            .where(EvaluationLifecycleEvent.lane_evaluation_id == lane_evaluation_id)
            .order_by(EvaluationLifecycleEvent.created_at.asc(), EvaluationLifecycleEvent.event_id.asc())
        ).all()
    )


def get_lane_evaluation_lifecycle(db: Session, lane_evaluation_id: str) -> LaneEvaluationLifecycleRead:
    evaluation = db.scalar(
        select(LaneEvaluation).where(
            LaneEvaluation.lane_evaluation_id == _clean_identifier(lane_evaluation_id, "lane_evaluation_id")
        )
    )
    if evaluation is None:
        raise GovernanceNotFoundError(
            f"LaneEvaluation {lane_evaluation_id} was not found."
        )
    events = [LaneEvaluationLifecycleEventRead.model_validate(item) for item in _get_lifecycle_events(db, evaluation.lane_evaluation_id)]
    lifecycle_read = LaneEvaluationLifecycleRead.model_validate(evaluation)
    return lifecycle_read.model_copy(update={"lifecycle_events": events})


def _direct_predecessor(db: Session, lane_evaluation_id: str) -> LaneEvaluation | None:
    return db.scalar(
        select(LaneEvaluation).where(
            LaneEvaluation.superseded_by_evaluation_id == lane_evaluation_id
        )
    )


def get_lane_evaluation_lineage(db: Session, lane_evaluation_id: str) -> LaneEvaluationLineageRead:
    anchor = db.scalar(
        select(LaneEvaluation).where(
            LaneEvaluation.lane_evaluation_id == _clean_identifier(lane_evaluation_id, "lane_evaluation_id")
        )
    )
    if anchor is None:
        raise GovernanceNotFoundError(
            f"LaneEvaluation {lane_evaluation_id} was not found."
        )

    oldest = anchor
    visited = {anchor.lane_evaluation_id}
    predecessor = _direct_predecessor(db, oldest.lane_evaluation_id)
    while predecessor is not None:
        if predecessor.lane_evaluation_id in visited:
            raise GovernanceValidationError("lineage cycle detected in supersession chain.")
        visited.add(predecessor.lane_evaluation_id)
        oldest = predecessor
        predecessor = _direct_predecessor(db, oldest.lane_evaluation_id)

    lineage: list[LaneEvaluationSummaryRead] = []
    current = oldest
    visited = set()
    while current is not None:
        if current.lane_evaluation_id in visited:
            raise GovernanceValidationError("lineage cycle detected in supersession chain.")
        visited.add(current.lane_evaluation_id)
        lineage.append(LaneEvaluationSummaryRead.model_validate(current))
        if current.superseded_by_evaluation_id is None:
            break
        current = db.scalar(
            select(LaneEvaluation).where(
                LaneEvaluation.lane_evaluation_id == current.superseded_by_evaluation_id
            )
        )

    return LaneEvaluationLineageRead(
        anchor_lane_evaluation_id=anchor.lane_evaluation_id,
        lane_id=anchor.lane_id,
        lineage=lineage,
    )


def apply_lifecycle_transition(
    db: Session,
    lane_evaluation_id: str,
    body: LaneEvaluationLifecycleTransitionCreate,
) -> LaneEvaluationLifecycleRead:
    evaluation = db.scalar(
        select(LaneEvaluation).where(
            LaneEvaluation.lane_evaluation_id == _clean_identifier(lane_evaluation_id, "lane_evaluation_id")
        )
    )
    if evaluation is None:
        raise GovernanceNotFoundError(
            f"LaneEvaluation {lane_evaluation_id} was not found."
        )

    bindings = _get_bindings(db, evaluation)
    _validate_lifecycle_bindings(bindings)
    _validate_supersession_transition(db, evaluation, body)
    _validate_stale_transition(evaluation=evaluation, bindings=bindings, body=body)
    _validate_replay_posture(
        evaluation=evaluation,
        bindings=bindings,
        replay_state=body.replay_state.value,
        compatibility_resolution_state=evaluation.compatibility_resolution_state,
        result_status=evaluation.result_status,
    )
    _validate_recomputation_action(
        stale_state=body.stale_state.value,
        recomputation_action=body.recomputation_action.value,
        compatibility_resolution_state=evaluation.compatibility_resolution_state,
        result_status=evaluation.result_status,
        replay_state=body.replay_state.value,
        is_superseded=evaluation.superseded_by_evaluation_id is not None or body.related_evaluation_id is not None,
    )

    new_related_evaluation_id = _clean_optional_text(body.related_evaluation_id)
    supersession_reason = _clean_optional_text(body.supersession_reason)
    lifecycle_reason_detail = _clean_optional_text(body.lifecycle_reason_detail)

    changed = (
        evaluation.replay_state != body.replay_state.value
        or evaluation.stale_state != body.stale_state.value
        or evaluation.recomputation_action != body.recomputation_action.value
        or evaluation.lifecycle_reason_code != body.lifecycle_reason_code
        or evaluation.lifecycle_reason_detail != lifecycle_reason_detail
        or (
            new_related_evaluation_id is not None
            and evaluation.superseded_by_evaluation_id != new_related_evaluation_id
        )
    )
    if not changed:
        raise GovernanceValidationError("lifecycle transition did not change canonical lifecycle truth.")

    prior_replay_state = evaluation.replay_state
    prior_stale_state = evaluation.stale_state
    prior_recomputation_action = evaluation.recomputation_action

    evaluation.replay_state = body.replay_state.value
    evaluation.stale_state = body.stale_state.value
    evaluation.recomputation_action = body.recomputation_action.value
    evaluation.lifecycle_reason_code = _clean_identifier(
        body.lifecycle_reason_code,
        "lifecycle_reason_code",
    )
    evaluation.lifecycle_reason_detail = lifecycle_reason_detail

    if new_related_evaluation_id is not None:
        if evaluation.superseded_by_evaluation_id is None:
            evaluation.superseded_by_evaluation_id = new_related_evaluation_id
            evaluation.supersession_class = body.supersession_class.value
            evaluation.supersession_reason = _clean_identifier(
                supersession_reason or "",
                "supersession_reason",
            )
            evaluation.supersession_timestamp = body.supersession_timestamp
        else:
            evaluation.superseded_by_evaluation_id = new_related_evaluation_id

    _append_lifecycle_event(
        db,
        evaluation=evaluation,
        event_type="lifecycle_transition",
        prior_replay_state=prior_replay_state,
        prior_stale_state=prior_stale_state,
        prior_recomputation_action=prior_recomputation_action,
        reason_code=evaluation.lifecycle_reason_code,
        reason_detail=evaluation.lifecycle_reason_detail,
        related_evaluation_id=new_related_evaluation_id,
        created_by=body.created_by,
    )
    db.commit()
    db.refresh(evaluation)
    return get_lane_evaluation_lifecycle(db, evaluation.lane_evaluation_id)
