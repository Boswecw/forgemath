from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import (
    LaneFamily,
    MigrationApprovalState,
    MigrationClass,
    MigrationCompatibilityClass,
    PolicyBundleKind,
    ScopeClass,
    TraceTier,
    enum_values,
)


def new_uuid() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _sql_in(enum_cls: type) -> str:
    return "(" + ", ".join(f"'{value}'" for value in enum_values(enum_cls)) + ")"


class ImmutablePersistedMixin:
    __abstract__ = True

    @classmethod
    def lifecycle_mutable_fields(cls) -> set[str]:
        return set()


class GovernedVersionedMixin(ImmutablePersistedMixin):
    __abstract__ = True

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    superseded_by_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    retired_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    created_by: Mapped[str | None] = mapped_column(String(255), nullable=True)

    @classmethod
    def lifecycle_mutable_fields(cls) -> set[str]:
        return {"superseded_at", "superseded_by_id", "retired_reason"}


class LaneSpec(GovernedVersionedMixin, Base):
    __tablename__ = "forgemath_lane_specs"

    lane_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    lane_family: Mapped[str] = mapped_column(String(32), nullable=False)
    trace_tier: Mapped[str] = mapped_column(String(32), nullable=False)
    is_admissible: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint("lane_id", "version", name="uq_forgemath_lane_specs_lane_id_version"),
        CheckConstraint("version > 0", name="ck_forgemath_lane_specs_version_positive"),
        CheckConstraint(
            f"lane_family IN {_sql_in(LaneFamily)}",
            name="ck_forgemath_lane_specs_lane_family",
        ),
        CheckConstraint(
            f"trace_tier IN {_sql_in(TraceTier)}",
            name="ck_forgemath_lane_specs_trace_tier",
        ),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name="ck_forgemath_lane_specs_supersession_consistency",
        ),
    )


class VariableRegistry(GovernedVersionedMixin, Base):
    __tablename__ = "forgemath_variable_registry"

    variable_registry_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "variable_registry_id",
            "version",
            name="uq_forgemath_variable_registry_identity_version",
        ),
        CheckConstraint("version > 0", name="ck_forgemath_variable_registry_version_positive"),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name="ck_forgemath_variable_registry_supersession_consistency",
        ),
    )


class ParameterSet(GovernedVersionedMixin, Base):
    __tablename__ = "forgemath_parameter_sets"

    parameter_set_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    lane_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "parameter_set_id",
            "version",
            name="uq_forgemath_parameter_sets_identity_version",
        ),
        CheckConstraint("version > 0", name="ck_forgemath_parameter_sets_version_positive"),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name="ck_forgemath_parameter_sets_supersession_consistency",
        ),
    )


class ThresholdSet(GovernedVersionedMixin, Base):
    __tablename__ = "forgemath_threshold_sets"

    threshold_set_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    lane_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "threshold_set_id",
            "version",
            name="uq_forgemath_threshold_sets_identity_version",
        ),
        CheckConstraint("version > 0", name="ck_forgemath_threshold_sets_version_positive"),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name="ck_forgemath_threshold_sets_supersession_consistency",
        ),
    )


class PolicyBundle(GovernedVersionedMixin, Base):
    __tablename__ = "forgemath_policy_bundles"

    policy_bundle_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    policy_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    lane_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "policy_bundle_id",
            "version",
            name="uq_forgemath_policy_bundles_identity_version",
        ),
        CheckConstraint("version > 0", name="ck_forgemath_policy_bundles_version_positive"),
        CheckConstraint(
            f"policy_kind IN {_sql_in(PolicyBundleKind)}",
            name="ck_forgemath_policy_bundles_policy_kind",
        ),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name="ck_forgemath_policy_bundles_supersession_consistency",
        ),
    )


class RuntimeProfile(GovernedVersionedMixin, Base):
    __tablename__ = "forgemath_runtime_profiles"

    runtime_profile_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    numeric_precision_mode: Mapped[str] = mapped_column(String(64), nullable=False)
    rounding_mode: Mapped[str] = mapped_column(String(64), nullable=False)
    sort_policy_id: Mapped[str] = mapped_column(String(255), nullable=False)
    serialization_policy_id: Mapped[str] = mapped_column(String(255), nullable=False)
    timezone_policy: Mapped[str] = mapped_column(String(64), nullable=False)
    seed_policy: Mapped[str] = mapped_column(String(255), nullable=False)
    non_determinism_allowed_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint(
            "runtime_profile_id",
            "version",
            name="uq_forgemath_runtime_profiles_identity_version",
        ),
        CheckConstraint("version > 0", name="ck_forgemath_runtime_profiles_version_positive"),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name="ck_forgemath_runtime_profiles_supersession_consistency",
        ),
    )


class ScopeRegistry(GovernedVersionedMixin, Base):
    __tablename__ = "forgemath_scope_registry"

    scope_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    scope_class: Mapped[str] = mapped_column(String(32), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)

    __table_args__ = (
        UniqueConstraint("scope_id", "version", name="uq_forgemath_scope_registry_identity_version"),
        CheckConstraint("version > 0", name="ck_forgemath_scope_registry_version_positive"),
        CheckConstraint(
            f"scope_class IN {_sql_in(ScopeClass)}",
            name="ck_forgemath_scope_registry_scope_class",
        ),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name="ck_forgemath_scope_registry_supersession_consistency",
        ),
    )


class MigrationPackage(GovernedVersionedMixin, Base):
    __tablename__ = "forgemath_migration_packages"

    migration_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    migration_class: Mapped[str] = mapped_column(String(48), nullable=False)
    source_versions: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    target_versions: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    affected_artifacts: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    migration_logic_summary: Mapped[str] = mapped_column(Text, nullable=False)
    compatibility_class_after_migration: Mapped[str] = mapped_column(String(48), nullable=False)
    rollback_plan: Mapped[str] = mapped_column(Text, nullable=False)
    replay_impact_statement: Mapped[str] = mapped_column(Text, nullable=False)
    audit_only_impact_statement: Mapped[str] = mapped_column(Text, nullable=False)
    approval_state: Mapped[str] = mapped_column(String(32), nullable=False)

    __table_args__ = (
        UniqueConstraint("migration_id", "version", name="uq_forgemath_migration_packages_identity_version"),
        CheckConstraint("version > 0", name="ck_forgemath_migration_packages_version_positive"),
        CheckConstraint(
            f"migration_class IN {_sql_in(MigrationClass)}",
            name="ck_forgemath_migration_packages_migration_class",
        ),
        CheckConstraint(
            f"compatibility_class_after_migration IN {_sql_in(MigrationCompatibilityClass)}",
            name="ck_forgemath_migration_packages_compatibility_class",
        ),
        CheckConstraint(
            f"approval_state IN {_sql_in(MigrationApprovalState)}",
            name="ck_forgemath_migration_packages_approval_state",
        ),
        CheckConstraint(
            "superseded_by_id IS NULL OR superseded_at IS NOT NULL",
            name="ck_forgemath_migration_packages_supersession_consistency",
        ),
    )
