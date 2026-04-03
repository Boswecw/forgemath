from datetime import datetime, timezone

import pytest

from app.schemas.governance import CompatibilityTuple, LaneSpecCreate, ParameterSetCreate
from app.services.immutability import ImmutablePayloadError
from app.services import registry_service


def test_lane_spec_payload_is_immutable_once_persisted(db):
    lane_spec = registry_service.create_lane_spec(
        db,
        LaneSpecCreate(
            lane_id="verification_burden",
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase1-test",
            lane_family="canonical_numeric",
            trace_tier="tier_1_full",
            is_admissible=True,
            payload={"contract_version": "v1"},
        ),
    )

    lane_spec.payload = {"contract_version": "v2"}
    with pytest.raises(ImmutablePayloadError):
        db.commit()
    db.rollback()


def test_superseding_parameter_set_closes_prior_version_without_overwrite(db):
    version_1 = registry_service.create_parameter_set(
        db,
        ParameterSetCreate(
            parameter_set_id="verification-burden-defaults",
            lane_id="verification_burden",
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase1-test",
            payload={"weights": {"w_I": 0.15}},
        ),
    )

    version_2 = registry_service.create_parameter_set(
        db,
        ParameterSetCreate(
            parameter_set_id="verification-burden-defaults",
            lane_id="verification_burden",
            version=2,
            supersedes_version=1,
            retired_reason="weight refresh",
            effective_from=datetime(2026, 4, 3, tzinfo=timezone.utc),
            created_by="phase1-test",
            payload={"weights": {"w_I": 0.20}},
        ),
    )

    previous = registry_service.get_parameter_set(db, "verification-burden-defaults", 1)
    assert previous.payload == {"weights": {"w_I": 0.15}}
    assert previous.superseded_by_id == version_2.id
    assert previous.retired_reason == "weight refresh"
    assert previous.superseded_at == datetime(2026, 4, 3, tzinfo=timezone.utc)
    assert version_2.version == 2


def test_compatibility_tuple_hash_is_stable():
    compatibility_tuple = CompatibilityTuple(
        lane_spec_version=1,
        variable_registry_version=1,
        parameter_set_version=1,
        threshold_registry_version=1,
        null_policy_version=1,
        degraded_mode_policy_version=1,
        trace_schema_version=1,
        projection_schema_version=1,
        submodule_build_version="forge-math-v0.1.0",
    )

    assert compatibility_tuple.canonical_hash() == compatibility_tuple.canonical_hash()
