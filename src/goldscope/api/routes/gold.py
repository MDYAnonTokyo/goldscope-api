from datetime import date

from fastapi import APIRouter, Query

from goldscope.api.deps import DbSession
from goldscope.schemas.gold import (
    AnomaliesResponse,
    DrawdownResponse,
    GoldLatestResponse,
    GoldPriceListResponse,
    RegimeResponse,
    ReturnsResponse,
    SummaryResponse,
    VolatilityResponse,
)
from goldscope.services import gold as gold_service

router = APIRouter()


@router.get("/prices", response_model=GoldPriceListResponse)
def list_gold_prices(
    db: DbSession,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=120, ge=0, le=5000),
) -> GoldPriceListResponse:
    items = gold_service.get_prices(db, start_date=start_date, end_date=end_date, limit=limit)
    return GoldPriceListResponse(
        count=len(items),
        start_date=items[0].price_date if items else start_date,
        end_date=items[-1].price_date if items else end_date,
        items=items,
    )


@router.get("/prices/latest", response_model=GoldLatestResponse)
def latest_gold_price(db: DbSession) -> GoldLatestResponse:
    return GoldLatestResponse(item=gold_service.get_latest_price(db))


@router.get("/analytics/summary", response_model=SummaryResponse)
def gold_summary(
    db: DbSession,
    start_date: date | None = None,
    end_date: date | None = None,
) -> SummaryResponse:
    return gold_service.get_summary(db, start_date=start_date, end_date=end_date)


@router.get("/analytics/returns", response_model=ReturnsResponse)
def gold_returns(db: DbSession) -> ReturnsResponse:
    return gold_service.get_returns(db)


@router.get("/analytics/volatility", response_model=VolatilityResponse)
def gold_volatility(
    db: DbSession,
    window_points: int = Query(default=12, ge=2, le=120),
) -> VolatilityResponse:
    return gold_service.get_volatility(db, window_points=window_points)


@router.get("/analytics/drawdown", response_model=DrawdownResponse)
def gold_drawdown(
    db: DbSession,
    start_date: date | None = None,
    end_date: date | None = None,
) -> DrawdownResponse:
    return gold_service.get_drawdown(db, start_date=start_date, end_date=end_date)


@router.get("/analytics/anomalies", response_model=AnomaliesResponse)
def gold_anomalies(
    db: DbSession,
    start_date: date | None = None,
    end_date: date | None = None,
    threshold: float = Query(default=1.5, ge=0.5, le=5.0),
) -> AnomaliesResponse:
    return gold_service.get_anomalies(
        db,
        start_date=start_date,
        end_date=end_date,
        threshold=threshold,
    )


@router.get("/analytics/regime", response_model=RegimeResponse)
def gold_regime(
    db: DbSession,
    short_window: int = Query(default=3, ge=2, le=12),
    long_window: int = Query(default=6, ge=3, le=24),
) -> RegimeResponse:
    return gold_service.get_regime(db, short_window=short_window, long_window=long_window)
