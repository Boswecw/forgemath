from __future__ import annotations

from datetime import datetime
from hashlib import sha256
import json
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.enums import (
    DeterminismSensitiveArtifact,
    LaneFamily,
    MigrationApprovalState,
    MigrationClass,
    MigrationCompatibilityClass,
    PolicyBundleKind,
    ScopeClass,
    TraceTier,
)


class GovernanceReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class VersionedCreateBase(BaseModel):
    version: int = Field(gt=0)
    effective_from: datetime
    created_by: str | None = Field(default=None, max_length=255)
    supersedes_version: int | None = Field(default=None, gt=0)
    retired_reason: str | None = None


class VersionedReadBase(GovernanceReadModel):
    id: str
    version: int
    payload_hash: str
    effective_from: datetime
    superseded_at: datetime | None
    superseded_by_id: str | None
    retired_reason: str | None
    created_at: datetime
    created_by: str | None


class LaneSpecCreate(VersionedCreateBase):
    lane_id: str = Field(min_length=1, max_length=255)
    lane_family: LaneFamily
    trace_tier: TraceTier
    is_admissible: bool = True
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("payload must not be empty.")
        return value


class LaneSpecRead(VersionedReadBase):
    lane_id: str
    lane_family: LaneFamily
    trace_tier: TraceTier
    is_admissible: bool
    payload: dict[str, Any]


