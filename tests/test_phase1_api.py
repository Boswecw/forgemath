from datetime import datetime, timezone

import pytest
from fastapi import HTTPException

from app.api.registry_router import (
    create_lane_spec,
    create_migration_package,
    create_runtime_profile,
    get_lane_spec,
    get_migration_package,
)
from app.schemas.governance import LaneSpecCreate, MigrationPackageCreate, RuntimeProfileCreate


def test_create_and_fetch_lane_spec(db):
    created = create_lane_spec(
        LaneSpecCreate(
            lane_id="verification_burden",
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase1-test",
            lane_family="canonical_numeric",
            trace_tier="tier_1_full",
            is_admissible=True,
            payload={
                "contract_version": "v1",
                "admitted_inputs": [
                    "implementation_minutes",
                    "verification_minutes",
                    "rework_minutes",
                ],
            },
        ),
        db,
    )
    assert created.lane_id == "verification_burden"
    assert created.version == 1
    assert created.payload_hash

    fetched = get_lane_spec("verification_burden", 1, db)
    assert fetched.payload_hash == created.payload_hash


def test_duplicate_lane_spec_version_is_rejected(db):
    payload = LaneSpecCreate(
        lane_id="verification_burden",
        version=1,
        effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
        created_by="phase1-test",
        lane_family="canonical_numeric",
        trace_tier="tier_1_full",
        is_admissible=True,
        payload={"contract_version": "v1"},
    )
    create_lane_spec(payload, db)

    with pytest.raises(HTTPException) as exc_info:
        create_lane_spec(payload, db)

    assert exc_info.value.status_code == 409
    assert "already exists" in exc_info.value.detail


def test_runtime_profile_rejects_nondeterministic_canonical_profile(db):
    with pytest.raises(HTTPException) as exc_info:
        create_runtime_profile(
            RuntimeProfileCreate(
                runtime_profile_id="default-canonical",
                version=1,
                effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
                created_by="phase1-test",
                numeric_precision_mode="decimal128",
                rounding_mode="half_even",
                sort_policy_id="stable-total-order",
                serialization_policy_id="canonical-json-v1",
                timezone_policy="UTC",
                seed_policy="fixed-zero-seed",
                non_determinism_allowed_flag=True,
            ),
            db,
        )

    assert exc_info.value.status_code == 400
    assert "non_determinism_allowed_flag" in exc_info.value.detail


def test_create_and_fetch_migration_package(db):
    created = create_migration_package(
        MigrationPackageCreate(
            migration_id="compatibility-tuple-v2",
            version=1,
            effective_from=datetime(2026, 4, 2, tzinfo=timezone.utc),
            created_by="phase1-test",
            migration_class="bounded_migration",
            source_versions={"lane_spec_version": 1, "projection_schema_version": 1},
            target_versions={"lane_spec_version": 2, "projection_schema_version": 2},
            affected_artifacts=["forgemath_lane_specs", "forgemath_projection_records"],
            migration_logic_summary="Advance the tuple contract without changing formula semantics.",
            compatibility_class_after_migration="bounded_migration",
            rollback_plan="Restore v1 bindings and classify migrated reads as audit_only.",
            replay_impact_statement="Replay required for strict canonical consumers.",
            audit_only_impact_statement="Legacy reads remain visible but non-authoritative.",
            approval_state="pending_review",
        ),
        db,
    )
    assert created.migration_id == "compatibility-tuple-v2"
    assert created.affected_artifacts == [
        "forgemath_lane_specs",
        "forgemath_projection_records",
    ]

    fetched = get_migration_package("compatibility-tuple-v2", 1, db)
    assert fetched.payload_hash == created.payload_hash
