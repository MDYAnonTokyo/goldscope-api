from datetime import UTC, date, datetime

from sqlalchemy import Date, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from goldscope.db.base import Base


class GoldPrice(Base):
    __tablename__ = "gold_prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    price_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    usd_oz: Mapped[float] = mapped_column(Float)
    gbp_oz: Mapped[float | None] = mapped_column(Float, nullable=True)
    eur_oz: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_name: Mapped[str] = mapped_column(String(255))
    source_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
