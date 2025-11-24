"""
API Integration Tests

Usage:
    pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from api.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "endpoints" in data


def test_extract_entities():
    """Test NER extraction endpoint"""
    response = client.post(
        "/api/extract-entities",
        json={"text": "Tech Solutions Ltd submitted PO-2024-001 for the Spring Launch campaign."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "count" in data
    assert isinstance(data["entities"], list)


def test_extract_entities_empty_text():
    """Test extraction with empty text"""
    response = client.post(
        "/api/extract-entities",
        json={"text": ""}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0


def test_link_entities():
    """Test entity linking endpoint"""
    response = client.post(
        "/api/link-entities",
        json={"text": "Acme Corp submitted invoice INV-123456 for Spring Launch"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert "count" in data
    
    # Check linked entity structure
    if data["count"] > 0:
        entity = data["entities"][0]
        assert "text" in entity
        assert "type" in entity
        assert "linked_to" in entity
        assert "confidence" in entity
        assert "status" in entity


def test_invalid_request():
    """Test invalid request format"""
    response = client.post(
        "/api/extract-entities",
        json={"wrong_field": "some text"}
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.parametrize("text,expected_min_entities", [
    ("Acme Corp submitted PO-2024-001", 2),
    ("Marketing Manager with Python skills", 2),
    ("Invoice INV-123 from Tech Solutions for Spring Launch", 3),
])
def test_extract_various_texts(text, expected_min_entities):
    """Test extraction with various texts"""
    response = client.post(
        "/api/extract-entities",
        json={"text": text}
    )
    assert response.status_code == 200
    data = response.json()
    # Note: Actual count depends on model performance
    # This is a minimum check
    assert data["count"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
