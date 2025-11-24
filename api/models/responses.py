"""
Pydantic Response Models for Fixed Query Endpoints
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# Endpoint 1: Top Suppliers by ROI
# ============================================================================

class SupplierROI(BaseModel):
    """Individual supplier ROI information"""
    supplier_id: str = Field(..., description="Unique supplier identifier")
    supplier_name: str = Field(..., description="Supplier company name")
    total_spent: float = Field(..., description="Total amount spent with this supplier")
    total_revenue: float = Field(..., description="Total revenue generated from related campaigns")
    roi: float = Field(..., description="Return on Investment (revenue/spent)")
    campaign_count: int = Field(..., description="Number of campaigns associated")
    po_count: int = Field(..., description="Number of purchase orders")
    
    class Config:
        json_schema_extra = {
            "example": {
                "supplier_id": "SUP-001",
                "supplier_name": "Tech Solutions Ltd",
                "total_spent": 150000.0,
                "total_revenue": 450000.0,
                "roi": 3.0,
                "campaign_count": 5,
                "po_count": 12
            }
        }


class TopSuppliersResponse(BaseModel):
    """Response for top suppliers by ROI endpoint"""
    suppliers: List[SupplierROI] = Field(..., description="List of suppliers sorted by ROI")
    total_count: int = Field(..., description="Total number of suppliers found")
    min_roi_filter: float = Field(..., description="Minimum ROI filter applied")
    
    class Config:
        json_schema_extra = {
            "example": {
                "suppliers": [
                    {
                        "supplier_id": "SUP-001",
                        "supplier_name": "Tech Solutions Ltd",
                        "total_spent": 150000.0,
                        "total_revenue": 450000.0,
                        "roi": 3.0,
                        "campaign_count": 5,
                        "po_count": 12
                    }
                ],
                "total_count": 1,
                "min_roi_filter": 1.5
            }
        }


# ============================================================================
# Endpoint 2: Campaign Team Skill Gaps
# ============================================================================

class SkillGap(BaseModel):
    """Individual skill gap information"""
    skill_name: str = Field(..., description="Name of the missing skill")
    required_count: int = Field(..., description="Number of team members that need this skill")
    available_count: int = Field(..., description="Number of team members that have this skill")
    gap: int = Field(..., description="Shortage (required - available)")
    severity: str = Field(..., description="Gap severity: critical, high, medium, low")
    
    class Config:
        json_schema_extra = {
            "example": {
                "skill_name": "Python",
                "required_count": 3,
                "available_count": 1,
                "gap": 2,
                "severity": "high"
            }
        }


class CampaignTeamGapsResponse(BaseModel):
    """Response for campaign team skill gaps endpoint"""
    campaign_id: str = Field(..., description="Campaign identifier")
    campaign_name: str = Field(..., description="Campaign name")
    team_size: int = Field(..., description="Total team members assigned")
    skill_gaps: List[SkillGap] = Field(..., description="List of identified skill gaps")
    total_gaps: int = Field(..., description="Total number of skill gaps")
    critical_gaps: int = Field(..., description="Number of critical gaps")
    
    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "CAMP-001",
                "campaign_name": "Spring Launch 2024",
                "team_size": 8,
                "skill_gaps": [
                    {
                        "skill_name": "Python",
                        "required_count": 3,
                        "available_count": 1,
                        "gap": 2,
                        "severity": "high"
                    }
                ],
                "total_gaps": 1,
                "critical_gaps": 0
            }
        }


# ============================================================================
# Endpoint 3: High-Conversion Products
# ============================================================================

class ProductConversion(BaseModel):
    """Individual product conversion information"""
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product name")
    category: Optional[str] = Field(None, description="Product category")
    total_impressions: int = Field(..., description="Total number of impressions")
    total_conversions: int = Field(..., description="Total number of conversions")
    conversion_rate: float = Field(..., description="Conversion rate (conversions/impressions)")
    revenue: float = Field(..., description="Total revenue generated")
    campaign_count: int = Field(..., description="Number of campaigns featuring this product")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "PROD-123",
                "product_name": "iPhone 15 Pro",
                "category": "Electronics",
                "total_impressions": 100000,
                "total_conversions": 5000,
                "conversion_rate": 0.05,
                "revenue": 5000000.0,
                "campaign_count": 3
            }
        }


class HighConversionProductsResponse(BaseModel):
    """Response for high-conversion products endpoint"""
    products: List[ProductConversion] = Field(..., description="List of products sorted by conversion rate")
    total_count: int = Field(..., description="Total number of products found")
    min_conversion_filter: float = Field(..., description="Minimum conversion rate filter applied")
    category_filter: Optional[str] = Field(None, description="Category filter applied")
    
    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "product_id": "PROD-123",
                        "product_name": "iPhone 15 Pro",
                        "category": "Electronics",
                        "total_impressions": 100000,
                        "total_conversions": 5000,
                        "conversion_rate": 0.05,
                        "revenue": 5000000.0,
                        "campaign_count": 3
                    }
                ],
                "total_count": 1,
                "min_conversion_filter": 0.03,
                "category_filter": "Electronics"
            }
        }


# ============================================================================
# Endpoint 4: Supplier Risk Summary
# ============================================================================

class RiskFlag(BaseModel):
    """Individual risk flag"""
    flag_type: str = Field(..., description="Type of risk flag")
    severity: str = Field(..., description="Risk severity: critical, high, medium, low")
    description: str = Field(..., description="Risk description")
    detected_date: str = Field(..., description="Date when risk was detected")
    

class SupplierRiskSummary(BaseModel):
    """Comprehensive supplier risk assessment"""
    supplier_id: str = Field(..., description="Unique supplier identifier")
    supplier_name: str = Field(..., description="Supplier company name")
    overall_risk_score: float = Field(..., description="Overall risk score (0-100)")
    risk_level: str = Field(..., description="Risk level: low, medium, high, critical")
    
    # Financial metrics
    total_outstanding: float = Field(..., description="Total outstanding amount")
    overdue_invoices: int = Field(..., description="Number of overdue invoices")
    overdue_amount: float = Field(..., description="Total amount overdue")
    
    # Performance metrics
    on_time_delivery_rate: float = Field(..., description="Percentage of on-time deliveries")
    quality_score: float = Field(..., description="Quality score (0-100)")
    
    # Active relationships
    active_contracts: int = Field(..., description="Number of active contracts")
    active_pos: int = Field(..., description="Number of active purchase orders")
    
    # Risk flags
    risk_flags: List[RiskFlag] = Field(..., description="List of active risk flags")
    
    class Config:
        json_schema_extra = {
            "example": {
                "supplier_id": "SUP-001",
                "supplier_name": "Tech Solutions Ltd",
                "overall_risk_score": 35.5,
                "risk_level": "low",
                "total_outstanding": 50000.0,
                "overdue_invoices": 1,
                "overdue_amount": 5000.0,
                "on_time_delivery_rate": 0.95,
                "quality_score": 88.5,
                "active_contracts": 3,
                "active_pos": 5,
                "risk_flags": [
                    {
                        "flag_type": "payment_delay",
                        "severity": "medium",
                        "description": "Invoice INV-123 overdue by 15 days",
                        "detected_date": "2024-03-15"
                    }
                ]
            }
        }


# ============================================================================
# Common Response Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "NotFound",
                "message": "Campaign with ID 'CAMP-999' not found",
                "detail": {"campaign_id": "CAMP-999"}
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="API status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="API version")
    ner_model_loaded: bool = Field(..., description="NER model status")
    entity_linker_loaded: bool = Field(..., description="Entity linker status")
    neo4j_connected: bool = Field(False, description="Neo4j connection status")
