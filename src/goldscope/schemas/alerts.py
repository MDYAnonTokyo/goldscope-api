from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class AlertCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    condition_type: Literal["above", "below"]
    threshold_value: float = Field(gt=0)
    notes: str | None = Field(default=None, max_length=500)
    active: bool = True


class AlertUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    condition_type: Literal["above", "below"] | None = None
    threshold_value: float | None = Field(default=None, gt=0)
    notes: str | None = Field(default=None, max_length=500)
    active: bool | None = None


class AlertRead(BaseModel):
    id: int
    user_id: int
    name: str
    condition_type: str
    threshold_value: float
    notes: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    count: int
    items: list[AlertRead]
