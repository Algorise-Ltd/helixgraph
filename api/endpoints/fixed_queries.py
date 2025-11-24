"""
Fixed Query Endpoints for HelixGraph API

These endpoints provide predefined business queries across the knowledge graph.
All queries are optimized for performance (<1s response time).
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional

from api.models.responses import (
    TopSuppliersResponse,
    SupplierROI,
    CampaignTeamGapsResponse,
    SkillGap,
    HighConversionProductsResponse,
    ProductConversion,
    SupplierRiskSummary,
    ErrorResponse
)
from api.database import get_neo4j_manager


router = APIRouter(
    prefix="/api/v1",
    tags=["Fixed Queries"],
    responses={
        404: {"model": ErrorResponse, "description": "Resource not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


# ============================================================================
# Endpoint 1: Top Suppliers by ROI
# ============================================================================

@router.get(
    "/suppliers/top-roi",
    response_model=TopSuppliersResponse,
    summary="Get Top Suppliers by ROI",
    description="""
    Returns suppliers ranked by Return on Investment (ROI).
    
    ROI is calculated as: (Total Revenue from Campaigns) / (Total Spent on POs)
    
    **Business Use Case:**
    Identify which suppliers provide the best value in terms of revenue generated
    relative to procurement costs. Useful for:
    - Supplier performance reviews
    - Budget allocation decisions
    - Strategic partnership identification
    
    **Performance:** < 500ms typical response time
    """,
    response_description="List of suppliers sorted by ROI"
)
async def get_top_suppliers_by_roi(
    min_roi: float = Query(
        default=1.0,
        ge=0.0,
        description="Minimum ROI threshold. Only suppliers with ROI >= this value are returned.",
        example=1.5
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of suppliers to return",
        example=10
    ),
    sort: str = Query(
        default="desc",
        regex="^(asc|desc)$",
        description="Sort order: 'asc' for ascending, 'desc' for descending",
        example="desc"
    )
):
    """
    Get top suppliers ranked by ROI.
    
    Args:
        min_roi: Minimum ROI threshold
        limit: Maximum number of results
        sort: Sort order ('asc' or 'desc')
        
    Returns:
        TopSuppliersResponse with supplier ROI data
        
    Raises:
        HTTPException: 500 if query fails
    """
    try:
        db = get_neo4j_manager()
        suppliers_data = db.get_top_suppliers_by_roi(
            min_roi=min_roi,
            limit=limit,
            sort=sort
        )
        
        # Convert to Pydantic models
        suppliers = [SupplierROI(**data) for data in suppliers_data]
        
        return TopSuppliersResponse(
            suppliers=suppliers,
            total_count=len(suppliers),
            min_roi_filter=min_roi
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve supplier ROI data: {str(e)}"
        )


# ============================================================================
# Endpoint 2: Campaign Team Skill Gaps
# ============================================================================

@router.get(
    "/campaigns/{campaign_id}/team-gaps",
    response_model=CampaignTeamGapsResponse,
    summary="Get Campaign Team Skill Gaps",
    description="""
    Analyzes skill gaps in a campaign team by comparing required skills 
    against available team member skills.
    
    **Business Use Case:**
    Identify missing skills needed for campaign success. Useful for:
    - Hiring decisions
    - Training program planning
    - Resource reallocation
    - Risk assessment
    
    **Gap Severity Levels:**
    - **Critical**: Gap >= 3 or required skills completely missing
    - **High**: Gap = 2
    - **Medium**: Gap = 1
    - **Low**: Gap < 1 (for partial skill matches)
    
    **Performance:** < 300ms typical response time
    """,
    response_description="Skill gap analysis for the campaign team"
)
async def get_campaign_team_gaps(
    campaign_id: str = Path(
        ...,
        description="Unique campaign identifier",
        example="CAMP-001"
    )
):
    """
    Get skill gaps for a campaign team.
    
    Args:
        campaign_id: Campaign identifier
        
    Returns:
        CampaignTeamGapsResponse with skill gap analysis
        
    Raises:
        HTTPException: 404 if campaign not found, 500 if query fails
    """
    try:
        db = get_neo4j_manager()
        gaps_data = db.get_campaign_team_gaps(campaign_id)
        
        if gaps_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Campaign with ID '{campaign_id}' not found"
            )
        
        # Convert skill gaps to Pydantic models
        skill_gaps = [SkillGap(**gap) for gap in gaps_data["skill_gaps"]]
        
        return CampaignTeamGapsResponse(
            campaign_id=gaps_data["campaign_id"],
            campaign_name=gaps_data["campaign_name"],
            team_size=gaps_data["team_size"],
            skill_gaps=skill_gaps,
            total_gaps=gaps_data["total_gaps"],
            critical_gaps=gaps_data["critical_gaps"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve campaign team gaps: {str(e)}"
        )


# ============================================================================
# Endpoint 3: High-Conversion Products
# ============================================================================

@router.get(
    "/products/high-conversion",
    response_model=HighConversionProductsResponse,
    summary="Get High-Conversion Products",
    description="""
    Returns products with high conversion rates from marketing campaigns.
    
    Conversion rate = (Total Conversions) / (Total Impressions)
    
    **Business Use Case:**
    Identify products that convert impressions into sales most effectively. 
    Useful for:
    - Marketing budget allocation
    - Product portfolio optimization
    - Campaign planning
    - Inventory decisions
    
    **Benchmarks:**
    - 0.05+ (5%): Excellent conversion
    - 0.03-0.05 (3-5%): Good conversion
    - 0.01-0.03 (1-3%): Average conversion
    - <0.01 (<1%): Poor conversion
    
    **Performance:** < 600ms typical response time
    """,
    response_description="List of products sorted by conversion rate"
)
async def get_high_conversion_products(
    min_conversion: float = Query(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Minimum conversion rate (0-1). Example: 0.03 = 3%",
        example=0.03
    ),
    category: Optional[str] = Query(
        default=None,
        description="Optional product category filter",
        example="Electronics"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of products to return",
        example=10
    )
):
    """
    Get products with high conversion rates.
    
    Args:
        min_conversion: Minimum conversion rate (0-1)
        category: Optional category filter
        limit: Maximum number of results
        
    Returns:
        HighConversionProductsResponse with product conversion data
        
    Raises:
        HTTPException: 500 if query fails
    """
    try:
        db = get_neo4j_manager()
        products_data = db.get_high_conversion_products(
            min_conversion=min_conversion,
            category=category,
            limit=limit
        )
        
        # Convert to Pydantic models
        products = [ProductConversion(**data) for data in products_data]
        
        return HighConversionProductsResponse(
            products=products,
            total_count=len(products),
            min_conversion_filter=min_conversion,
            category_filter=category
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve product conversion data: {str(e)}"
        )


# ============================================================================
# Endpoint 4: Supplier Risk Summary
# ============================================================================

@router.get(
    "/suppliers/{supplier_id}/risk",
    response_model=SupplierRiskSummary,
    summary="Get Supplier Risk Assessment",
    description="""
    Provides comprehensive risk assessment for a supplier, including:
    - Financial risks (overdue invoices, outstanding amounts)
    - Performance metrics (on-time delivery, quality scores)
    - Active relationships (contracts, purchase orders)
    - Risk flags and alerts
    
    **Business Use Case:**
    Evaluate supplier reliability and identify potential supply chain risks. 
    Useful for:
    - Vendor evaluation
    - Procurement decisions
    - Risk mitigation planning
    - Contract renewals
    
    **Risk Scoring:**
    - 0-30: Low risk
    - 31-60: Medium risk
    - 61-80: High risk
    - 81-100: Critical risk
    
    **Risk Factors Considered:**
    - Payment history (30% weight)
    - Delivery performance (25% weight)
    - Quality metrics (25% weight)
    - Financial stability (20% weight)
    
    **Performance:** < 400ms typical response time
    """,
    response_description="Comprehensive supplier risk assessment"
)
async def get_supplier_risk_summary(
    supplier_id: str = Path(
        ...,
        description="Unique supplier identifier",
        example="SUP-001"
    )
):
    """
    Get comprehensive risk assessment for a supplier.
    
    Args:
        supplier_id: Supplier identifier
        
    Returns:
        SupplierRiskSummary with risk assessment data
        
    Raises:
        HTTPException: 404 if supplier not found, 500 if query fails
    """
    try:
        db = get_neo4j_manager()
        risk_data = db.get_supplier_risk_summary(supplier_id)
        
        if risk_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Supplier with ID '{supplier_id}' not found"
            )
        
        return SupplierRiskSummary(**risk_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve supplier risk summary: {str(e)}"
        )
