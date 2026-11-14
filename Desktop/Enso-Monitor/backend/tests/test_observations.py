"""
Tests de la route GET /api/v1/observations.

Les données utilisées ici sont fictives (TEST_OBSERVATIONS dans conftest.py).
Elles ne représentent pas des valeurs ONI officielles.
"""


# ---------------------------------------------------------------------------
# Test 1 : récupération de toutes les observations
# ---------------------------------------------------------------------------

def test_list_observations_returns_all(db_client):
    """Sans filtre, toutes les observations doivent être retournées."""
    response = db_client.get("/api/v1/observations")
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 4
    assert len(data["results"]) == 4
    assert data["page"] == 1
    assert data["page_size"] == 50


def test_list_observations_structure(db_client):
    """Chaque observation doit contenir les champs attendus."""
    response = db_client.get("/api/v1/observations")
    obs = response.json()["results"][0]

    assert "id" in obs
    assert "season" in obs
    assert "year" in obs
    assert "period_start" in obs
    assert "oni" in obs
    assert "source" in obs


def test_list_observations_sorted_by_date(db_client):
    """Les observations doivent être triées par period_start croissant."""
    response = db_client.get("/api/v1/observations")
    results = response.json()["results"]
    dates = [r["period_start"] for r in results]
    assert dates == sorted(dates)


# ---------------------------------------------------------------------------
# Test 2 : filtre temporel
# ---------------------------------------------------------------------------

def test_filter_by_start_date(db_client):
    """start_date doit exclure les observations antérieures."""
    response = db_client.get("/api/v1/observations?start_date=2005-01-01")
    data = response.json()
    assert data["total"] == 2
    for obs in data["results"]:
        assert obs["period_start"] >= "2005-01-01"


def test_filter_by_end_date(db_client):
    """end_date doit exclure les observations postérieures."""
    response = db_client.get("/api/v1/observations?end_date=2000-12-31")
    data = response.json()
    assert data["total"] == 2
    for obs in data["results"]:
        assert obs["period_start"] <= "2000-12-31"


def test_filter_by_start_and_end_date(db_client):
    """start_date et end_date combinés doivent filtrer correctement."""
    response = db_client.get(
        "/api/v1/observations?start_date=2000-07-01&end_date=2005-12-31"
    )
    data = response.json()
    assert data["total"] == 2


# ---------------------------------------------------------------------------
# Test 3 : rejet d'une entrée invalide
# ---------------------------------------------------------------------------

def test_reject_invalid_date_format(db_client):
    """Une date au mauvais format doit retourner 422."""
    response = db_client.get("/api/v1/observations?start_date=not-a-date")
    assert response.status_code == 422


def test_reject_start_date_after_end_date(db_client):
    """start_date postérieure à end_date doit retourner 422."""
    response = db_client.get(
        "/api/v1/observations?start_date=2010-01-01&end_date=2000-01-01"
    )
    assert response.status_code == 422
    assert "start_date" in response.json()["detail"].lower()


def test_reject_invalid_page_size(db_client):
    """page_size=0 doit retourner 422 (ge=1)."""
    response = db_client.get("/api/v1/observations?page_size=0")
    assert response.status_code == 422


def test_reject_page_size_too_large(db_client):
    """page_size > 200 doit retourner 422 (le=200)."""
    response = db_client.get("/api/v1/observations?page_size=201")
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Test 4 : cas sans résultat
# ---------------------------------------------------------------------------

def test_no_results_for_out_of_range_dates(db_client):
    """Une plage de dates sans données doit retourner total=0 et results=[]."""
    response = db_client.get(
        "/api/v1/observations?start_date=1800-01-01&end_date=1899-12-31"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["results"] == []


# ---------------------------------------------------------------------------
# Test 5 : pagination
# ---------------------------------------------------------------------------

def test_pagination_page_size(db_client):
    """page_size=2 doit retourner 2 résultats sur 4 au total."""
    response = db_client.get("/api/v1/observations?page_size=2")
    data = response.json()
    assert data["total"] == 4
    assert len(data["results"]) == 2
    assert data["page_size"] == 2


def test_pagination_second_page(db_client):
    """La page 2 avec page_size=2 doit retourner les 2 observations restantes."""
    response = db_client.get("/api/v1/observations?page=2&page_size=2")
    data = response.json()
    assert data["total"] == 4
    assert len(data["results"]) == 2
    assert data["page"] == 2
