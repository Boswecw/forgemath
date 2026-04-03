from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.evaluation import (
    IncidentRecordCreate,
    IncidentRecordRead,
    InputBundleCreate,
    InputBundleRead,
    LaneEvaluationDetailRead,
    LaneEvaluationLifecycleRead,
    LaneEvaluationLifecycleTransitionCreate,
    LaneEvaluationLineageRead,
    LaneEvaluationRuntimeAdmissionRead,
    LaneEvaluationSummaryRead,
    ManualLaneEvaluationCreate,
    ReplayQueueEventCreate,
    ReplayQueueEventRead,
)
from app.schemas.execution import LaneExecutionCreate, LaneExecutionResultRead
from app.schemas.projection import (
    LaneEvaluationDetailModel,
    LaneEvaluationSummaryModel,
    LaneFactorInspectionModel,
    LaneReplayDiagnosticModel,
    LaneTraceInspectionModel,
)
from app.services import (
    execution_service,
    evaluation_service,
    lifecycle_service,
    projection_service,
    registry_service,
    runtime_admission_service,
)

router = APIRouter(prefix="/api/v1/forgemath", tags=["forgemath-evaluations"])


def _raise_http_error(exc: Exception) -> None:
    if isinstance(exc, registry_service.GovernanceNotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    if isinstance(exc, registry_service.GovernanceConflictError):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if isinstance(exc, registry_service.GovernanceValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    raise exc


@router.post("/input-bundles", response_model=InputBundleRead, status_code=status.HTTP_201_CREATED)
def create_input_bundle(body: InputBundleCreate, db: Session = Depends(get_db)) -> InputBundleRead:
    try:
        return evaluation_service.create_input_bundle(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/input-bundles", response_model=list[InputBundleRead])
def list_input_bundles(db: Session = Depends(get_db)) -> list[InputBundleRead]:
    return evaluation_service.list_input_bundles(db)


@router.get("/input-bundles/{input_bundle_id}", response_model=InputBundleRead)
def get_input_bundle(input_bundle_id: str, db: Session = Depends(get_db)) -> InputBundleRead:
    try:
        return evaluation_service.get_input_bundle(db, input_bundle_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/lane-evaluations",
    response_model=LaneEvaluationDetailRead,
    status_code=status.HTTP_201_CREATED,
)
def create_lane_evaluation(
    body: ManualLaneEvaluationCreate,
    db: Session = Depends(get_db),
) -> LaneEvaluationDetailRead:
    try:
        evaluation_service.create_manual_lane_evaluation(db, body)
        return evaluation_service.get_lane_evaluation_detail(db, body.lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/lane-executions",
    response_model=LaneExecutionResultRead,
    status_code=status.HTTP_201_CREATED,
)
def create_lane_execution(
    body: LaneExecutionCreate,
    db: Session = Depends(get_db),
) -> LaneExecutionResultRead:
    try:
        return execution_service.execute_lane(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/lane-evaluations", response_model=list[LaneEvaluationSummaryRead])
def list_lane_evaluations(db: Session = Depends(get_db)) -> list[LaneEvaluationSummaryRead]:
    return evaluation_service.list_lane_evaluations(db)


@router.get("/lane-evaluations/{lane_evaluation_id}", response_model=LaneEvaluationDetailRead)
def get_lane_evaluation(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneEvaluationDetailRead:
    try:
        return evaluation_service.get_lane_evaluation_detail(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get(
    "/lane-evaluations/{lane_evaluation_id}/summary",
    response_model=LaneEvaluationSummaryModel,
)
def get_lane_evaluation_summary_projection(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneEvaluationSummaryModel:
    try:
        return projection_service.get_lane_evaluation_summary_model(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get(
    "/lane-evaluations/{lane_evaluation_id}/detail",
    response_model=LaneEvaluationDetailModel,
)
def get_lane_evaluation_detail_projection(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneEvaluationDetailModel:
    try:
        return projection_service.get_lane_evaluation_detail_model(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get(
    "/lane-evaluations/{lane_evaluation_id}/factors",
    response_model=LaneFactorInspectionModel,
)
def get_lane_factor_projection(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneFactorInspectionModel:
    try:
        return projection_service.get_lane_factor_inspection_model(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get(
    "/lane-evaluations/{lane_evaluation_id}/trace",
    response_model=LaneTraceInspectionModel,
)
def get_lane_trace_projection(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneTraceInspectionModel:
    try:
        return projection_service.get_lane_trace_inspection_model(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get(
    "/lane-evaluations/{lane_evaluation_id}/replay-diagnostics",
    response_model=LaneReplayDiagnosticModel,
)
def get_lane_replay_diagnostic_projection(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneReplayDiagnosticModel:
    try:
        return projection_service.get_lane_replay_diagnostic_model(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get(
    "/lane-evaluations/{lane_evaluation_id}/lifecycle",
    response_model=LaneEvaluationLifecycleRead,
)
def get_lane_evaluation_lifecycle(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneEvaluationLifecycleRead:
    try:
        return lifecycle_service.get_lane_evaluation_lifecycle(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/lane-evaluations/{lane_evaluation_id}/lifecycle-transitions",
    response_model=LaneEvaluationLifecycleRead,
)
def transition_lane_evaluation_lifecycle(
    lane_evaluation_id: str,
    body: LaneEvaluationLifecycleTransitionCreate,
    db: Session = Depends(get_db),
) -> LaneEvaluationLifecycleRead:
    try:
        return lifecycle_service.apply_lifecycle_transition(db, lane_evaluation_id, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get(
    "/lane-evaluations/{lane_evaluation_id}/lineage",
    response_model=LaneEvaluationLineageRead,
)
def get_lane_evaluation_lineage(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneEvaluationLineageRead:
    try:
        return lifecycle_service.get_lane_evaluation_lineage(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get(
    "/lane-evaluations/{lane_evaluation_id}/runtime-admission",
    response_model=LaneEvaluationRuntimeAdmissionRead,
)
def get_lane_evaluation_runtime_admission(
    lane_evaluation_id: str,
    db: Session = Depends(get_db),
) -> LaneEvaluationRuntimeAdmissionRead:
    try:
        return runtime_admission_service.get_runtime_admission(db, lane_evaluation_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post(
    "/replay-queue-events",
    response_model=ReplayQueueEventRead,
    status_code=status.HTTP_201_CREATED,
)
def create_replay_queue_event(
    body: ReplayQueueEventCreate,
    db: Session = Depends(get_db),
) -> ReplayQueueEventRead:
    try:
        return evaluation_service.create_replay_queue_event(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/replay-queue-events", response_model=list[ReplayQueueEventRead])
def list_replay_queue_events(db: Session = Depends(get_db)) -> list[ReplayQueueEventRead]:
    return evaluation_service.list_replay_queue_events(db)


@router.get("/replay-queue-events/{replay_event_id}", response_model=ReplayQueueEventRead)
def get_replay_queue_event(
    replay_event_id: str,
    db: Session = Depends(get_db),
) -> ReplayQueueEventRead:
    try:
        return evaluation_service.get_replay_queue_event(db, replay_event_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.post("/incidents", response_model=IncidentRecordRead, status_code=status.HTTP_201_CREATED)
def create_incident_record(
    body: IncidentRecordCreate,
    db: Session = Depends(get_db),
) -> IncidentRecordRead:
    try:
        return evaluation_service.create_incident_record(db, body)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)


@router.get("/incidents", response_model=list[IncidentRecordRead])
def list_incident_records(db: Session = Depends(get_db)) -> list[IncidentRecordRead]:
    return evaluation_service.list_incident_records(db)


@router.get("/incidents/{incident_id}", response_model=IncidentRecordRead)
def get_incident_record(incident_id: str, db: Session = Depends(get_db)) -> IncidentRecordRead:
    try:
        return evaluation_service.get_incident_record(db, incident_id)
    except registry_service.GovernanceError as exc:
        _raise_http_error(exc)
