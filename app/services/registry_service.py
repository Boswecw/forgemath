from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Any, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.governance import (
    GovernedVersionedMixin,
    LaneSpec,
    MigrationPackage,
    ParameterSet,
    PolicyBundle,
    RuntimeProfile,
    ScopeRegistry,
    ThresholdSet,
    VariableRegistry,
    new_uuid,
)
from app.schemas.governance import (
    LaneSpecCreate,
    MigrationPackageCreate,
    ParameterSetCreate,
    PolicyBundleCreate,
    RuntimeProfileCreate,
    ScopeRegistryCreate,
    ThresholdSetCreate,
    VariableRegistryCreate,
)

GovernedModel = TypeVar("GovernedModel", bound=GovernedVersionedMixin)


class GovernanceError(ValueError):
    """Base class for governed write failures."""


class GovernanceValidationError(GovernanceError):
    """Raised when request content violates governed Phase 1 rules."""


class GovernanceConflictError(GovernanceError):
    """Raised when a duplicate or conflicting version is requested."""


class GovernanceNotFoundError(GovernanceError):
    """Raised when a governed object cannot be resolved."""


def _canonical_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)


def _payload_hash(payload: Any) -> str:
    return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def _clean_identifier(value: str, label: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise GovernanceValidationError(f"{label} must not be blank.")
    return normalized


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _list_records(
    db: Session,
    model: type[GovernedModel],
    identity_field: str,
    identity_value: str | None = None,
) -> list[GovernedModel]:
    stmt: Select[tuple[GovernedModel]] = select(model)
    if identity_value is not None:
        stmt = stmt.where(getattr(model, identity_field) == identity_value)
    stmt = stmt.order_by(getattr(model, identity_field).asc(), model.version.desc())
    return list(db.scalars(stmt).all())


def _get_record(
    db: Session,
    model: type[GovernedModel],
    identity_field: str,
    identity_value: str,
    version: int,
) -> GovernedModel:
    stmt = select(model).where(
        getattr(model, identity_field) == identity_value,
        model.version == version,
    )
    record = db.scalar(stmt)
    if record is None:
        raise GovernanceNotFoundError(
            f"{model.__name__} {identity_value} version {version} was not found."
        )
    return record


def _get_latest_record(
    db: Session,
    model: type[GovernedModel],
    identity_field: str,
    identity_value: str,
) -> GovernedModel | None:
    stmt = (
        select(model)
        .where(getattr(model, identity_field) == identity_value)
        .order_by(model.version.desc())
    )
    return db.scalar(stmt)


def _prepare_version_insert(
    db: Session,
    model: type[GovernedModel],
    identity_field: str,
    identity_value: str,
    version: int,
    supersedes_version: int | None,
    retired_reason: str | None,
) -> GovernedModel | None:
    existing_same_version = db.scalar(
        select(model).where(
            getattr(model, identity_field) == identity_value,
            model.version == version,
        )
    )
    if existing_same_version is not None:
        raise GovernanceConflictError(
            f"{model.__name__} {identity_value} version {version} already exists."
        )

    latest = _get_latest_record(db, model, identity_field, identity_value)
    if latest is None:
        if supersedes_version is not None:
            raise GovernanceValidationError(
                f"{model.__name__} {identity_value} has no prior version to supersede."
            )
        if version != 1:
            raise GovernanceValidationError(
                f"{model.__name__} {identity_value} must start at version 1."
            )
        return None

    if version != latest.version + 1:
        raise GovernanceValidationError(
            f"{model.__name__} {identity_value} must advance sequentially from version "
            f"{latest.version} to {latest.version + 1}."
        )

    if supersedes_version != latest.version:
        raise GovernanceValidationError(
            f"{model.__name__} {identity_value} version {version} must explicitly supersede "
            f"version {latest.version}."
        )

    if latest.superseded_at is None and retired_reason is None:
        raise GovernanceValidationError(
            f"{model.__name__} {identity_value} requires retired_reason when superseding "
            "an active version."
        )

    return latest


def _finalize_supersession(
    previous: GovernedModel | None,
    successor: GovernedModel,
    effective_from: datetime,
    retired_reason: str | None,
) -> None:
    if previous is None or previous.superseded_at is not None:
        return

    previous.superseded_at = effective_from
    previous.superseded_by_id = successor.id
    previous.retired_reason = retired_reason


def create_lane_spec(db: Session, body: LaneSpecCreate) -> LaneSpec:
    lane_id = _clean_identifier(body.lane_id, "lane_id")
    created_by = _clean_optional_text(body.created_by)
    retired_reason = _clean_optional_text(body.retired_reason)
    previous = _prepare_version_insert(
        db,
        LaneSpec,
        "lane_id",
        lane_id,
        body.version,
        body.supersedes_version,
        retired_reason,
    )
    hash_material = {
        "lane_family": body.lane_family.value,
        "trace_tier": body.trace_tier.value,
        "is_admissible": body.is_admissible,
        "payload": body.payload,
    }
    record = LaneSpec(
        id=new_uuid(),
        lane_id=lane_id,
        version=body.version,
        lane_family=body.lane_family.value,
        trace_tier=body.trace_tier.value,
        is_admissible=body.is_admissible,
        payload=body.payload,
        payload_hash=_payload_hash(hash_material),
        effective_from=body.effective_from,
        created_by=created_by,
    )
    db.add(record)
    _finalize_supersession(previous, record, body.effective_from, retired_reason)
    db.commit()
    db.refresh(record)
    return record


def create_variable_registry(db: Session, body: VariableRegistryCreate) -> VariableRegistry:
    variable_registry_id = _clean_identifier(body.variable_registry_id, "variable_registry_id")
    created_by = _clean_optional_text(body.created_by)
    retired_reason = _clean_optional_text(body.retired_reason)
    previous = _prepare_version_insert(
        db,
        VariableRegistry,
        "variable_registry_id",
        variable_registry_id,
        body.version,
        body.supersedes_version,
        retired_reason,
    )
    record = VariableRegistry(
        id=new_uuid(),
        variable_registry_id=variable_registry_id,
        version=body.version,
        payload=body.payload,
        payload_hash=_payload_hash({"payload": body.payload}),
        effective_from=body.effective_from,
        created_by=created_by,
    )
    db.add(record)
    _finalize_supersession(previous, record, body.effective_from, retired_reason)
    db.commit()
    db.refresh(record)
    return record


def create_parameter_set(db: Session, body: ParameterSetCreate) -> ParameterSet:
    parameter_set_id = _clean_identifier(body.parameter_set_id, "parameter_set_id")
    created_by = _clean_optional_text(body.created_by)
    retired_reason = _clean_optional_text(body.retired_reason)
    lane_id = _clean_optional_text(body.lane_id)
    previous = _prepare_version_insert(
        db,
        ParameterSet,
        "parameter_set_id",
        parameter_set_id,
        body.version,
        body.supersedes_version,
        retired_reason,
    )
    record = ParameterSet(
        id=new_uuid(),
        parameter_set_id=parameter_set_id,
        version=body.version,
        lane_id=lane_id,
        payload=body.payload,
        payload_hash=_payload_hash({"lane_id": lane_id, "payload": body.payload}),
        effective_from=body.effective_from,
        created_by=created_by,
    )
    db.add(record)
    _finalize_supersession(previous, record, body.effective_from, retired_reason)
    db.commit()
    db.refresh(record)
    return record


def create_threshold_set(db: Session, body: ThresholdSetCreate) -> ThresholdSet:
    threshold_set_id = _clean_identifier(body.threshold_set_id, "threshold_set_id")
    created_by = _clean_optional_text(body.created_by)
    retired_reason = _clean_optional_text(body.retired_reason)
    lane_id = _clean_optional_text(body.lane_id)
    previous = _prepare_version_insert(
        db,
        ThresholdSet,
        "threshold_set_id",
        threshold_set_id,
        body.version,
        body.supersedes_version,
        retired_reason,
    )
    record = ThresholdSet(
        id=new_uuid(),
        threshold_set_id=threshold_set_id,
        version=body.version,
        lane_id=lane_id,
        payload=body.payload,
        payload_hash=_payload_hash({"lane_id": lane_id, "payload": body.payload}),
        effective_from=body.effective_from,
        created_by=created_by,
    )
    db.add(record)
    _finalize_supersession(previous, record, body.effective_from, retired_reason)
    db.commit()
    db.refresh(record)
    return record


def create_policy_bundle(db: Session, body: PolicyBundleCreate) -> PolicyBundle:
    policy_bundle_id = _clean_identifier(body.policy_bundle_id, "policy_bundle_id")
    created_by = _clean_optional_text(body.created_by)
    retired_reason = _clean_optional_text(body.retired_reason)
    lane_id = _clean_optional_text(body.lane_id)
    previous = _prepare_version_insert(
        db,
        PolicyBundle,
        "policy_bundle_id",
        policy_bundle_id,
        body.version,
        body.supersedes_version,
        retired_reason,
    )
    record = PolicyBundle(
        id=new_uuid(),
        policy_bundle_id=policy_bundle_id,
        version=body.version,
        policy_kind=body.policy_kind.value,
        lane_id=lane_id,
        payload=body.payload,
        payload_hash=_payload_hash(
            {"policy_kind": body.policy_kind.value, "lane_id": lane_id, "payload": body.payload}
        ),
        effective_from=body.effective_from,
        created_by=created_by,
    )
    db.add(record)
    _finalize_supersession(previous, record, body.effective_from, retired_reason)
    db.commit()
    db.refresh(record)
    return record


def create_runtime_profile(db: Session, body: RuntimeProfileCreate) -> RuntimeProfile:
    runtime_profile_id = _clean_identifier(body.runtime_profile_id, "runtime_profile_id")
    created_by = _clean_optional_text(body.created_by)
    retired_reason = _clean_optional_text(body.retired_reason)
    previous = _prepare_version_insert(
        db,
        RuntimeProfile,
        "runtime_profile_id",
        runtime_profile_id,
        body.version,
        body.supersedes_version,
        retired_reason,
    )
    if body.non_determinism_allowed_flag:
        raise GovernanceValidationError(
            "Canonical runtime profiles must set non_determinism_allowed_flag to false."
        )
    record = RuntimeProfile(
        id=new_uuid(),
        runtime_profile_id=runtime_profile_id,
        version=body.version,
        numeric_precision_mode=_clean_identifier(body.numeric_precision_mode, "numeric_precision_mode"),
        rounding_mode=_clean_identifier(body.rounding_mode, "rounding_mode"),
        sort_policy_id=_clean_identifier(body.sort_policy_id, "sort_policy_id"),
        serialization_policy_id=_clean_identifier(
            body.serialization_policy_id,
            "serialization_policy_id",
        ),
        timezone_policy=_clean_identifier(body.timezone_policy, "timezone_policy"),
        seed_policy=_clean_identifier(body.seed_policy, "seed_policy"),
        non_determinism_allowed_flag=False,
        payload_hash=_payload_hash(
            {
                "numeric_precision_mode": body.numeric_precision_mode,
                "rounding_mode": body.rounding_mode,
                "sort_policy_id": body.sort_policy_id,
                "serialization_policy_id": body.serialization_policy_id,
                "timezone_policy": body.timezone_policy,
                "seed_policy": body.seed_policy,
                "non_determinism_allowed_flag": False,
            }
        ),
        effective_from=body.effective_from,
        created_by=created_by,
    )
    db.add(record)
    _finalize_supersession(previous, record, body.effective_from, retired_reason)
    db.commit()
    db.refresh(record)
    return record


def create_scope_registry(db: Session, body: ScopeRegistryCreate) -> ScopeRegistry:
    scope_id = _clean_identifier(body.scope_id, "scope_id")
    created_by = _clean_optional_text(body.created_by)
    retired_reason = _clean_optional_text(body.retired_reason)
    previous = _prepare_version_insert(
        db,
        ScopeRegistry,
        "scope_id",
        scope_id,
        body.version,
        body.supersedes_version,
        retired_reason,
    )
    record = ScopeRegistry(
        id=new_uuid(),
        scope_id=scope_id,
        version=body.version,
        scope_class=body.scope_class.value,
        display_name=_clean_identifier(body.display_name, "display_name"),
        payload=body.payload,
        payload_hash=_payload_hash(
            {
                "scope_class": body.scope_class.value,
                "display_name": body.display_name,
                "payload": body.payload,
            }
        ),
        effective_from=body.effective_from,
        created_by=created_by,
    )
    db.add(record)
    _finalize_supersession(previous, record, body.effective_from, retired_reason)
    db.commit()
    db.refresh(record)
    return record


def create_migration_package(db: Session, body: MigrationPackageCreate) -> MigrationPackage:
    migration_id = _clean_identifier(body.migration_id, "migration_id")
    created_by = _clean_optional_text(body.created_by)
    retired_reason = _clean_optional_text(body.retired_reason)
    previous = _prepare_version_insert(
        db,
        MigrationPackage,
        "migration_id",
        migration_id,
        body.version,
        body.supersedes_version,
        retired_reason,
    )
    determinism_sensitive_artifacts = [
        item.value for item in body.determinism_sensitive_artifacts
    ]
    record = MigrationPackage(
        id=new_uuid(),
        migration_id=migration_id,
        version=body.version,
        migration_class=body.migration_class.value,
        source_versions=body.source_versions,
        target_versions=body.target_versions,
        affected_artifacts=body.affected_artifacts,
        determinism_sensitive_artifacts=determinism_sensitive_artifacts,
        migration_logic_summary=_clean_identifier(
            body.migration_logic_summary,
            "migration_logic_summary",
        ),
        compatibility_class_after_migration=body.compatibility_class_after_migration.value,
        rollback_plan=_clean_identifier(body.rollback_plan, "rollback_plan"),
        replay_impact_statement=_clean_identifier(
            body.replay_impact_statement,
            "replay_impact_statement",
        ),
        audit_only_impact_statement=_clean_identifier(
            body.audit_only_impact_statement,
            "audit_only_impact_statement",
        ),
        approval_state=body.approval_state.value,
        payload_hash=_payload_hash(
            {
                "migration_class": body.migration_class.value,
                "source_versions": body.source_versions,
                "target_versions": body.target_versions,
                "affected_artifacts": body.affected_artifacts,
                "determinism_sensitive_artifacts": determinism_sensitive_artifacts,
                "migration_logic_summary": body.migration_logic_summary,
                "compatibility_class_after_migration": body.compatibility_class_after_migration.value,
                "rollback_plan": body.rollback_plan,
                "replay_impact_statement": body.replay_impact_statement,
                "audit_only_impact_statement": body.audit_only_impact_statement,
                "approval_state": body.approval_state.value,
            }
        ),
        effective_from=body.effective_from,
        created_by=created_by,
    )
    db.add(record)
    _finalize_supersession(previous, record, body.effective_from, retired_reason)
    db.commit()
    db.refresh(record)
    return record


def list_lane_specs(db: Session, lane_id: str | None = None) -> list[LaneSpec]:
    return _list_records(db, LaneSpec, "lane_id", _clean_optional_text(lane_id))


def get_lane_spec(db: Session, lane_id: str, version: int) -> LaneSpec:
    return _get_record(db, LaneSpec, "lane_id", _clean_identifier(lane_id, "lane_id"), version)


def list_variable_registries(
    db: Session,
    variable_registry_id: str | None = None,
) -> list[VariableRegistry]:
    return _list_records(
        db,
        VariableRegistry,
        "variable_registry_id",
        _clean_optional_text(variable_registry_id),
    )


def get_variable_registry(
    db: Session,
    variable_registry_id: str,
    version: int,
) -> VariableRegistry:
    return _get_record(
        db,
        VariableRegistry,
        "variable_registry_id",
        _clean_identifier(variable_registry_id, "variable_registry_id"),
        version,
    )


def list_parameter_sets(db: Session, parameter_set_id: str | None = None) -> list[ParameterSet]:
    return _list_records(db, ParameterSet, "parameter_set_id", _clean_optional_text(parameter_set_id))


def get_parameter_set(db: Session, parameter_set_id: str, version: int) -> ParameterSet:
    return _get_record(
        db,
        ParameterSet,
        "parameter_set_id",
        _clean_identifier(parameter_set_id, "parameter_set_id"),
        version,
    )


def list_threshold_sets(db: Session, threshold_set_id: str | None = None) -> list[ThresholdSet]:
    return _list_records(db, ThresholdSet, "threshold_set_id", _clean_optional_text(threshold_set_id))


def get_threshold_set(db: Session, threshold_set_id: str, version: int) -> ThresholdSet:
    return _get_record(
        db,
        ThresholdSet,
        "threshold_set_id",
        _clean_identifier(threshold_set_id, "threshold_set_id"),
        version,
    )


def list_policy_bundles(db: Session, policy_bundle_id: str | None = None) -> list[PolicyBundle]:
    return _list_records(db, PolicyBundle, "policy_bundle_id", _clean_optional_text(policy_bundle_id))


def get_policy_bundle(db: Session, policy_bundle_id: str, version: int) -> PolicyBundle:
    return _get_record(
        db,
        PolicyBundle,
        "policy_bundle_id",
        _clean_identifier(policy_bundle_id, "policy_bundle_id"),
        version,
    )


def list_runtime_profiles(
    db: Session,
    runtime_profile_id: str | None = None,
) -> list[RuntimeProfile]:
    return _list_records(
        db,
        RuntimeProfile,
        "runtime_profile_id",
        _clean_optional_text(runtime_profile_id),
    )


def get_runtime_profile(db: Session, runtime_profile_id: str, version: int) -> RuntimeProfile:
    return _get_record(
        db,
        RuntimeProfile,
        "runtime_profile_id",
        _clean_identifier(runtime_profile_id, "runtime_profile_id"),
        version,
    )


def list_scope_registry(db: Session, scope_id: str | None = None) -> list[ScopeRegistry]:
    return _list_records(db, ScopeRegistry, "scope_id", _clean_optional_text(scope_id))


def get_scope_registry(db: Session, scope_id: str, version: int) -> ScopeRegistry:
    return _get_record(db, ScopeRegistry, "scope_id", _clean_identifier(scope_id, "scope_id"), version)


def list_migration_packages(
    db: Session,
    migration_id: str | None = None,
) -> list[MigrationPackage]:
    return _list_records(db, MigrationPackage, "migration_id", _clean_optional_text(migration_id))


def get_migration_package(db: Session, migration_id: str, version: int) -> MigrationPackage:
    return _get_record(
        db,
        MigrationPackage,
        "migration_id",
        _clean_identifier(migration_id, "migration_id"),
        version,
    )
