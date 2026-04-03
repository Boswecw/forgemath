from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.api.evaluation_router import (
    get_lane_evaluation_runtime_admission,
    create_lane_evaluation,
    transition_lane_evaluation_lifecycle,
)
from app.api.registry_router import create_migration_package
from app.schemas.evaluation import LaneEvaluationLifecycleTransitionCreate
from app.schemas.governance import MigrationPackageCreate, RuntimeProfileCreate
from app.services import evaluation_service, registry_service
from tests.test_phase2_api import _create_input_bundle, _evaluation_create, _seed_phase1_bindings
from tests.test_phase2_api import _manual_evaluation_create


def test_persistence_level_active_canonical_exclusivity_rejects_duplicate_context(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)

    evaluation_service.create_lane_evaluation(
        db,
        _evaluation_create(
            bindings,
            lane_evaluation_id="canonical-001",
            execution_mode="governed_canonical_execution",
        ),
    )

    with pytest.raises(registry_service.GovernanceConflictError) as exc_info:
        evaluation_service.create_lane_evaluation(
            db,
            _evaluation_create(
                bindings,
                lane_evaluation_id="canonical-002",
                execution_mode="governed_canonical_execution",
            ),
        )

    assert "active canonical execution exclusivity" in str(exc_info.value)


def test_active_canonical_exclusivity_allows_explicit_supersession(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)

    first = evaluation_service.create_lane_evaluation(
        db,
        _evaluation_create(
            bindings,
            lane_evaluation_id="canonical-001",
            execution_mode="governed_canonical_execution",
        ),
    )
    assert first.active_canonical_execution_key is not None
    second = evaluation_service.create_lane_evaluation(
        db,
        _evaluation_create(
            bindings,
            lane_evaluation_id="canonical-002",
            execution_mode="governed_canonical_execution",
            supersedes_evaluation_id="canonical-001",
        ),
    )

    refreshed_first = evaluation_service.get_lane_evaluation(db, "canonical-001")
    refreshed_second = evaluation_service.get_lane_evaluation(db, "canonical-002")

    assert refreshed_first.superseded_by_evaluation_id == "canonical-002"
    assert refreshed_first.active_canonical_execution_key is None
    assert refreshed_second.active_canonical_execution_key is not None
    assert second.lane_evaluation_id == "canonical-002"


def test_canonical_execution_writer_rejects_supersession_of_manual_ingest_lineage(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    create_lane_evaluation(_manual_evaluation_create(bindings, lane_evaluation_id="manual-001"), db)

    with pytest.raises(registry_service.GovernanceValidationError) as exc_info:
        evaluation_service.create_lane_evaluation(
            db,
            _evaluation_create(
                bindings,
                lane_evaluation_id="canonical-003",
                execution_mode="governed_canonical_execution",
                supersedes_evaluation_id="manual-001",
            ),
        )

    assert "may only supersede prior governed_canonical_execution" in str(exc_info.value)


def test_determinism_sensitive_migration_rejects_hard_compatible_posture():
    with pytest.raises(ValidationError) as exc_info:
        MigrationPackageCreate(
            migration_id="numeric-serialization-v2",
            version=1,
            effective_from=datetime(2026, 4, 3, tzinfo=timezone.utc),
            created_by="phase7-test",
            migration_class="numeric_serialization_migration",
            source_versions={"serialization_policy_id": "canonical-json-v1"},
            target_versions={"serialization_policy_id": "canonical-json-v2"},
            affected_artifacts=["forgemath_lane_output_values", "forgemath_lane_factor_values"],
            determinism_sensitive_artifacts=["numeric_serialization", "artifact_hashing"],
            migration_logic_summary="Change canonical decimal-string rendering rules.",
            compatibility_class_after_migration="hard_compatible",
            rollback_plan="Restore canonical-json-v1 and quarantine changed outputs.",
            replay_impact_statement="Replay comparability changes under the new canonical serializer.",
            audit_only_impact_statement="Legacy artifacts remain visible but not canonically equivalent.",
            approval_state="pending_review",
        )

    assert "may not declare compatibility_class_after_migration=hard_compatible" in str(exc_info.value)


def test_valid_determinism_sensitive_migration_package_persists(db):
    created = create_migration_package(
        MigrationPackageCreate(
            migration_id="artifact-hashing-v2",
            version=1,
            effective_from=datetime(2026, 4, 3, tzinfo=timezone.utc),
            created_by="phase7-test",
            migration_class="artifact_hashing_migration",
            source_versions={"artifact_hashing": "v1"},
            target_versions={"artifact_hashing": "v2"},
            affected_artifacts=["forgemath_lane_evaluations", "forgemath_trace_bundles"],
            determinism_sensitive_artifacts=["artifact_hashing", "trace_hashing"],
            migration_logic_summary="Advance canonical artifact hashing with explicit bounded migration posture.",
            compatibility_class_after_migration="bounded_migration",
            rollback_plan="Restore v1 hashing and preserve v2 artifacts as audit-only.",
            replay_impact_statement="Replay requires bounded migration because canonical artifact equality changes.",
            audit_only_impact_statement="Legacy artifacts remain readable but not equal to recomputed v2 artifacts.",
            approval_state="pending_review",
        ),
        db,
    )

    assert created.migration_class == "artifact_hashing_migration"
    assert created.determinism_sensitive_artifacts == [
        "artifact_hashing",
        "trace_hashing",
    ]


def test_runtime_admission_read_exposes_retired_profile_recovery_posture(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings))

    registry_service.create_runtime_profile(
        db,
        RuntimeProfileCreate(
            runtime_profile_id=bindings["runtime_profile"].runtime_profile_id,
            version=2,
            effective_from=datetime(2026, 4, 3, 9, 0, tzinfo=timezone.utc),
            created_by="phase7-test",
            supersedes_version=1,
            retired_reason="Phase 7 runtime retirement hardening test.",
            numeric_precision_mode="decimal128",
            rounding_mode="half_even",
            sort_policy_id="stable-total-order",
            serialization_policy_id="canonical-json-v1",
            timezone_policy="UTC",
            seed_policy="fixed-seed",
            non_determinism_allowed_flag=False,
        ),
    )

    runtime_read = get_lane_evaluation_runtime_admission("eval-001", db)

    assert runtime_read.current_runtime_profile_present is True
    assert runtime_read.current_runtime_profile_active is False
    assert runtime_read.runtime_recovery_posture == "retired_for_canonical_execution"
    assert runtime_read.runtime_recovery_action == "requires_recompute_under_new_runtime_profile"
    assert runtime_read.operator_review_required_flag is True


