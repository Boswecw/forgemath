from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.enums import DeterministicAdmissionState
from app.models.evaluation import InputBundle, LaneEvaluation, RuntimeAdmissionEvent
from app.models.governance import RuntimeProfile
from app.schemas.evaluation import LaneEvaluationRuntimeAdmissionRead, RuntimeAdmissionEventRead
from app.services.registry_service import (
    GovernanceNotFoundError,
    GovernanceValidationError,
    _clean_identifier,
    _clean_optional_text,
)


REQUIRED_RUNTIME_FIELDS = {
    "numeric_precision_mode": "numeric_precision_mode",
    "rounding_mode": "rounding_mode",
    "sort_policy_id": "sort_policy_id",
    "serialization_policy_id": "serialization_policy_id",
    "timezone_policy": "timezone_policy",
    "seed_policy": "seed_policy",
}

BIT_EXACT_RUNTIME_POLICY = {
    "numeric_precision_mode": {"decimal128"},
    "rounding_mode": {"half_even"},
    "sort_policy_id": {"stable-total-order"},
    "serialization_policy_id": {"canonical-json-v1"},
    "timezone_policy": {"UTC"},
    "seed_policy": {"fixed-seed"},
}


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _hash_payload(payload: Any) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RuntimeAdmissionResult:
    deterministic_admission_state: str
    runtime_validation_reason_code: str
    runtime_validation_reason_detail: str | None
    determinism_certificate_ref: str
    bit_exact_eligible: bool


def _missing_runtime_fields(runtime_profile: RuntimeProfile) -> list[str]:
    missing: list[str] = []
    for field_name in REQUIRED_RUNTIME_FIELDS:
        value = getattr(runtime_profile, field_name, None)
        if value is None or not str(value).strip():
            missing.append(field_name)
    return missing


def _bit_exact_eligible(runtime_profile: RuntimeProfile) -> bool:
    if runtime_profile.non_determinism_allowed_flag:
        return False
    for field_name, allowed_values in BIT_EXACT_RUNTIME_POLICY.items():
        value = getattr(runtime_profile, field_name, None)
        if value not in allowed_values:
            return False
    return True


def validate_runtime_profile_for_canonical_execution(
    runtime_profile: RuntimeProfile,
    runtime_profile_id: str,
) -> None:
    if runtime_profile.superseded_at is not None:
        raise GovernanceValidationError(
            "runtime profile blocks canonical admission: "
            f"{DeterministicAdmissionState.BLOCKED_RETIRED_RUNTIME_PROFILE.value}. "
            f"RuntimeProfile {runtime_profile_id} version {runtime_profile.version} is retired."
        )

    missing_fields = _missing_runtime_fields(runtime_profile)
    if missing_fields:
        raise GovernanceValidationError(
            "runtime profile blocks canonical admission: "
            f"{DeterministicAdmissionState.BLOCKED_INCOMPLETE_RUNTIME_PROFILE.value}. "
            "Missing or blank fields: "
            + ", ".join(sorted(missing_fields))
            + "."
        )

    if runtime_profile.non_determinism_allowed_flag:
        raise GovernanceValidationError(
            "runtime profile blocks canonical admission: "
            f"{DeterministicAdmissionState.BLOCKED_NON_DETERMINISTIC_PROFILE.value}. "
            "non_determinism_allowed_flag must be false."
        )


