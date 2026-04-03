from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.evaluation import (
    IncidentRecordCreate,
    IncidentRecordRead,
    InputBundleCreate,
    InputBundleRead,
    LaneEvaluationCreate,
    LaneEvaluationDetailRead,
    LaneEvaluationSummaryRead,
    ReplayQueueEventCreate,
    ReplayQueueEventRead,
)
from app.services import evaluation_service, registry_service

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
    body: LaneEvaluationCreate,
    db: Session = Depends(get_db),
) -> LaneEvaluationDetailRead:
    try:
        evaluation_service.create_lane_evaluation(db, body)
        return evaluation_service.get_lane_evaluation_detail(db, body.lane_evaluation_id)
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