def test_runtime_admission_read_exposes_missing_profile_rebinding_posture(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings))

    db.delete(bindings["runtime_profile"])
    db.commit()

    runtime_read = get_lane_evaluation_runtime_admission("eval-001", db)

    assert runtime_read.current_runtime_profile_present is False
    assert runtime_read.runtime_recovery_posture == "requires_profile_rebinding"
    assert runtime_read.runtime_recovery_action == "requires_profile_rebinding"
    assert runtime_read.operator_review_required_flag is True


def test_lifecycle_transition_rejects_temporally_reversed_supersession(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings, lane_evaluation_id="eval-001"))
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings, lane_evaluation_id="eval-002"))

    with pytest.raises(HTTPException) as exc_info:
        transition_lane_evaluation_lifecycle(
            "eval-002",
            LaneEvaluationLifecycleTransitionCreate(
                replay_state="audit_readable_only",
                stale_state="stale_upstream_changed",
                recomputation_action="preserve_as_audit_only",
                lifecycle_reason_code="temporal_supersession_rejected",
                related_evaluation_id="eval-001",
                supersession_class="parameter_supersession",
                supersession_reason="Newer evaluation may not be superseded by an older record.",
                supersession_timestamp=datetime(2026, 4, 3, 10, 0, tzinfo=timezone.utc),
                created_by="phase7-test",
            ),
            db,
        )

    assert exc_info.value.status_code == 400
    assert "created at or after" in exc_info.value.detail


def test_lifecycle_transition_rejects_lineage_cycle(db):
    bindings = _seed_phase1_bindings(db)
    _create_input_bundle(db, bindings)
    evaluation_service.create_lane_evaluation(db, _evaluation_create(bindings, lane_evaluation_id="eval-001"))
    evaluation_service.create_lane_evaluation(
        db,
        _evaluation_create(
            bindings,
            lane_evaluation_id="eval-002",
            supersedes_evaluation_id="eval-001",
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        transition_lane_evaluation_lifecycle(
            "eval-002",
            LaneEvaluationLifecycleTransitionCreate(
                replay_state="audit_readable_only",
                stale_state="stale_upstream_changed",
                recomputation_action="preserve_as_audit_only",
                lifecycle_reason_code="cycle_rejected",
                related_evaluation_id="eval-001",
                supersession_class="parameter_supersession",
                supersession_reason="Cycle attempt should be rejected.",
                supersession_timestamp=datetime(2026, 4, 3, 11, 0, tzinfo=timezone.utc),
                created_by="phase7-test",
            ),
            db,
        )

    assert exc_info.value.status_code == 409
    assert "lineage cycle" in exc_info.value.detail