class VariableRegistryCreate(VersionedCreateBase):
    variable_registry_id: str = Field(min_length=1, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("payload must not be empty.")
        return value


class VariableRegistryRead(VersionedReadBase):
    variable_registry_id: str
    payload: dict[str, Any]


class ParameterSetCreate(VersionedCreateBase):
    parameter_set_id: str = Field(min_length=1, max_length=255)
    lane_id: str | None = Field(default=None, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("payload must not be empty.")
        return value


class ParameterSetRead(VersionedReadBase):
    parameter_set_id: str
    lane_id: str | None
    payload: dict[str, Any]


class ThresholdSetCreate(VersionedCreateBase):
    threshold_set_id: str = Field(min_length=1, max_length=255)
    lane_id: str | None = Field(default=None, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("payload must not be empty.")
        return value


class ThresholdSetRead(VersionedReadBase):
    threshold_set_id: str
    lane_id: str | None
    payload: dict[str, Any]


class PolicyBundleCreate(VersionedCreateBase):
    policy_bundle_id: str = Field(min_length=1, max_length=255)
    policy_kind: PolicyBundleKind
    lane_id: str | None = Field(default=None, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("payload must not be empty.")
        return value


class PolicyBundleRead(VersionedReadBase):
    policy_bundle_id: str
    policy_kind: PolicyBundleKind
    lane_id: str | None
    payload: dict[str, Any]


class RuntimeProfileCreate(VersionedCreateBase):
    runtime_profile_id: str = Field(min_length=1, max_length=255)
    numeric_precision_mode: str = Field(min_length=1, max_length=64)
    rounding_mode: str = Field(min_length=1, max_length=64)
    sort_policy_id: str = Field(min_length=1, max_length=255)
    serialization_policy_id: str = Field(min_length=1, max_length=255)
    timezone_policy: str = Field(min_length=1, max_length=64)
    seed_policy: str = Field(min_length=1, max_length=255)
    non_determinism_allowed_flag: bool = False


class RuntimeProfileRead(VersionedReadBase):
    runtime_profile_id: str
    numeric_precision_mode: str
    rounding_mode: str
    sort_policy_id: str
    serialization_policy_id: str
    timezone_policy: str
    seed_policy: str
    non_determinism_allowed_flag: bool


class ScopeRegistryCreate(VersionedCreateBase):
    scope_id: str = Field(min_length=1, max_length=255)
    scope_class: ScopeClass
    display_name: str = Field(min_length=1, max_length=255)
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("payload must not be empty.")
        return value


class ScopeRegistryRead(VersionedReadBase):
    scope_id: str
    scope_class: ScopeClass
    display_name: str
    payload: dict[str, Any]


class MigrationPackageCreate(VersionedCreateBase):
    migration_id: str = Field(min_length=1, max_length=255)
    migration_class: MigrationClass
    source_versions: dict[str, Any] = Field(default_factory=dict)
    target_versions: dict[str, Any] = Field(default_factory=dict)
    affected_artifacts: list[str] = Field(default_factory=list)
    determinism_sensitive_artifacts: list[DeterminismSensitiveArtifact] = Field(default_factory=list)
    migration_logic_summary: str = Field(min_length=1)
    compatibility_class_after_migration: MigrationCompatibilityClass
    rollback_plan: str = Field(min_length=1)
    replay_impact_statement: str = Field(min_length=1)
    audit_only_impact_statement: str = Field(min_length=1)
    approval_state: MigrationApprovalState

    @field_validator("source_versions", "target_versions")
    @classmethod
    def validate_version_maps(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("version maps must not be empty.")
        return value

    @field_validator("affected_artifacts")
    @classmethod
    def validate_affected_artifacts(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("affected_artifacts must not be empty.")
        return value

    @field_validator("determinism_sensitive_artifacts")
    @classmethod
    def validate_determinism_sensitive_artifacts(
        cls,
        value: list[DeterminismSensitiveArtifact],
    ) -> list[DeterminismSensitiveArtifact]:
        if len(value) != len(set(value)):
            raise ValueError("determinism_sensitive_artifacts must be unique.")
        return value

    @model_validator(mode="after")
    def validate_determinism_sensitive_posture(self) -> "MigrationPackageCreate":
        determinism_sensitive_classes = {
            MigrationClass.NUMERIC_SERIALIZATION_MIGRATION,
            MigrationClass.ARTIFACT_HASHING_MIGRATION,
            MigrationClass.TRACE_HASHING_MIGRATION,
            MigrationClass.COMPATIBILITY_INTERPRETATION_MIGRATION,
            MigrationClass.PROJECTION_COMPATIBILITY_MIGRATION,
        }
        is_sensitive_class = self.migration_class in determinism_sensitive_classes
        has_sensitive_artifacts = bool(self.determinism_sensitive_artifacts)

        if is_sensitive_class and not has_sensitive_artifacts:
            raise ValueError(
                "determinism-sensitive migration classes require determinism_sensitive_artifacts."
            )
        if not is_sensitive_class and has_sensitive_artifacts:
            raise ValueError(
                "determinism_sensitive_artifacts may only be declared for determinism-sensitive migration classes."
            )
        if has_sensitive_artifacts and self.compatibility_class_after_migration == MigrationCompatibilityClass.HARD_COMPATIBLE:
            raise ValueError(
                "determinism-sensitive migrations may not declare compatibility_class_after_migration=hard_compatible."
            )
        return self


class MigrationPackageRead(VersionedReadBase):
    migration_id: str
    migration_class: MigrationClass
    source_versions: dict[str, Any]
    target_versions: dict[str, Any]
    affected_artifacts: list[str]
    determinism_sensitive_artifacts: list[DeterminismSensitiveArtifact]
    migration_logic_summary: str
    compatibility_class_after_migration: MigrationCompatibilityClass
    rollback_plan: str
    replay_impact_statement: str
    audit_only_impact_statement: str
    approval_state: MigrationApprovalState


class CompatibilityTuple(BaseModel):
    lane_spec_version: int = Field(gt=0)
    variable_registry_version: int = Field(gt=0)
    parameter_set_version: int = Field(gt=0)
    threshold_registry_version: int = Field(gt=0)
    prior_registry_version: int | None = Field(default=None, gt=0)
    decay_registry_version: int | None = Field(default=None, gt=0)
    null_policy_version: int = Field(gt=0)
    degraded_mode_policy_version: int = Field(gt=0)
    trace_schema_version: int = Field(gt=0)
    projection_schema_version: int = Field(gt=0)
    submodule_build_version: str = Field(min_length=1, max_length=255)

    def canonical_hash(self) -> str:
        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()
