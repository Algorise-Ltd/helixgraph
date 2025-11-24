"""
API Integration Tests for HelixGraph

Tests all FastAPI endpoints with real and mock data scenarios.
"""

import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check_success(self):
        """Test that health endpoint returns status"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "neo4j_connected" in data
        assert "timestamp" in data
        assert data["status"] in ["healthy", "degraded"]
    
    def test_health_check_structure(self):
        """Test health check response structure"""
        response = client.get("/health")
        data = response.json()
        
        # Required fields
        required_fields = ["status", "neo4j_connected", "using_mock_data", "timestamp"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


class TestSuppliersEndpoint:
    """Test suppliers ROI endpoint"""
    
    def test_get_top_suppliers_default(self):
        """Test top suppliers with default parameters"""
        response = client.get("/api/v1/suppliers/top-roi")
        assert response.status_code == 200
        
        data = response.json()
        assert "suppliers" in data
        assert "total_count" in data
        assert "min_roi_filter" in data
        assert isinstance(data["suppliers"], list)
        assert data["min_roi_filter"] == 1.0
    
    def test_get_top_suppliers_with_filters(self):
        """Test top suppliers with custom filters"""
        response = client.get("/api/v1/suppliers/top-roi?min_roi=2.0&limit=5&sort=desc")
        assert response.status_code == 200
        
        data = response.json()
        assert data["min_roi_filter"] == 2.0
        assert len(data["suppliers"]) <= 5
        
        # Check ROI values meet minimum
        for supplier in data["suppliers"]:
            assert supplier["roi"] >= 2.0
    
    def test_get_top_suppliers_sorting(self):
        """Test that suppliers are sorted by ROI"""
        response = client.get("/api/v1/suppliers/top-roi?sort=desc")
        assert response.status_code == 200
        
        data = response.json()
        suppliers = data["suppliers"]
        
        if len(suppliers) > 1:
            # Check descending order
            for i in range(len(suppliers) - 1):
                assert suppliers[i]["roi"] >= suppliers[i + 1]["roi"]
    
    def test_get_top_suppliers_ascending(self):
        """Test ascending sort order"""
        response = client.get("/api/v1/suppliers/top-roi?sort=asc")
        assert response.status_code == 200
        
        data = response.json()
        suppliers = data["suppliers"]
        
        if len(suppliers) > 1:
            # Check ascending order
            for i in range(len(suppliers) - 1):
                assert suppliers[i]["roi"] <= suppliers[i + 1]["roi"]
    
    def test_supplier_response_structure(self):
        """Test supplier object structure"""
        response = client.get("/api/v1/suppliers/top-roi?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data["suppliers"]:
            supplier = data["suppliers"][0]
            
            # Required fields
            required_fields = [
                "supplier_id", "supplier_name", "total_spent",
                "total_revenue", "roi", "campaign_count", "po_count"
            ]
            for field in required_fields:
                assert field in supplier, f"Missing field: {field}"
            
            # Type checks
            assert isinstance(supplier["roi"], (int, float))
            assert isinstance(supplier["campaign_count"], int)
            assert supplier["roi"] >= 0
    
    def test_invalid_min_roi(self):
        """Test invalid min_roi parameter"""
        response = client.get("/api/v1/suppliers/top-roi?min_roi=-1.0")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_limit(self):
        """Test invalid limit parameter"""
        response = client.get("/api/v1/suppliers/top-roi?limit=0")
        assert response.status_code == 422
        
        response = client.get("/api/v1/suppliers/top-roi?limit=200")
        assert response.status_code == 422
    
    def test_invalid_sort(self):
        """Test invalid sort parameter"""
        response = client.get("/api/v1/suppliers/top-roi?sort=invalid")
        assert response.status_code == 422


class TestProductsEndpoint:
    """Test high-conversion products endpoint"""
    
    def test_get_high_conversion_products_default(self):
        """Test products with default parameters"""
        response = client.get("/api/v1/products/high-conversion")
        assert response.status_code == 200
        
        data = response.json()
        assert "products" in data
        assert "total_count" in data
        assert "min_conversion_filter" in data
        assert isinstance(data["products"], list)
    
    def test_get_products_with_filters(self):
        """Test products with filters"""
        response = client.get("/api/v1/products/high-conversion?min_conversion=0.03&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert data["min_conversion_filter"] == 0.03
        assert len(data["products"]) <= 5
        
        # Check conversion rates meet minimum
        for product in data["products"]:
            assert product["conversion_rate"] >= 0.03
    
    def test_get_products_with_category(self):
        """Test products filtered by category"""
        response = client.get("/api/v1/products/high-conversion?category=Electronics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["category_filter"] == "Electronics"
        
        # All products should be in specified category
        for product in data["products"]:
            assert product["category"] == "Electronics"
    
    def test_product_response_structure(self):
        """Test product object structure"""
        response = client.get("/api/v1/products/high-conversion?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        if data["products"]:
            product = data["products"][0]
            
            required_fields = [
                "product_id", "product_name", "category",
                "total_impressions", "total_conversions",
                "conversion_rate", "revenue", "campaign_count"
            ]
            for field in required_fields:
                assert field in product
            
            # Value checks
            assert 0 <= product["conversion_rate"] <= 1
            assert product["total_conversions"] <= product["total_impressions"]
    
    def test_invalid_conversion_rate(self):
        """Test invalid conversion rate"""
        response = client.get("/api/v1/products/high-conversion?min_conversion=1.5")
        assert response.status_code == 422
        
        response = client.get("/api/v1/products/high-conversion?min_conversion=-0.1")
        assert response.status_code == 422


class TestCampaignEndpoint:
    """Test campaign team gaps endpoint"""
    
    def test_get_campaign_gaps_found(self):
        """Test campaign gaps for existing campaign"""
        # Try with mock campaign ID
        response = client.get("/api/v1/campaigns/CAMP-001/team-gaps")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "campaign_id" in data
            assert "campaign_name" in data
            assert "team_size" in data
            assert "skill_gaps" in data
            assert "total_gaps" in data
            assert "critical_gaps" in data
    
    def test_get_campaign_gaps_not_found(self):
        """Test campaign gaps for non-existent campaign"""
        response = client.get("/api/v1/campaigns/NONEXISTENT-999/team-gaps")
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
    
    def test_campaign_gaps_structure(self):
        """Test campaign gaps response structure"""
        response = client.get("/api/v1/campaigns/CAMP-001/team-gaps")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check skill gaps structure
            if data["skill_gaps"]:
                gap = data["skill_gaps"][0]
                assert "skill_name" in gap
                assert "severity" in gap
                
                # Severity should be valid
                assert gap["severity"] in ["Critical", "High", "Medium", "Low", "critical", "high", "medium", "low"]


class TestSupplierRiskEndpoint:
    """Test supplier risk assessment endpoint"""
    
    def test_get_supplier_risk_found(self):
        """Test risk assessment for existing supplier"""
        response = client.get("/api/v1/suppliers/SUP-001/risk")
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "supplier_id" in data
            assert "supplier_name" in data
            assert "risk_score" in data or "overall_risk_score" in data
            assert "risk_level" in data
    
    def test_get_supplier_risk_not_found(self):
        """Test risk assessment for non-existent supplier"""
        response = client.get("/api/v1/suppliers/NONEXISTENT-999/risk")
        assert response.status_code == 404
    
    def test_supplier_risk_structure(self):
        """Test supplier risk response structure"""
        response = client.get("/api/v1/suppliers/SUP-001/risk")
        
        if response.status_code == 200:
            data = response.json()
            
            # Risk level should be valid
            assert "risk_level" in data
            risk_level = data["risk_level"].lower()
            assert risk_level in ["low", "medium", "high", "critical"]
            
            # Risk score should be in valid range
            risk_score = data.get("risk_score") or data.get("overall_risk_score", 0)
            assert 0 <= risk_score <= 100


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_invalid_endpoint(self):
        """Test 404 for invalid endpoint"""
        response = client.get("/api/v1/invalid-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test POST on GET-only endpoint"""
        response = client.post("/api/v1/suppliers/top-roi")
        assert response.status_code == 405
    
    def test_malformed_parameters(self):
        """Test malformed query parameters"""
        response = client.get("/api/v1/suppliers/top-roi?min_roi=invalid")
        assert response.status_code == 422


class TestAPIDocumentation:
    """Test API documentation endpoints"""
    
    def test_openapi_schema(self):
        """Test that OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema
    
    def test_docs_endpoint(self):
        """Test that Swagger UI is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
    
    def test_redoc_endpoint(self):
        """Test that ReDoc is accessible"""
        response = client.get("/redoc")
        assert response.status_code == 200


class TestResponsePerformance:
    """Test response time and performance"""
    
    def test_health_response_time(self):
        """Test health endpoint responds quickly"""
        import time
        start = time.time()
        response = client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 1.0  # Should respond in under 1 second
    
    def test_suppliers_response_time(self):
        """Test suppliers endpoint responds reasonably"""
        import time
        start = time.time()
        response = client.get("/api/v1/suppliers/top-roi?limit=10")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 5.0  # Should respond in under 5 seconds


# Run tests with pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
