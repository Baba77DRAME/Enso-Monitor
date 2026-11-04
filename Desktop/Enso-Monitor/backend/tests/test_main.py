"""
Tests des routes principales de l'API ENSO Monitor.

TestClient (fourni par httpx) simule des requêtes HTTP réelles
sans démarrer de vrai serveur réseau.
"""


def test_root_status_200(client):
    """La route GET / doit retourner un code HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_root_contains_message(client):
    """La route GET / doit retourner un champ 'message'."""
    response = client.get("/")
    data = response.json()
    assert "message" in data
    assert "ENSO Monitor API" in data["message"]


def test_root_contains_version(client):
    """La route GET / doit retourner un champ 'version'."""
    response = client.get("/")
    data = response.json()
    assert "version" in data


def test_root_contains_docs_link(client):
    """La route GET / doit indiquer le lien vers /docs."""
    response = client.get("/")
    data = response.json()
    assert data["docs"] == "/docs"


def test_health_status_200(client):
    """La route GET /health doit retourner un code HTTP 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_ok(client):
    """La route GET /health doit retourner status: ok."""
    response = client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


def test_health_returns_service_name(client):
    """La route GET /health doit identifier le service."""
    response = client.get("/health")
    data = response.json()
    assert "service" in data
