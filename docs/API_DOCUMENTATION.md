# HelixGraph API Documentation

**Version:** 1.0  
**Base URL:** `http://localhost:8000`  
**Production URL:** (To be deployed)

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limiting](#rate-limiting)
4. [Response Format](#response-format)
5. [Error Handling](#error-handling)
6. [Endpoints](#endpoints)
   - [Health Check](#health-check)
   - [Top Suppliers by ROI](#top-suppliers-by-roi)
   - [Campaign Team Skill Gaps](#campaign-team-skill-gaps)
   - [High-Conversion Products](#high-conversion-products)
   - [Supplier Risk Assessment](#supplier-risk-assessment)
7. [Code Examples](#code-examples)
8. [Postman Collection](#postman-collection)

---

## Overview

HelixGraph API provides access to business intelligence queries across marketing, procurement, and HR data stored in a Neo4j knowledge graph.

### Key Features

- ✅ RESTful API design
- ✅ FastAPI with automatic OpenAPI documentation
- ✅ Real-time Neo4j queries
- ✅ Structured JSON responses
- ✅ Comprehensive error handling
- ✅ Performance optimized (<1s typical response)

### Tech Stack

- **Framework:** FastAPI 0.109+
- **Database:** Neo4j Aura (Cloud)
- **Python:** 3.11+
- **Documentation:** OpenAPI 3.0

---

## Authentication

**Current Status:** No authentication required (development)

**Production:** Will implement:
- API Key authentication
- JWT tokens for user sessions
- Rate limiting per API key

---

## Rate Limiting

**Current:** No rate limits (development)

**Production:** 
- 100 requests/minute per IP
- 1000 requests/hour per API key
- Burst limit: 10 requests/second

---

## Response Format

All responses are JSON with consistent structure:

### Success Response
```json
{
  "data": { ... },
  "meta": {
    "timestamp": "2024-11-24T16:43:00Z",
    "request_id": "req_abc123"
  }
}
```

### Error Response
```json
{
  "detail": "Error message",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-11-24T16:43:00Z"
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid parameters |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Parameter validation failed |
| 500 | Internal Error | Server error |

### Common Error Messages

```json
{
  "detail": "Campaign with ID 'INVALID' not found",
  "error_code": "NOT_FOUND"
}
```

---

## Endpoints

### Health Check

**Endpoint:** `GET /health`

Check API and database connectivity status.

#### Response

```json
{
  "status": "healthy",
  "neo4j_connected": true,
  "using_mock_data": false,
  "timestamp": "2024-11-24T16:43:00Z"
}
```

#### cURL Example

```bash
curl http://localhost:8000/health
```

---

### Top Suppliers by ROI

**Endpoint:** `GET /api/v1/suppliers/top-roi`

Get suppliers ranked by Return on Investment (ROI).

**ROI Formula:** `(Total Revenue from Campaigns) / (Total Spent on POs)`

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_roi` | float | 1.0 | Minimum ROI threshold (≥0) |
| `limit` | int | 10 | Max results (1-100) |
| `sort` | string | "desc" | Sort order: "asc" or "desc" |

#### Response

```json
{
  "suppliers": [
    {
      "supplier_id": "SUP-001",
      "supplier_name": "TechSupply GmbH",
      "total_spent": 150000.0,
      "total_revenue": 450000.0,
      "roi": 3.0,
      "campaign_count": 5,
      "po_count": 12
    }
  ],
  "total_count": 1,
  "min_roi_filter": 1.0
}
```

#### cURL Example

```bash
curl "http://localhost:8000/api/v1/suppliers/top-roi?min_roi=2.0&limit=5&sort=desc"
```

#### Python Example

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/suppliers/top-roi",
    params={"min_roi": 2.0, "limit": 5}
)

data = response.json()
for supplier in data["suppliers"]:
    print(f"{supplier['supplier_name']}: ROI {supplier['roi']:.2f}")
```

#### Business Use Cases

- Supplier performance reviews
- Budget allocation decisions
- Strategic partnership identification
- Procurement optimization

---

### Campaign Team Skill Gaps

**Endpoint:** `GET /api/v1/campaigns/{campaign_id}/team-gaps`

Analyze skill gaps in a campaign team by comparing required vs available skills.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `campaign_id` | string | Campaign identifier (e.g., "CAMP-001") |

#### Response

```json
{
  "campaign_id": "CAMP-001",
  "campaign_name": "Spring Launch 2024",
  "team_size": 8,
  "skill_gaps": [
    {
      "skill_name": "Python",
      "required_count": 3,
      "available_count": 1,
      "gap": 2,
      "severity": "High"
    }
  ],
  "total_gaps": 2,
  "critical_gaps": 1
}
```

#### Severity Levels

- **Critical**: Gap ≥ 3 or required skills completely missing
- **High**: Gap = 2
- **Medium**: Gap = 1
- **Low**: Gap < 1

#### cURL Example

```bash
curl "http://localhost:8000/api/v1/campaigns/CAMP-001/team-gaps"
```

#### Python Example

```python
import requests

campaign_id = "CAMP-001"
response = requests.get(
    f"http://localhost:8000/api/v1/campaigns/{campaign_id}/team-gaps"
)

if response.status_code == 200:
    data = response.json()
    print(f"Campaign: {data['campaign_name']}")
    print(f"Critical gaps: {data['critical_gaps']}")
    
    for gap in data['skill_gaps']:
        if gap['severity'] == 'Critical':
            print(f"  - Need {gap['gap']} more {gap['skill_name']} experts")
else:
    print(f"Campaign not found: {response.json()['detail']}")
```

#### Business Use Cases

- Hiring decisions
- Training program planning
- Resource reallocation
- Risk assessment

---

### High-Conversion Products

**Endpoint:** `GET /api/v1/products/high-conversion`

Get products with high conversion rates from marketing campaigns.

**Conversion Rate:** `(Total Conversions) / (Total Impressions)`

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `min_conversion` | float | 0.01 | Minimum conversion rate (0-1) |
| `category` | string | null | Optional category filter |
| `limit` | int | 10 | Max results (1-100) |

#### Response

```json
{
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
  "min_conversion_filter": 0.01,
  "category_filter": null
}
```

#### Conversion Benchmarks

- **0.05+ (5%)**: Excellent conversion
- **0.03-0.05 (3-5%)**: Good conversion
- **0.01-0.03 (1-3%)**: Average conversion
- **<0.01 (<1%)**: Poor conversion

#### cURL Example

```bash
curl "http://localhost:8000/api/v1/products/high-conversion?min_conversion=0.03&category=Electronics&limit=5"
```

#### Python Example

```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/products/high-conversion",
    params={
        "min_conversion": 0.03,
        "category": "Electronics",
        "limit": 10
    }
)

data = response.json()
for product in data["products"]:
    print(f"{product['product_name']}: {product['conversion_rate']:.1%} conversion")
```

#### Business Use Cases

- Marketing budget allocation
- Product portfolio optimization
- Campaign planning
- Inventory decisions

---

### Supplier Risk Assessment

**Endpoint:** `GET /api/v1/suppliers/{supplier_id}/risk`

Get comprehensive risk assessment for a supplier.

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `supplier_id` | string | Supplier identifier (e.g., "SUP-001") |

#### Response

```json
{
  "supplier_id": "SUP-001",
  "supplier_name": "TechSupply GmbH",
  "overall_risk_score": 35.5,
  "risk_level": "low",
  "total_outstanding": 50000.0,
  "overdue_invoices": 1,
  "overdue_amount": 5000.0,
  "on_time_delivery_rate": 0.95,
  "quality_score": 0.92,
  "active_contracts": 3,
  "risk_flags": []
}
```

#### Risk Scoring

| Score | Level | Description |
|-------|-------|-------------|
| 0-30 | Low | Reliable supplier |
| 31-60 | Medium | Minor concerns |
| 61-80 | High | Significant issues |
| 81-100 | Critical | Immediate action needed |

#### Risk Factors

- **Payment history** (30% weight)
- **Delivery performance** (25% weight)
- **Quality metrics** (25% weight)
- **Financial stability** (20% weight)

#### cURL Example

```bash
curl "http://localhost:8000/api/v1/suppliers/SUP-001/risk"
```

#### Python Example

```python
import requests

supplier_id = "SUP-001"
response = requests.get(
    f"http://localhost:8000/api/v1/suppliers/{supplier_id}/risk"
)

if response.status_code == 200:
    data = response.json()
    risk_level = data['risk_level']
    risk_score = data['overall_risk_score']
    
    print(f"Supplier: {data['supplier_name']}")
    print(f"Risk: {risk_level.upper()} ({risk_score:.1f}/100)")
    
    if data['risk_flags']:
        print("⚠️  Risk Flags:")
        for flag in data['risk_flags']:
            print(f"  - {flag}")
    else:
        print("✅ No risk flags")
else:
    print(f"Supplier not found: {response.json()['detail']}")
```

#### Business Use Cases

- Vendor evaluation
- Procurement decisions
- Risk mitigation planning
- Contract renewals

---

## Code Examples

### Complete Python Client

```python
"""HelixGraph API Client Example"""

import requests
from typing import Dict, List, Optional

class HelixGraphClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_top_suppliers(
        self,
        min_roi: float = 1.0,
        limit: int = 10,
        sort: str = "desc"
    ) -> List[Dict]:
        """Get top suppliers by ROI"""
        response = self.session.get(
            f"{self.base_url}/api/v1/suppliers/top-roi",
            params={"min_roi": min_roi, "limit": limit, "sort": sort}
        )
        response.raise_for_status()
        return response.json()["suppliers"]
    
    def get_campaign_gaps(self, campaign_id: str) -> Dict:
        """Get skill gaps for a campaign"""
        response = self.session.get(
            f"{self.base_url}/api/v1/campaigns/{campaign_id}/team-gaps"
        )
        response.raise_for_status()
        return response.json()
    
    def get_high_conversion_products(
        self,
        min_conversion: float = 0.01,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get high-conversion products"""
        params = {"min_conversion": min_conversion, "limit": limit}
        if category:
            params["category"] = category
        
        response = self.session.get(
            f"{self.base_url}/api/v1/products/high-conversion",
            params=params
        )
        response.raise_for_status()
        return response.json()["products"]
    
    def get_supplier_risk(self, supplier_id: str) -> Dict:
        """Get supplier risk assessment"""
        response = self.session.get(
            f"{self.base_url}/api/v1/suppliers/{supplier_id}/risk"
        )
        response.raise_for_status()
        return response.json()


# Usage example
if __name__ == "__main__":
    client = HelixGraphClient()
    
    # Check health
    health = client.health_check()
    print(f"API Status: {health['status']}")
    
    # Get top suppliers
    suppliers = client.get_top_suppliers(min_roi=2.0, limit=5)
    print(f"\nTop {len(suppliers)} Suppliers:")
    for s in suppliers:
        print(f"  - {s['supplier_name']}: ROI {s['roi']:.2f}")
    
    # Get campaign gaps
    try:
        gaps = client.get_campaign_gaps("CAMP-001")
        print(f"\nCampaign: {gaps['campaign_name']}")
        print(f"Critical gaps: {gaps['critical_gaps']}")
    except requests.HTTPError as e:
        print(f"Campaign not found: {e}")
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

class HelixGraphClient {
  async healthCheck() {
    const response = await axios.get(`${BASE_URL}/health`);
    return response.data;
  }
  
  async getTopSuppliers(minRoi = 1.0, limit = 10) {
    const response = await axios.get(`${BASE_URL}/api/v1/suppliers/top-roi`, {
      params: { min_roi: minRoi, limit }
    });
    return response.data.suppliers;
  }
  
  async getCampaignGaps(campaignId) {
    const response = await axios.get(
      `${BASE_URL}/api/v1/campaigns/${campaignId}/team-gaps`
    );
    return response.data;
  }
}

// Usage
(async () => {
  const client = new HelixGraphClient();
  
  const health = await client.healthCheck();
  console.log(`API Status: ${health.status}`);
  
  const suppliers = await client.getTopSuppliers(2.0, 5);
  console.log(`\nTop ${suppliers.length} Suppliers:`);
  suppliers.forEach(s => {
    console.log(`  - ${s.supplier_name}: ROI ${s.roi.toFixed(2)}`);
  });
})();
```

---

## Postman Collection

### Import Instructions

1. Open Postman
2. Click **Import** > **Link**
3. Enter: `http://localhost:8000/openapi.json`
4. Postman will auto-generate all endpoints

### Or Download JSON

Download: [`HelixGraph_API.postman_collection.json`](./HelixGraph_API.postman_collection.json)

### Environment Variables

Create a Postman environment with:

```json
{
  "base_url": "http://localhost:8000",
  "api_key": "your_api_key_here"
}
```

---

## Interactive Documentation

### Swagger UI

**URL:** `http://localhost:8000/docs`

Features:
- Try endpoints directly in browser
- See request/response schemas
- Test with different parameters
- No additional tools needed

### ReDoc

**URL:** `http://localhost:8000/redoc`

Features:
- Clean, readable documentation
- Code examples in multiple languages
- Printable format
- Better for reference

---

## Support & Contact

- **GitHub Issues:** (Add repository URL)
- **Email:** ivan.guoyixuan@gmail.com
- **Documentation:** Check `/docs` endpoint for latest

---

## Changelog

### Version 1.0 (Nov 2024)
- ✅ Initial API release
- ✅ 4 fixed query endpoints
- ✅ Real Neo4j integration
- ✅ Comprehensive documentation
- ✅ Integration tests

### Upcoming Features
- 🔄 Authentication & API keys
- 🔄 Rate limiting
- 🔄 Webhooks
- 🔄 Batch operations
- 🔄 GraphQL endpoint

---

**Last Updated:** November 24, 2024  
**API Version:** 1.0  
**Documentation Version:** 1.0
