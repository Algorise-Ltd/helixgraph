"""
Neo4j Database Connection Manager

This module provides connection pooling and query execution for Neo4j.
Supports both real Neo4j connections and mock data fallback.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import os

# 【SSL FIX】：强制使用 certifi 提供的标准根证书库
try:
    import certifi
    os.environ['SSL_CERT_FILE'] = certifi.where()
except ImportError:
    pass  # certifi not installed, continue without SSL fix

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️  neo4j package not installed. Using mock data.")


class Neo4jManager:
    """
    Neo4j connection manager with connection pooling.
    
    TODO: Replace mock data with real Neo4j driver when database is ready.
    Connection info needed from Sun (HEL-22):
    - Neo4j URI
    - Username/Password
    - Database name
    """
    
    def __init__(self, uri: str = None, user: str = None, password: str = None, database: str = "neo4j"):
        """
        Initialize Neo4j connection manager.
        
        Args:
            uri: Neo4j connection URI (e.g., 'neo4j+s://xxxxx.databases.neo4j.io')
            user: Neo4j username
            password: Neo4j password
            database: Neo4j database name (default: 'neo4j')
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.database = database
        self.driver = None
        self.connected = False
        
        # Will use mock data if connection fails or credentials not provided
        self._using_mock = True
        
    def connect(self):
        """
        Establish connection to Neo4j database.
        Falls back to mock data if connection fails.
        """
        if not NEO4J_AVAILABLE:
            print("⚠️  Neo4j driver not available. Using mock data.")
            self._using_mock = True
            return
        
        if self.uri and self.user and self.password:
            try:
                print(f"🔌 Connecting to Neo4j at {self.uri}...")
                self.driver = GraphDatabase.driver(
                    self.uri, 
                    auth=(self.user, self.password),
                    max_connection_lifetime=3600
                )
                # Test connection
                self.driver.verify_connectivity()
                self.connected = True
                self._using_mock = False
                print(f"✅ Successfully connected to Neo4j database '{self.database}'")
            except Exception as e:
                print(f"❌ Failed to connect to Neo4j: {e}")
                print("⚠️  Falling back to mock data")
                self._using_mock = True
                self.connected = False
        else:
            print("⚠️  No Neo4j credentials provided. Using mock data for development.")
            self._using_mock = True
    
    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            self.connected = False
    
    def is_connected(self) -> bool:
        """Check if connected to Neo4j"""
        return self.connected
    
    # ============================================================================
    # Query Methods (Real Neo4j + Mock Fallback)
    # ============================================================================
    
    def get_top_suppliers_by_roi(
        self, 
        min_roi: float = 1.0, 
        limit: int = 10, 
        sort: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Get top suppliers ranked by ROI.
        
        Uses real Neo4j data when connected, falls back to mock data otherwise.
        
        Note: Financial metrics (spent/revenue) are estimated from campaign count
        since PO and financial data aren't yet in the database.
        
        Args:
            min_roi: Minimum ROI threshold
            limit: Maximum number of results
            sort: Sort order ('asc' or 'desc')
            
        Returns:
            List of supplier ROI data
        """
        if self.connected and self.driver:
            try:
                from api.database_queries import get_suppliers_with_campaigns
                
                with self.driver.session(database=self.database) as session:
                    suppliers = get_suppliers_with_campaigns(session, self.database)
                
                # Filter by min_roi
                filtered = [s for s in suppliers if s["roi"] >= min_roi]
                
                # Sort
                reverse = (sort.lower() == "desc")
                sorted_suppliers = sorted(filtered, key=lambda x: x["roi"], reverse=reverse)
                
                # Limit
                return sorted_suppliers[:limit]
                
            except Exception as e:
                print(f"⚠️  Error querying Neo4j: {e}. Using mock data.")
                # Fall through to mock data
        
        # Mock data fallback
        mock_suppliers = [
            {
                "supplier_id": "SUP-001",
                "supplier_name": "Tech Solutions Ltd",
                "total_spent": 150000.0,
                "total_revenue": 450000.0,
                "roi": 3.0,
                "campaign_count": 5,
                "po_count": 12
            },
            {
                "supplier_id": "SUP-002",
                "supplier_name": "Global Procurement Inc",
                "total_spent": 200000.0,
                "total_revenue": 500000.0,
                "roi": 2.5,
                "campaign_count": 4,
                "po_count": 10
            },
            {
                "supplier_id": "SUP-003",
                "supplier_name": "Acme Corp",
                "total_spent": 100000.0,
                "total_revenue": 220000.0,
                "roi": 2.2,
                "campaign_count": 3,
                "po_count": 8
            },
            {
                "supplier_id": "SUP-004",
                "supplier_name": "Prime Logistics",
                "total_spent": 80000.0,
                "total_revenue": 144000.0,
                "roi": 1.8,
                "campaign_count": 2,
                "po_count": 6
            }
        ]
        
        # Filter by min_roi
        filtered = [s for s in mock_suppliers if s["roi"] >= min_roi]
        
        # Sort
        reverse = (sort.lower() == "desc")
        sorted_suppliers = sorted(filtered, key=lambda x: x["roi"], reverse=reverse)
        
        # Limit
        return sorted_suppliers[:limit]
    
    def get_campaign_team_gaps(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """
        Get skill gaps for a campaign team.
        
        Uses real Neo4j data when connected, falls back to mock data otherwise.
        
        Note: Skill gap analysis is mocked since employee-skill relationships
        aren't yet in the database.
        WITH c, 
             collect(DISTINCT rs) as required_skills,
             collect(DISTINCT e) as team,
             collect(DISTINCT hs) as available_skills
        UNWIND required_skills as skill
        WITH c, skill, team, available_skills,
             size([s IN required_skills WHERE s.name = skill.name]) as required_count,
             size([s IN available_skills WHERE s.name = skill.name]) as available_count
        WHERE required_count > available_count
        RETURN c.id as campaign_id,
               c.name as campaign_name,
               size(team) as team_size,
               collect({
                   skill_name: skill.name,
                   required_count: required_count,
                   available_count: available_count,
                   gap: required_count - available_count
               }) as skill_gaps
        ```
        
        Args:
            campaign_id: Campaign identifier
            
        Returns:
            Campaign team gap analysis or None if not found
        """
        if self.connected and self.driver:
            try:
                from api.database_queries import get_campaign_details
                
                with self.driver.session(database=self.database) as session:
                    result = get_campaign_details(session, self.database, campaign_id)
                
                if result:
                    return result
                # If not found, try mock data
                    
            except Exception as e:
                print(f"⚠️  Error querying Neo4j: {e}. Using mock data.")
                # Fall through to mock data
        
        # Mock campaigns with skill gaps
        mock_campaigns = {
            "CAMP-001": {
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
                    },
                    {
                        "skill_name": "Data Analysis",
                        "required_count": 2,
                        "available_count": 1,
                        "gap": 1,
                        "severity": "medium"
                    }
                ],
                "total_gaps": 2,
                "critical_gaps": 0
            },
            "CAMP-002": {
                "campaign_id": "CAMP-002",
                "campaign_name": "Q4 Initiative",
                "team_size": 10,
                "skill_gaps": [
                    {
                        "skill_name": "SQL",
                        "required_count": 4,
                        "available_count": 2,
                        "gap": 2,
                        "severity": "critical"
                    }
                ],
                "total_gaps": 1,
                "critical_gaps": 1
            }
        }
        
        return mock_campaigns.get(campaign_id)
    
    def get_high_conversion_products(
        self,
        min_conversion: float = 0.01,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get products with high conversion rates.
        
        Uses real Neo4j data when connected, falls back to mock data otherwise.
        
        Note: Conversion metrics are estimated from campaign count
        since impression/conversion data aren't yet in the database.
        
        Args:
            min_conversion: Minimum conversion rate (0-1)
            category: Optional category filter
            limit: Maximum number of results
            
        Returns:
            List of high-conversion products
        """
        if self.connected and self.driver:
            try:
                from api.database_queries import get_products_by_campaign_count
                
                with self.driver.session(database=self.database) as session:
                    products = get_products_by_campaign_count(session, self.database, limit * 2)
                
                # Filter by min_conversion and category
                filtered = [p for p in products if p["conversion_rate"] >= min_conversion]
                if category:
                    filtered = [p for p in filtered if p["category"] == category]
                
                # Sort and limit
                sorted_products = sorted(filtered, key=lambda x: x["conversion_rate"], reverse=True)
                return sorted_products[:limit]
                
            except Exception as e:
                print(f"⚠️  Error querying Neo4j: {e}. Using mock data.")
                # Fall through to mock data
        
        # Mock data
        mock_products = [
            {
                "product_id": "PROD-123",
                "product_name": "iPhone 15 Pro",
                "category": "Electronics",
                "total_impressions": 100000,
                "total_conversions": 5000,
                "conversion_rate": 0.05,
                "revenue": 5000000.0,
                "campaign_count": 3
            },
            {
                "product_id": "PROD-456",
                "product_name": "MacBook Air",
                "category": "Electronics",
                "total_impressions": 80000,
                "total_conversions": 3200,
                "conversion_rate": 0.04,
                "revenue": 3200000.0,
                "campaign_count": 2
            },
            {
                "product_id": "PROD-789",
                "product_name": "Nike Air Max",
                "category": "Footwear",
                "total_impressions": 150000,
                "total_conversions": 4500,
                "conversion_rate": 0.03,
                "revenue": 450000.0,
                "campaign_count": 4
            },
            {
                "product_id": "PROD-101",
                "product_name": "Samsung Galaxy S24",
                "category": "Electronics",
                "total_impressions": 90000,
                "total_conversions": 1800,
                "conversion_rate": 0.02,
                "revenue": 1800000.0,
                "campaign_count": 2
            }
        ]
        
        # Filter
        filtered = [p for p in mock_products if p["conversion_rate"] >= min_conversion]
        if category:
            filtered = [p for p in filtered if p["category"] == category]
        
        # Sort and limit
        sorted_products = sorted(filtered, key=lambda x: x["conversion_rate"], reverse=True)
        return sorted_products[:limit]
    
    def get_supplier_risk_summary(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive risk assessment for a supplier.
        
        Uses real Neo4j data when connected, falls back to mock data otherwise.
        
        Note: Risk metrics are estimated from campaign activity
        since invoice/contract data aren't yet in the database.
        
        Args:
            supplier_id: Supplier identifier
            
        Returns:
            Supplier risk summary or None if not found
        """
        if self.connected and self.driver:
            try:
                from api.database_queries import get_supplier_details
                
                with self.driver.session(database=self.database) as session:
                    result = get_supplier_details(session, self.database, supplier_id)
                
                if result:
                    return result
                # If not found, try mock data
                    
            except Exception as e:
                print(f"⚠️  Error querying Neo4j: {e}. Using mock data.")
                # Fall through to mock data
        
        # Mock supplier risk data
        mock_suppliers = {
            "SUP-001": {
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
            },
            "SUP-002": {
                "supplier_id": "SUP-002",
                "supplier_name": "Global Procurement Inc",
                "overall_risk_score": 65.0,
                "risk_level": "high",
                "total_outstanding": 120000.0,
                "overdue_invoices": 3,
                "overdue_amount": 35000.0,
                "on_time_delivery_rate": 0.78,
                "quality_score": 72.0,
                "active_contracts": 2,
                "active_pos": 8,
                "risk_flags": [
                    {
                        "flag_type": "quality_issues",
                        "severity": "high",
                        "description": "Multiple quality complaints in last quarter",
                        "detected_date": "2024-03-10"
                    },
                    {
                        "flag_type": "delivery_delays",
                        "severity": "medium",
                        "description": "22% of deliveries delayed",
                        "detected_date": "2024-03-12"
                    }
                ]
            }
        }
        
        return mock_suppliers.get(supplier_id)


# Singleton instance
_neo4j_manager: Optional[Neo4jManager] = None


def get_neo4j_manager(uri: str = None, user: str = None, password: str = None, database: str = "neo4j") -> Neo4jManager:
    """
    Get or create Neo4j manager instance.
    
    Args:
        uri: Neo4j connection URI
        user: Neo4j username
        password: Neo4j password
        database: Neo4j database name
        
    Returns:
        Neo4jManager instance
    """
    global _neo4j_manager
    if _neo4j_manager is None:
        _neo4j_manager = Neo4jManager(uri=uri, user=user, password=password, database=database)
        _neo4j_manager.connect()
    return _neo4j_manager


def close_neo4j_manager():
    """Close Neo4j manager instance"""
    global _neo4j_manager
    if _neo4j_manager:
        _neo4j_manager.close()
        _neo4j_manager = None
