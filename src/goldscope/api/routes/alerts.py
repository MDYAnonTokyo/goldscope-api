from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from goldscope.api.deps import DbSession, get_current_user
from goldscope.models.user import User
from goldscope.schemas.alerts import AlertCreate, AlertListResponse, AlertRead, AlertUpdate
from goldscope.services import alerts as alert_service

router = APIRouter()

CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("", response_model=AlertListResponse)
def list_user_alerts(db: DbSession, current_user: CurrentUser) -> AlertListResponse:
    items = alert_service.list_alerts(db, current_user=current_user)
    return AlertListResponse(count=len(items), items=items)


@router.post("", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(payload: AlertCreate, db: DbSession, current_user: CurrentUser) -> AlertRead:
    return alert_service.create_alert(db, payload=payload, current_user=current_user)


@router.get("/{alert_id}", response_model=AlertRead)
def get_alert(alert_id: int, db: DbSession, current_user: CurrentUser) -> AlertRead:
    return alert_service.get_alert(db, alert_id=alert_id, current_user=current_user)


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(
    alert_id: int,
    payload: AlertUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> AlertRead:
    alert = alert_service.get_alert(db, alert_id=alert_id, current_user=current_user)
    return alert_service.update_alert(db, alert=alert, payload=payload)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert(alert_id: int, db: DbSession, current_user: CurrentUser) -> Response:
    alert = alert_service.get_alert(db, alert_id=alert_id, current_user=current_user)
    alert_service.delete_alert(db, alert=alert)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
