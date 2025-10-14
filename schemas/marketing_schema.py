"""Pydantic models for the Marketing domain."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class ChannelType(str, Enum):
    """Supported marketing channel categories."""

    DIGITAL = "Digital"
    SOCIAL = "Social"
    EMAIL = "Email"
    SEARCH = "Search"
    DISPLAY = "Display"
    RETAIL = "Retail"
    PR = "PR"


class Currency(str, Enum):
    """Supported currency codes."""

    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"


class KPIUnit(str, Enum):
    """Measurement unit for KPI values."""

    PERCENT = "Percent"
    COUNT = "Count"
    CURRENCY = "Currency"
    RATIO = "Ratio"
    INDEX = "Index"


class Brand(BaseModel):
    """Brand references used by campaigns."""

    brand_id: str = Field(..., description="Unique brand identifier")
    name: str
    category: str
    market: str = Field(..., description="Primary market focus, e.g. Germany")


class Objective(BaseModel):
    """Marketing objective definition."""

    objective_id: str
    name: str
    description: str


class KPI(BaseModel):
    """Key performance indicator definition."""

    kpi_id: str
    name: str
    description: str
    unit: KPIUnit
    direction: str = Field(..., description="higher_is_better or lower_is_better")


class Channel(BaseModel):
    """Marketing channel taxonomy node."""

    channel_id: str
    name: str
    type: ChannelType
    parent_id: Optional[str] = Field(None, description="Parent channel for hierarchy")


class CampaignChannelKPI(BaseModel):
    """KPI value reported for a campaign-channel combination."""

    kpi_id: str
    value: float
    unit: KPIUnit
    period_start: date
    period_end: date


class CampaignChannel(BaseModel):
    """Channel mix allocation for a campaign."""

    channel_id: str
    spend: float
    currency: Currency
    kpis: List[CampaignChannelKPI] = Field(default_factory=list)


class CampaignOrder(BaseModel):
    """Downstream commerce order attributed to a campaign."""

    order_id: str
    platform: str
    revenue: float
    currency: Currency
    conversion_date: date


class Campaign(BaseModel):
    """Synthetic marketing campaign dataset."""

    campaign_id: str
    name: str
    objective_id: str
    brand_id: str
    region: str
    start_date: date
    end_date: date
    budget: float
    currency: Currency
    channels: List[CampaignChannel]
    orders: List[CampaignOrder] = Field(default_factory=list)


class MarketingDataset(BaseModel):
    """Root object written to disk for loader consumption."""

    brands: List[Brand]
    objectives: List[Objective]
    kpis: List[KPI]
    channels: List[Channel]
    campaigns: List[Campaign]