def derive_runtime_admission_result(
    runtime_profile: RuntimeProfile,
    *,
    input_bundle: InputBundle,
    compatibility_tuple_hash: str,
) -> RuntimeAdmissionResult:
    validate_runtime_profile_for_canonical_execution(
        runtime_profile,
        runtime_profile.runtime_profile_id,
    )

    bit_exact_eligible = _bit_exact_eligible(runtime_profile)
    certificate_hash = _hash_payload(
        {
            "runtime_profile_id": runtime_profile.runtime_profile_id,
            "runtime_profile_version": runtime_profile.version,
            "numeric_precision_mode": runtime_profile.numeric_precision_mode,
            "rounding_mode": runtime_profile.rounding_mode,
            "sort_policy_id": runtime_profile.sort_policy_id,
            "serialization_policy_id": runtime_profile.serialization_policy_id,
            "timezone_policy": runtime_profile.timezone_policy,
            "seed_policy": runtime_profile.seed_policy,
            "compatibility_tuple_hash": compatibility_tuple_hash,
            "deterministic_input_hash": input_bundle.deterministic_input_hash,
        }
    )
    detail = (
        "Deterministic runtime profile validated for canonical admission; "
        f"bit_exact_eligible={'true' if bit_exact_eligible else 'false'}."
    )
    return RuntimeAdmissionResult(
        deterministic_admission_state=DeterministicAdmissionState.ADMITTED_CANONICAL_DETERMINISTIC.value,
        runtime_validation_reason_code="runtime_profile_validated_for_canonical_admission",
        runtime_validation_reason_detail=detail,
        determinism_certificate_ref=f"determinism-cert://{certificate_hash}",
        bit_exact_eligible=bit_exact_eligible,
    )


def record_runtime_admission_event(
    db: Session,
    *,
    evaluation: LaneEvaluation,
    created_by: str | None,
) -> None:
    db.add(
        RuntimeAdmissionEvent(
            lane_evaluation_id=evaluation.lane_evaluation_id,
            runtime_profile_id=evaluation.runtime_profile_id,
            runtime_profile_version=evaluation.runtime_profile_version,
            admission_outcome=evaluation.deterministic_admission_state,
            reason_code=evaluation.runtime_validation_reason_code,
            reason_detail=evaluation.runtime_validation_reason_detail,
            determinism_certificate_ref=evaluation.determinism_certificate_ref,
            bit_exact_eligible=evaluation.bit_exact_eligible,
            created_by=_clean_optional_text(created_by),
        )
    )


def get_runtime_admission(db: Session, lane_evaluation_id: str) -> LaneEvaluationRuntimeAdmissionRead:
    normalized_id = _clean_identifier(lane_evaluation_id, "lane_evaluation_id")
    evaluation = db.scalar(
        select(LaneEvaluation).where(LaneEvaluation.lane_evaluation_id == normalized_id)
    )
    if evaluation is None:
        raise GovernanceNotFoundError(
            f"LaneEvaluation {normalized_id} was not found."
        )

    runtime_events = list(
        db.scalars(
            select(RuntimeAdmissionEvent)
            .where(RuntimeAdmissionEvent.lane_evaluation_id == normalized_id)
            .order_by(RuntimeAdmissionEvent.created_at.asc(), RuntimeAdmissionEvent.event_id.asc())
        ).all()
    )
    runtime_profile = db.scalar(
        select(RuntimeProfile).where(
            RuntimeProfile.runtime_profile_id == evaluation.runtime_profile_id,
            RuntimeProfile.version == evaluation.runtime_profile_version,
        )
    )

    return LaneEvaluationRuntimeAdmissionRead(
        lane_evaluation_id=evaluation.lane_evaluation_id,
        runtime_profile_id=evaluation.runtime_profile_id,
        runtime_profile_version=evaluation.runtime_profile_version,
        deterministic_admission_state=evaluation.deterministic_admission_state,
        runtime_validation_reason_code=evaluation.runtime_validation_reason_code,
        runtime_validation_reason_detail=evaluation.runtime_validation_reason_detail,
        determinism_certificate_ref=evaluation.determinism_certificate_ref,
        bit_exact_eligible=evaluation.bit_exact_eligible,
        current_runtime_profile_present=runtime_profile is not None,
        current_runtime_profile_active=(
            runtime_profile is not None and runtime_profile.superseded_at is None
        ),
        current_runtime_profile_non_deterministic=(
            None if runtime_profile is None else runtime_profile.non_determinism_allowed_flag
        ),
        runtime_admission_events=[
            RuntimeAdmissionEventRead.model_validate(item) for item in runtime_events
        ],
    )
