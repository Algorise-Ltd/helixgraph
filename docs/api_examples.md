# HelixGraph API — Example Requests & Responses

This document shows example calls and outputs for the HelixGraph Product & API Foundation endpoints.  
All requests require an API key via the header `X-API-Key`.

---

## 1. Health Check

**Request**
```bash
GET /health
```

**Response**
```json
{
  "status": "ok"
}
```

---

## 2. List All Canonical Questions

**Request**
```bash
GET /questions
-H "X-API-Key: dev-key"
```

**Response**
```json
[
  {"id": "Q001", "text": "Top 10 high-value customers", "priority": "High"},
  {"id": "Q002", "text": "Marketing campaigns with highest conversion rate", "priority": "High"},
  {"id": "Q003", "text": "Average order frequency per customer by region", "priority": "Medium"}
]
```

---

## 3. Get Question Details

**Request**
```bash
GET /questions/Q001
-H "X-API-Key: dev-key"
```

**Response**
```json
{
  "id": "Q001",
  "text": "Top 10 high-value customers",
  "priority": "High",
  "entities": ["Customer", "Order"],
  "relationships": ["Customer→Order"],
  "expected_metrics": ["total_revenue", "order_count"],
  "test_scenario": "Return customers sorted by total_revenue descending"
}
```

---

## 4. Retrieve Schema Definition

**Request**
```bash
GET /schema/Q001
-H "X-API-Key: dev-key"
```

**Response**
```json
{
  "title": "Q1Schema",
  "type": "object",
  "properties": {
    "customer_id": {"type": "integer"},
    "total_revenue": {"type": "number"},
    "order_count": {"type": "integer"}
  },
  "required": ["customer_id", "total_revenue", "order_count"]
}
```

---

## 5. Run Example Question (Stub Result)

**Request**
```bash
POST /run/Q001
-H "X-API-Key: dev-key"
```

**Response**
```json
[
  {
    "customer_id": 0,
    "total_revenue": 0,
    "order_count": 0
  }
]
```

This output is generated from the Pydantic schema (a placeholder).  
Later, real computation logic will replace this stub.

---

## Summary of Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| GET | `/health` | API availability check |
| GET | `/questions` | List all canonical questions |
| GET | `/questions/{qid}` | Get details for a specific question |
| GET | `/schema/{qid}` | Retrieve schema definition |
| POST | `/run/{qid}` | Run query and get structured output |

---

Version: v0.1.0  
Maintainer: Product & API Foundation Team
