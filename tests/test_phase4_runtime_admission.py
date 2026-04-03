from datetime import datetime, timezone

import pytest

from app.api.evaluation_router import get_lane_evaluation_runtime_admission
from app.models.governance import RuntimeProfile
from app.services import evaluation_service, registry_service
from tests.test_phase2_api import _create_input_bundle, _evaluation_create, _seed_phase1_bindings


def _insert_runtime_profile(
    db,
    *,
    runtime_profile_id: str,
    version: int = 1,
    numeric_precision_mode: str = "decimal128",
    rounding_mode: str = "half_even",
    sort_policy_id: str = "stable-total-order",
    serialization_policy_id: str = "canonical-json-v1",
    timezone_policy: str = "UTC",
    seed_policy: str = "fixed-seed",
    non_determinism_allowed_flag: bool = False,
    superseded_at=None,
):
    db.add(
        RuntimeProfile(
            runtime_profile_id=runtime_profile_id,
            version=version,
            payload_hash=f"{runtime_profile_id}-payload-hash",
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            superseded_at=superseded_at,
            superseded_by_id=None,
            retired_reason="retired for deterministic runtime test"
            if superseded_at is not None
            else None,
            created_by="phase4-test",
            numeric_precision_mode=numeric_precision_mode,
            rounding_mode=rounding_mode,
            sort_policy_id=sort_policy_id,
            serialization_policy_id=serialization_policy_id,
            timezone_policy=timezone_policy,
            seed_policy=seed_policy,
            non_determinism_allowed_flag=non_determinism_allowed_flag,
        )
    )
    db.commit()


def test_evaluation_persists_runtime_admission_truth_and_events(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)

    created = evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings))
    assert created.deterministic_admission_state == "admitted_canonical_deterministic"
    assert created.runtime_validation_reason_code == "runtime_profile_validated_for_canonical_admission"
    assert created.determinism_certificate_ref.startswith("determinism-cert://")
    assert created.bit_exact_eligible is True

    runtime_read = get_lane_evaluation_runtime_admission("eval-001", db)
    assert runtime_read.current_runtime_profile_present is True
    assert runtime_read.current_runtime_profile_active is True
    assert runtime_read.current_runtime_profile_non_deterministic is False
    assert runtime_read.runtime_admission_events[0].admission_outcome == "admitted_canonical_deterministic"


def test_runtime_admission_rejects_non_deterministic_runtime_profile(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    _insert_runtime_profile(
        db,
        runtime_profile_id="runtime-nondeterministic",
        non_determinism_allowed_flag=True,
    )

    body = _evaluation_create(bindings)
    body.runtime_profile_id = "runtime-nondeterministic"
    body.runtime_profile_version = 1

    with pytest.raises(registry_service.GovernanceValidationError) as exc_info:
        evaluation_service.create_lane_evaluation(db, body)

    assert "blocked_non_deterministic_profile" in str(exc_info.value)


def test_runtime_admission_rejects_incomplete_runtime_profile(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    _insert_runtime_profile(
        db,
        runtime_profile_id="runtime-incomplete",
        sort_policy_id="",
        serialization_policy_id="",
    )

    body = _evaluation_create(bindings)
    body.runtime_profile_id = "runtime-incomplete"
    body.runtime_profile_version = 1

    with pytest.raises(registry_service.GovernanceValidationError) as exc_info:
        evaluation_service.create_lane_evaluation(db, body)

    assert "blocked_incomplete_runtime_profile" in str(exc_info.value)


def test_runtime_admission_rejects_retired_runtime_profile(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    _insert_runtime_profile(
        db,
        runtime_profile_id="runtime-retired",
        superseded_at=datetime(2026, 4, 2, 13, 0, tzinfo=timezone.utc),
    )

    body = _evaluation_create(bindings)
    body.runtime_profile_id = "runtime-retired"
    body.runtime_profile_version = 1

    with pytest.raises(registry_service.GovernanceValidationError) as exc_info:
        evaluation_service.create_lane_evaluation(db, body)

    assert "blocked_retired_runtime_profile" in str(exc_info.value)
