from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.governance import (
    LaneSpecCreate,
    LaneSpecRead,
    MigrationPackageCreate,
    MigrationPackageRead,
    ParameterSetCreate,
    ParameterSetRead,
    PolicyBundleCreate,
    PolicyBundleRead,
    RuntimeProfileCreate,
    RuntimeProfileRead,
    ScopeRegistryCreate,
    ScopeRegistryRead,
    ThresholdSetCreate,
    ThresholdSetRead,
    VariableRegistryCreate,
    VariableRegistryRead,
)
from app.services import registry_service

router = APIRouter(prefix="/api/v1/forgemath/governance", tags=["forgemath-governance"])


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, registry_service.GovernanceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, registry_service.GovernanceConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, registry_service.GovernanceValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    raise exc


@router.post("/lane-specs", response_model=LaneSpecRead, status_code=status.HTTP_201_CREATED)
def create_lane_spec(body: LaneSpecCreate, db: Session = Depends(get_db)) -> LaneSpecRead:
    try:
        return registry_service.create_lane_spec(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/lane-specs", response_model=list[LaneSpecRead])
def list_lane_specs(
    lane_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[LaneSpecRead]:
    return registry_service.list_lane_specs(db, lane_id)


@router.get("/lane-specs/{lane_id}/versions/{version}", response_model=LaneSpecRead)
def get_lane_spec(lane_id: str, version: int, db: Session = Depends(get_db)) -> LaneSpecRead:
    try:
        return registry_service.get_lane_spec(db, lane_id, version)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/variable-registries",
    response_model=VariableRegistryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_variable_registry(
    body: VariableRegistryCreate,
    db: Session = Depends(get_db),
) -> VariableRegistryRead:
    try:
        return registry_service.create_variable_registry(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/variable-registries", response_model=list[VariableRegistryRead])
def list_variable_registries(
    variable_registry_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[VariableRegistryRead]:
    return registry_service.list_variable_registries(db, variable_registry_id)


@router.get(
    "/variable-registries/{variable_registry_id}/versions/{version}",
    response_model=VariableRegistryRead,
)
def get_variable_registry(
    variable_registry_id: str,
    version: int,
    db: Session = Depends(get_db),
) -> VariableRegistryRead:
    try:
        return registry_service.get_variable_registry(db, variable_registry_id, version)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/parameter-sets",
    response_model=ParameterSetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_parameter_set(
    body: ParameterSetCreate,
    db: Session = Depends(get_db),
) -> ParameterSetRead:
    try:
        return registry_service.create_parameter_set(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/parameter-sets", response_model=list[ParameterSetRead])
def list_parameter_sets(
    parameter_set_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ParameterSetRead]:
    return registry_service.list_parameter_sets(db, parameter_set_id)


@router.get("/parameter-sets/{parameter_set_id}/versions/{version}", response_model=ParameterSetRead)
def get_parameter_set(
    parameter_set_id: str,
    version: int,
    db: Session = Depends(get_db),
) -> ParameterSetRead:
    try:
        return registry_service.get_parameter_set(db, parameter_set_id, version)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/threshold-sets",
    response_model=ThresholdSetRead,
    status_code=status.HTTP_201_CREATED,
)
def create_threshold_set(
    body: ThresholdSetCreate,
    db: Session = Depends(get_db),
) -> ThresholdSetRead:
    try:
        return registry_service.create_threshold_set(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/threshold-sets", response_model=list[ThresholdSetRead])
def list_threshold_sets(
    threshold_set_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ThresholdSetRead]:
    return registry_service.list_threshold_sets(db, threshold_set_id)


@router.get("/threshold-sets/{threshold_set_id}/versions/{version}", response_model=ThresholdSetRead)
def get_threshold_set(
    threshold_set_id: str,
    version: int,
    db: Session = Depends(get_db),
) -> ThresholdSetRead:
    try:
        return registry_service.get_threshold_set(db, threshold_set_id, version)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/policy-bundles",
    response_model=PolicyBundleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_policy_bundle(
    body: PolicyBundleCreate,
    db: Session = Depends(get_db),
) -> PolicyBundleRead:
    try:
        return registry_service.create_policy_bundle(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/policy-bundles", response_model=list[PolicyBundleRead])
def list_policy_bundles(
    policy_bundle_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[PolicyBundleRead]:
    return registry_service.list_policy_bundles(db, policy_bundle_id)


@router.get("/policy-bundles/{policy_bundle_id}/versions/{version}", response_model=PolicyBundleRead)
def get_policy_bundle(
    policy_bundle_id: str,
    version: int,
    db: Session = Depends(get_db),
) -> PolicyBundleRead:
    try:
        return registry_service.get_policy_bundle(db, policy_bundle_id, version)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/runtime-profiles",
    response_model=RuntimeProfileRead,
    status_code=status.HTTP_201_CREATED,
)
def create_runtime_profile(
    body: RuntimeProfileCreate,
    db: Session = Depends(get_db),
) -> RuntimeProfileRead:
    try:
        return registry_service.create_runtime_profile(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/runtime-profiles", response_model=list[RuntimeProfileRead])
def list_runtime_profiles(
    runtime_profile_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[RuntimeProfileRead]:
    return registry_service.list_runtime_profiles(db, runtime_profile_id)


@router.get(
    "/runtime-profiles/{runtime_profile_id}/versions/{version}",
    response_model=RuntimeProfileRead,
)
def get_runtime_profile(
    runtime_profile_id: str,
    version: int,
    db: Session = Depends(get_db),
) -> RuntimeProfileRead:
    try:
        return registry_service.get_runtime_profile(db, runtime_profile_id, version)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post("/scopes", response_model=ScopeRegistryRead, status_code=status.HTTP_201_CREATED)
def create_scope_registry(
    body: ScopeRegistryCreate,
    db: Session = Depends(get_db),
) -> ScopeRegistryRead:
    try:
        return registry_service.create_scope_registry(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/scopes", response_model=list[ScopeRegistryRead])
def list_scope_registry(
    scope_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ScopeRegistryRead]:
    return registry_service.list_scope_registry(db, scope_id)


@router.get("/scopes/{scope_id}/versions/{version}", response_model=ScopeRegistryRead)
def get_scope_registry(scope_id: str, version: int, db: Session = Depends(get_db)) -> ScopeRegistryRead:
    try:
        return registry_service.get_scope_registry(db, scope_id, version)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/migration-packages",
    response_model=MigrationPackageRead,
    status_code=status.HTTP_201_CREATED,
)
def create_migration_package(
    body: MigrationPackageCreate,
    db: Session = Depends(get_db),
) -> MigrationPackageRead:
    try:
        return registry_service.create_migration_package(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/migration-packages", response_model=list[MigrationPackageRead])
def list_migration_packages(
    migration_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[MigrationPackageRead]:
    return registry_service.list_migration_packages(db, migration_id)


@router.get("/migration-packages/{migration_id}/versions/{version}", response_model=MigrationPackageRead)
def get_migration_package(
    migration_id: str,
    version: int,
    db: Session = Depends(get_db),
) -> MigrationPackageRead:
    try:
        return registry_service.get_migration_package(db, migration_id, version)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)

