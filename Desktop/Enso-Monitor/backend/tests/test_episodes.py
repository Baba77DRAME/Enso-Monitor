"""
Tests de la route /api/v1/episodes/.

Les données utilisées sont des FIXTURES DE TEST (pas des valeurs NOAA).
Elles forment deux épisodes contrôlés : 1 El Niño (6 saisons) + 1 La Niña (5 saisons).
"""

import pytest


# ---------------------------------------------------------------------------
# Liste des épisodes
# ---------------------------------------------------------------------------

def test_list_episodes_status_200(episode_client):
    r = episode_client.get("/api/v1/episodes/")
    assert r.status_code == 200


def test_list_episodes_returns_two_episodes(episode_client):
    r = episode_client.get("/api/v1/episodes/")
    episodes = r.json()
    assert len(episodes) == 2


def test_list_episodes_types(episode_client):
    r = episode_client.get("/api/v1/episodes/")
    types = {ep["type"] for ep in r.json()}
    assert "el_nino" in types
    assert "la_nina" in types


def test_all_episodes_meet_minimum_duration(episode_client):
    r = episode_client.get("/api/v1/episodes/")
    for ep in r.json():
        assert ep["duration"] >= 5


def test_el_nino_episode_peak(episode_client):
    r = episode_client.get("/api/v1/episodes/")
    nino = next(ep for ep in r.json() if ep["type"] == "el_nino")
    assert nino["peak_oni"] == pytest.approx(2.3, abs=0.01)


def test_la_nina_episode_peak(episode_client):
    r = episode_client.get("/api/v1/episodes/")
    nina = next(ep for ep in r.json() if ep["type"] == "la_nina")
    assert nina["peak_oni"] == pytest.approx(-1.2, abs=0.01)


def test_episodes_sorted_chronologically(episode_client):
    r = episode_client.get("/api/v1/episodes/")
    years = [ep["start_year"] for ep in r.json()]
    assert years == sorted(years)


# ---------------------------------------------------------------------------
# Détail d'un épisode
# ---------------------------------------------------------------------------

def test_episode_detail_status_200(episode_client):
    r = episode_client.get("/api/v1/episodes/1")
    assert r.status_code == 200


def test_episode_detail_has_observations(episode_client):
    r = episode_client.get("/api/v1/episodes/1")
    ep = r.json()
    assert "observations" in ep
    assert len(ep["observations"]) >= 5


def test_episode_detail_observations_have_oni(episode_client):
    r = episode_client.get("/api/v1/episodes/1")
    for obs in r.json()["observations"]:
        assert "oni" in obs
        assert obs["oni"] is not None


def test_episode_not_found_returns_404(episode_client):
    r = episode_client.get("/api/v1/episodes/999")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Cas sans données : aucun épisode identifiable
# ---------------------------------------------------------------------------

def test_no_episodes_when_database_empty(empty_db_client):
    r = empty_db_client.get("/api/v1/episodes/")
    assert r.status_code == 200
    assert r.json() == []
