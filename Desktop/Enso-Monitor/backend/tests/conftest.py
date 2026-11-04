import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Fournit un client HTTP de test pour toute la suite de tests."""
    return TestClient(app)
