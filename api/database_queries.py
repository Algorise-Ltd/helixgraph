"""
Real Neo4j Query Methods

This module contains real Cypher queries to replace mock data in database.py.
Uses actual data from Neo4j Aura instance.
"""

from typing import List, Dict, Any, Optional


def get_suppliers_with_campaigns(session, database: str) -> List[Dict[str, Any]]:
    """
    Get suppliers who have campaigns featuring their products.
    This is a simplified ROI query based on available data.
    
    Real data structure:
    - Supplier nodes exist
    - Campaign nodes exist  
    - Product nodes exist
    - FEATURES relationships: Campaign→Product
    
    Missing (using estimates):
    - PO (Purchase Order) relationships
    - Revenue/cost data
    """
    query = """
    MATCH (s:Supplier)
    OPTIONAL MATCH (p:Product {name: s.name})<-[:FEATURES]-(c:Campaign)
    WITH s, count(DISTINCT c) as campaign_count, collect(DISTINCT c.name)[0..5] as campaigns
    WHERE campaign_count > 0
    RETURN s.name as supplier_name,
           campaign_count,
           campaigns
    ORDER BY campaign_count DESC
    LIMIT 20
    """
    
    result = session.run(query)
    
    suppliers = []
    for record in result:
        # Since we don't have real financial data, estimate based on campaign count
        campaign_count = record["campaign_count"]
        estimated_spent = campaign_count * 25000  # $25k per campaign estimate
        estimated_revenue = campaign_count * 60000  # $60k revenue estimate
        roi = estimated_revenue / estimated_spent if estimated_spent > 0 else 0
        
        suppliers.append({
            "supplier_id": f"SUP-{hash(record['supplier_name']) % 1000:03d}",
            "supplier_name": record["supplier_name"],
            "total_spent": float(estimated_spent),
            "total_revenue": float(estimated_revenue),
            "roi": float(roi),
            "campaign_count": campaign_count,
            "po_count": campaign_count * 2  # Estimate 2 POs per campaign
        })
    
    return suppliers


def get_products_by_campaign_count(session, database: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get products ranked by number of campaigns they appear in.
    Simulates conversion data using campaign frequency.
    """
    query = """
    MATCH (p:Product)<-[:FEATURES]-(c:Campaign)
    WITH p, count(c) as campaign_count, collect(c.name)[0..3] as campaigns
    RETURN p.name as product_name,
           campaign_count,
           campaigns
    ORDER BY campaign_count DESC
    LIMIT $limit
    """
    
    result = session.run(query, limit=limit)
    
    products = []
    for record in result:
        campaign_count = record["campaign_count"]
        # Simulate metrics based on campaign count
        impressions = campaign_count * 50000  # 50k impressions per campaign
        conversions = int(impressions * (0.02 + campaign_count * 0.005))  # Higher count = better conversion
        conversion_rate = conversions / impressions if impressions > 0 else 0
        revenue = conversions * 100  # $100 per conversion
        
        products.append({
            "product_id": f"PROD-{hash(record['product_name']) % 1000:03d}",
            "product_name": record["product_name"],
            "category": "Consumer Goods",  # Default category
            "total_impressions": impressions,
            "total_conversions": conversions,
            "conversion_rate": float(conversion_rate),
            "revenue": float(revenue),
            "campaign_count": campaign_count
        })
    
    return products


def get_campaign_details(session, database: str, campaign_id: str) -> Optional[Dict[str, Any]]:
    """
    Get campaign details by ID or name.
    """
    query = """
    MATCH (c:Campaign)
    WHERE c.name CONTAINS $campaign_id OR c.campaign_id = $campaign_id
    OPTIONAL MATCH (c)-[:FEATURES]->(p:Product)
    RETURN c.name as campaign_name,
           c.campaign_id as campaign_id,
           collect(p.name) as products
    LIMIT 1
    """
    
    result = session.run(query, campaign_id=campaign_id)
    record = result.single()
    
    if not record:
        return None
    
    # Since we don't have skill/employee data, return mock skill gaps
    return {
        "campaign_id": campaign_id,
        "campaign_name": record["campaign_name"],
        "team_size": 5,  # Mock team size
        "skill_gaps": [
            {
                "skill_name": "Python",
                "required_level": 3,
                "current_level": 2,
                "gap": 1,
                "severity": "Medium"
            },
            {
                "skill_name": "Digital Marketing",
                "required_level": 4,
                "current_level": 1,
                "gap": 3,
                "severity": "Critical"
            }
        ],
        "total_gaps": 2,
        "critical_gaps": 1
    }


def get_supplier_details(session, database: str, supplier_id: str) -> Optional[Dict[str, Any]]:
    """
    Get supplier details and related campaigns.
    """
    query = """
    MATCH (s:Supplier)
    WHERE s.name CONTAINS $supplier_id
    OPTIONAL MATCH (p:Product {name: s.name})<-[:FEATURES]-(c:Campaign)
    RETURN s.name as supplier_name,
           count(DISTINCT c) as campaign_count,
           collect(DISTINCT c.name)[0..5] as campaigns
    LIMIT 1
    """
    
    result = session.run(query, supplier_id=supplier_id)
    record = result.single()
    
    if not record:
        return None
    
    # Mock risk assessment based on campaign activity
    campaign_count = record["campaign_count"]
    risk_score = max(0, 50 - (campaign_count * 5))  # More campaigns = lower risk
    
    return {
        "supplier_id": supplier_id,
        "supplier_name": record["supplier_name"],
        "risk_score": risk_score,
        "risk_level": "Low" if risk_score < 30 else "Medium" if risk_score < 60 else "High",
        "active_contracts": campaign_count,
        "overdue_invoices": 0,
        "overdue_amount": 0.0,
        "on_time_delivery_rate": 0.95,
        "quality_score": 0.92,
        "risk_flags": [] if risk_score < 60 else ["Limited campaign activity"]
    }


def list_all_suppliers(session, database: str, limit: int = 100) -> List[str]:
    """List all supplier names in database"""
    query = """
    MATCH (s:Supplier)
    RETURN s.name as name
    ORDER BY s.name
    LIMIT $limit
    """
    result = session.run(query, limit=limit)
    return [record["name"] for record in result]


def list_all_campaigns(session, database: str, limit: int = 100) -> List[str]:
    """List all campaign names in database"""
    query = """
    MATCH (c:Campaign)
    RETURN c.name as name
    ORDER BY c.name
    LIMIT $limit
    """
    result = session.run(query, limit=limit)
    return [record["name"] for record in result]


def list_all_products(session, database: str, limit: int = 100) -> List[str]:
    """List all product names in database"""
    query = """
    MATCH (p:Product)
    RETURN p.name as name
    ORDER BY p.name
    LIMIT $limit
    """
    result = session.run(query, limit=limit)
    return [record["name"] for record in result]
