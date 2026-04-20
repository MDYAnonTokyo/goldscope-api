from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from goldscope.models.price_alert import PriceAlert
from goldscope.models.user import User
from goldscope.schemas.alerts import AlertCreate, AlertUpdate


def list_alerts(db: Session, *, current_user: User) -> list[PriceAlert]:
    stmt = (
        select(PriceAlert)
        .where(PriceAlert.user_id == current_user.id)
        .order_by(PriceAlert.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def get_alert(db: Session, *, alert_id: int, current_user: User) -> PriceAlert:
    stmt = select(PriceAlert).where(
        PriceAlert.id == alert_id,
        PriceAlert.user_id == current_user.id,
    )
    alert = db.scalar(stmt)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found.",
        )
    return alert


def create_alert(db: Session, *, payload: AlertCreate, current_user: User) -> PriceAlert:
    alert = PriceAlert(user_id=current_user.id, **payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def update_alert(
    db: Session,
    *,
    alert: PriceAlert,
    payload: AlertUpdate,
) -> PriceAlert:
    updates = payload.model_dump(exclude_unset=True)
    for field_name, field_value in updates.items():
        setattr(alert, field_name, field_value)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def delete_alert(db: Session, *, alert: PriceAlert) -> None:
    db.delete(alert)
    db.commit()
