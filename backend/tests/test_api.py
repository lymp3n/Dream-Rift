"""Integration tests for API."""

import pytest
from fastapi.testclient import TestClient
from backend.src.api.main import app

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Dreamforge" in data["message"]


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_locations_list():
    """Test locations list endpoint."""
    response = client.get("/api/locations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

