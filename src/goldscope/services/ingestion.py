import csv
from datetime import UTC, date, datetime
from pathlib import Path

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from goldscope.core.config import get_settings
from goldscope.models.gold_price import GoldPrice


def import_gold_prices_from_csv(*, db: Session, csv_path: Path, replace_existing: bool = False) -> int:
    settings = get_settings()
    rows_to_add: list[GoldPrice] = []

    if replace_existing:
        db.execute(delete(GoldPrice))

    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            price_date = date.fromisoformat(row["Date"])
            price_value = float(row["Price"])
            if not replace_existing:
                existing = db.scalar(select(GoldPrice).where(GoldPrice.price_date == price_date))
                if existing:
                    continue
            rows_to_add.append(
                GoldPrice(
                    price_date=price_date,
                    usd_oz=price_value,
                    gbp_oz=None,
                    eur_oz=None,
                    source_name=settings.gold_prices_source_name,
                    source_date=datetime.now(UTC),
                )
            )

    if rows_to_add:
        db.add_all(rows_to_add)
        db.commit()

    return len(rows_to_add)
