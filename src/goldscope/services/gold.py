import math
import statistics
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from goldscope.models.gold_price import GoldPrice
from goldscope.schemas.gold import (
    AnomaliesResponse,
    AnomalyRead,
    DrawdownResponse,
    RegimeResponse,
    ReturnMetric,
    ReturnsResponse,
    SummaryResponse,
    VolatilityResponse,
)


def get_prices(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 120,
) -> list[GoldPrice]:
    stmt = select(GoldPrice).order_by(GoldPrice.price_date.asc())
    if start_date:
        stmt = stmt.where(GoldPrice.price_date >= start_date)
    if end_date:
        stmt = stmt.where(GoldPrice.price_date <= end_date)
    if limit:
        stmt = stmt.limit(limit)
    items = list(db.scalars(stmt).all())
    return items


def get_latest_price(db: Session) -> GoldPrice:
    stmt = select(GoldPrice).order_by(GoldPrice.price_date.desc()).limit(1)
    latest = db.scalar(stmt)
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No gold price data is available.",
        )
    return latest


def get_summary(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> SummaryResponse:
    prices = _require_prices(db=db, start_date=start_date, end_date=end_date)
    values = [item.usd_oz for item in prices]
    first_value = values[0]
    latest_value = values[-1]
    percent_change = ((latest_value - first_value) / first_value) * 100 if first_value else 0.0
    return SummaryResponse(
        start_date=prices[0].price_date,
        end_date=prices[-1].price_date,
        observation_count=len(prices),
        observation_frequency="monthly",
        latest_price=round(latest_value, 2),
        latest_date=prices[-1].price_date,
        min_price=round(min(values), 2),
        max_price=round(max(values), 2),
        average_price=round(sum(values) / len(values), 2),
        absolute_change=round(latest_value - first_value, 2),
        percent_change=round(percent_change, 2),
    )


def get_returns(db: Session) -> ReturnsResponse:
    prices = _require_prices(db=db)
    latest = prices[-1]
    latest_price = latest.usd_oz
    lookbacks = [
        ("7d", 7),
        ("30d", 30),
        ("90d", 90),
        ("1y", 365),
    ]
    items: list[ReturnMetric] = []
    for label, days in lookbacks:
        target_date = date.fromordinal(latest.price_date.toordinal() - days)
        matched = _find_latest_on_or_before(prices, target_date)
        if matched is None:
            continue
        absolute_return = latest_price - matched.usd_oz
        percent_return = ((latest_price - matched.usd_oz) / matched.usd_oz) * 100 if matched.usd_oz else 0.0
        items.append(
            ReturnMetric(
                period_label=label,
                lookback_days=days,
                matched_date=matched.price_date,
                matched_price=round(matched.usd_oz, 2),
                latest_price=round(latest_price, 2),
                absolute_return=round(absolute_return, 2),
                percent_return=round(percent_return, 2),
            )
        )
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough gold price history to compute returns.",
        )
    return ReturnsResponse(
        as_of_date=latest.price_date,
        observation_frequency="monthly",
        items=items,
    )


def get_volatility(db: Session, *, window_points: int = 12) -> VolatilityResponse:
    prices = _require_prices(db=db)
    returns = _pct_returns(prices)
    rolling_returns = returns[-window_points:] if len(returns) > window_points else returns
    if len(rolling_returns) < 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough gold price history to compute volatility.",
        )
    stdev = statistics.stdev(rolling_returns)
    annualized = stdev * math.sqrt(12)
    return VolatilityResponse(
        as_of_date=prices[-1].price_date,
        observation_frequency="monthly",
        window_points=len(rolling_returns),
        annualized_volatility=round(annualized * 100, 2),
        return_count=len(rolling_returns),
    )


