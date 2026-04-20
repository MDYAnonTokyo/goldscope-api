from datetime import date

from pydantic import BaseModel


class GoldPriceRead(BaseModel):
    id: int
    price_date: date
    usd_oz: float
    gbp_oz: float | None
    eur_oz: float | None
    source_name: str

    model_config = {"from_attributes": True}


class GoldPriceListResponse(BaseModel):
    count: int
    start_date: date | None
    end_date: date | None
    items: list[GoldPriceRead]


class GoldLatestResponse(BaseModel):
    item: GoldPriceRead


class SummaryResponse(BaseModel):
    start_date: date
    end_date: date
    observation_count: int
    observation_frequency: str
    latest_price: float
    latest_date: date
    min_price: float
    max_price: float
    average_price: float
    absolute_change: float
    percent_change: float


class ReturnMetric(BaseModel):
    period_label: str
    lookback_days: int
    matched_date: date
    matched_price: float
    latest_price: float
    absolute_return: float
    percent_return: float


class ReturnsResponse(BaseModel):
    as_of_date: date
    observation_frequency: str
    items: list[ReturnMetric]


class VolatilityResponse(BaseModel):
    as_of_date: date
    observation_frequency: str
    window_points: int
    annualized_volatility: float
    return_count: int


class DrawdownResponse(BaseModel):
    start_date: date
    end_date: date
    max_drawdown_pct: float
    peak_date: date
    trough_date: date
    recovery_date: date | None


class AnomalyRead(BaseModel):
    price_date: date
    usd_oz: float
    pct_change: float
    z_score: float


class AnomaliesResponse(BaseModel):
    start_date: date
    end_date: date
    threshold: float
    count: int
    observation_frequency: str
    items: list[AnomalyRead]


class RegimeResponse(BaseModel):
    as_of_date: date
    short_window: int
    long_window: int
    short_moving_average: float
    long_moving_average: float
    regime: str
