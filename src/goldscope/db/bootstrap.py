from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from goldscope.core.config import get_settings
from goldscope.db.base import Base
from goldscope.db.session import get_engine, get_session_factory
from goldscope.models.gold_price import GoldPrice
from goldscope.services.ingestion import import_gold_prices_from_csv


def bootstrap_database() -> None:
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    settings = get_settings()
    csv_path = settings.default_gold_prices_csv
    if not csv_path.exists():
        return

    session_factory = get_session_factory()
    with session_factory() as db:
        if _database_has_prices(db):
            return
        import_gold_prices_from_csv(db=db, csv_path=csv_path)


def _database_has_prices(db: Session) -> bool:
    return db.scalar(select(GoldPrice.id).limit(1)) is not None