def get_drawdown(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
) -> DrawdownResponse:
    prices = _require_prices(db=db, start_date=start_date, end_date=end_date)
    peak_price = prices[0].usd_oz
    peak_date = prices[0].price_date
    trough_price = prices[0].usd_oz
    trough_date = prices[0].price_date
    recovery_date: date | None = None
    max_drawdown_pct = 0.0

    for item in prices:
        if item.usd_oz > peak_price:
            peak_price = item.usd_oz
            peak_date = item.price_date
        current_drawdown = ((item.usd_oz - peak_price) / peak_price) * 100
        if current_drawdown < max_drawdown_pct:
            max_drawdown_pct = current_drawdown
            trough_price = item.usd_oz
            trough_date = item.price_date

    for item in prices:
        if item.price_date > trough_date and item.usd_oz >= peak_price:
            recovery_date = item.price_date
            break

    return DrawdownResponse(
        start_date=prices[0].price_date,
        end_date=prices[-1].price_date,
        max_drawdown_pct=round(max_drawdown_pct, 2),
        peak_date=peak_date,
        trough_date=trough_date,
        recovery_date=recovery_date,
    )


def get_anomalies(
    db: Session,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    threshold: float = 1.5,
) -> AnomaliesResponse:
    prices = _require_prices(db=db, start_date=start_date, end_date=end_date)
    returns = _pct_returns(prices)
    if len(returns) < 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough gold price history to detect anomalies.",
        )
    mean_return = statistics.mean(returns)
    std_return = statistics.stdev(returns)
    anomalies: list[AnomalyRead] = []
    if std_return == 0:
        return AnomaliesResponse(
            start_date=prices[0].price_date,
            end_date=prices[-1].price_date,
            threshold=threshold,
            count=0,
            observation_frequency="monthly",
            items=[],
        )

    for previous, current in zip(prices, prices[1:]):
        pct_change = ((current.usd_oz - previous.usd_oz) / previous.usd_oz) * 100
        z_score = (pct_change - mean_return) / std_return
        if abs(z_score) >= threshold:
            anomalies.append(
                AnomalyRead(
                    price_date=current.price_date,
                    usd_oz=round(current.usd_oz, 2),
                    pct_change=round(pct_change, 2),
                    z_score=round(z_score, 2),
                )
            )
    return AnomaliesResponse(
        start_date=prices[0].price_date,
        end_date=prices[-1].price_date,
        threshold=threshold,
        count=len(anomalies),
        observation_frequency="monthly",
        items=anomalies,
    )


def get_regime(
    db: Session,
    *,
    short_window: int = 3,
    long_window: int = 6,
) -> RegimeResponse:
    prices = _require_prices(db=db)
    if len(prices) < long_window:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not enough gold price history to classify market regime.",
        )
    values = [item.usd_oz for item in prices]
    short_ma = sum(values[-short_window:]) / short_window
    long_ma = sum(values[-long_window:]) / long_window
    regime = "sideways"
    gap_pct = ((short_ma - long_ma) / long_ma) * 100 if long_ma else 0.0
    if gap_pct >= 1.0:
        regime = "bull"
    elif gap_pct <= -1.0:
        regime = "bear"
    return RegimeResponse(
        as_of_date=prices[-1].price_date,
        short_window=short_window,
        long_window=long_window,
        short_moving_average=round(short_ma, 2),
        long_moving_average=round(long_ma, 2),
        regime=regime,
    )


def _require_prices(
    *,
    db: Session,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[GoldPrice]:
    prices = get_prices(db, start_date=start_date, end_date=end_date, limit=0)
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No gold price data was found for the requested range.",
        )
    return prices


def _pct_returns(prices: list[GoldPrice]) -> list[float]:
    returns: list[float] = []
    for previous, current in zip(prices, prices[1:]):
        if previous.usd_oz == 0:
            continue
        returns.append(((current.usd_oz - previous.usd_oz) / previous.usd_oz) * 100)
    return returns


def _find_latest_on_or_before(prices: list[GoldPrice], target_date: date) -> GoldPrice | None:
    candidate: GoldPrice | None = None
    for item in prices:
        if item.price_date <= target_date:
            candidate = item
        else:
            break
    return candidate
