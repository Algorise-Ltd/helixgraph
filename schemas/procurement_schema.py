"""Pydantic models for the Procurement domain."""
from __future__ import annotations

from datetime import date
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class SupplierTier(str, Enum):
    """Supplier segmentation tiers."""

    STRATEGIC = "Strategic"
    PREFERRED = "Preferred"
    APPROVED = "Approved"
    TACTICAL = "Tactical"


class RiskCategory(str, Enum):
    """Risk dimensions considered by the risk model."""

    FINANCIAL = "Financial"
    OPERATIONAL = "Operational"
    ESG = "ESG"
    GEO_POLITICAL = "GeoPolitical"
    COMPLIANCE = "Compliance"


class Currency(str, Enum):
    """Supported currency codes."""

    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"


class Supplier(BaseModel):
    """Supplier master record."""

    supplier_id: str
    name: str
    country: str
    industry: str
    tier: SupplierTier
    onboarding_date: date


class Contract(BaseModel):
    """Procurement contract between buyer and supplier."""

    contract_id: str
    supplier_id: str
    category: str
    start_date: date
    end_date: Optional[date]
    value: float
    currency: Currency


class RiskScore(BaseModel):
    """Risk rating for a supplier."""

    supplier_id: str
    category: RiskCategory
    score: float = Field(..., ge=0, le=100)
    assessed_date: date
    notes: Optional[str]


class PurchaseOrderLine(BaseModel):
    """Line level data for a purchase order."""

    line_id: str
    contract_id: str
    product_category: str
    quantity: float
    unit_price: float
    currency: Currency


class PurchaseOrder(BaseModel):
    """Purchase order header with associated lines."""

    po_id: str
    supplier_id: str
    issue_date: date
    expected_delivery_date: date
    status: str
    lines: List[PurchaseOrderLine]


class ProcurementDataset(BaseModel):
    """Root object for procurement sample data."""

    suppliers: List[Supplier]
    contracts: List[Contract]
    risk_scores: List[RiskScore]
    purchase_orders: List[PurchaseOrder]

