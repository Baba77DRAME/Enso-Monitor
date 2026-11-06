"""
Tests unitaires du module etl/transform.py.

IMPORTANT : toutes les données utilisées ici sont fictives et inventées
uniquement pour tester la logique de transformation.
Elles ne représentent en aucun cas des valeurs ONI officielles.
"""

import pandas as pd
import numpy as np
import pytest
from datetime import date

from etl.transform import clean, add_provenance, SEASON_TO_MONTH


# ---------------------------------------------------------------------------
# Utilitaire : construire un DataFrame brut au format NOAA (SEAS YR TOTAL ANOM)
# ---------------------------------------------------------------------------

def make_raw(rows: list[tuple]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=["SEAS", "YR", "TOTAL", "ANOM"])


# ---------------------------------------------------------------------------
# Test 1 : transformation d'une observation valide
# ---------------------------------------------------------------------------

def test_transform_single_valid_observation():
    """Une ligne valide doit être transformée sans perte ni modification."""
    df = make_raw([("DJF", 1950, 25.01, -1.32)])
    result = clean(df)

    assert len(result) == 1
    assert result.iloc[0]["season"] == "DJF"
    assert result.iloc[0]["year"] == 1950
    assert result.iloc[0]["oni"] == pytest.approx(-1.32)
    assert result.iloc[0]["sst_total"] == pytest.approx(25.01)


# ---------------------------------------------------------------------------
# Test 2 : conversion des dates (period_start)
# ---------------------------------------------------------------------------

def test_period_start_conversion():
    """Chaque saison doit être convertie en la bonne date (1er du mois)."""
    df = make_raw([
        ("DJF", 2000, 26.5,  0.5),   # → 2000-01-01
        ("JJA", 2000, 27.0,  1.0),   # → 2000-07-01
        ("NDJ", 2000, 25.0, -0.5),   # → 2000-12-01
        ("MAM", 1990, 26.2, -0.3),   # → 1990-04-01
    ])
    result = clean(df)
    dates = {row["season"]: row["period_start"] for _, row in result.iterrows()}

    assert dates["DJF"] == date(2000, 1, 1)
    assert dates["JJA"] == date(2000, 7, 1)
    assert dates["NDJ"] == date(2000, 12, 1)
    assert dates["MAM"] == date(1990, 4, 1)


def test_all_seasons_have_a_month_mapping():
    """Les 12 saisons doivent toutes avoir un mois défini dans SEASON_TO_MONTH."""
    expected = {"DJF","JFM","FMA","MAM","AMJ","MJJ","JJA","JAS","ASO","SON","OND","NDJ"}
    assert set(SEASON_TO_MONTH.keys()) == expected


# ---------------------------------------------------------------------------
# Test 3 : conversion des valeurs numériques
# ---------------------------------------------------------------------------

def test_numeric_conversion_from_strings():
    """Les valeurs en chaîne doivent être converties en float."""
    df = make_raw([("MAM", 1980, "26.10", "-0.75")])
    result = clean(df)

    assert isinstance(result.iloc[0]["oni"], float)
    assert isinstance(result.iloc[0]["sst_total"], float)
    assert result.iloc[0]["oni"] == pytest.approx(-0.75)
    assert result.iloc[0]["sst_total"] == pytest.approx(26.10)


# ---------------------------------------------------------------------------
# Test 4 : détection et suppression des doublons
# ---------------------------------------------------------------------------

def test_duplicate_detection():
    """Deux lignes identiques (même saison, même année) → une seule conservée."""
    df = make_raw([
        ("DJF", 2010, 26.0, 0.3),
        ("DJF", 2010, 26.0, 0.3),  # doublon exact
    ])
    result = clean(df)
    assert len(result) == 1


# ---------------------------------------------------------------------------
# Test 5 : gestion des données invalides
# ---------------------------------------------------------------------------

def test_missing_value_sentinel_removed():
    """Les valeurs sentinelles -999 (NOAA) doivent être converties en NaN puis supprimées."""
    df = make_raw([
        ("DJF", 2010, 26.0, -999.0),  # oni manquant → ligne supprimée
        ("SON", 2010, 26.0,   0.8),   # valide → conservée
    ])
    result = clean(df)
    assert len(result) == 1
    assert result.iloc[0]["season"] == "SON"


def test_invalid_season_removed():
    """Une saison inconnue doit être supprimée."""
    df = make_raw([
        ("XYZ", 2010, 26.0, 0.5),  # invalide
        ("MAM", 2010, 26.0, 0.5),  # valide
    ])
    result = clean(df)
    assert len(result) == 1
    assert result.iloc[0]["season"] == "MAM"


def test_missing_year_removed():
    """Une ligne sans année doit être supprimée."""
    df = make_raw([
        ("MAM", None, 26.0, 0.5),  # année manquante
        ("SON", 2010, 26.0, 0.8),  # valide
    ])
    result = clean(df)
    assert len(result) == 1
    assert result.iloc[0]["season"] == "SON"


# ---------------------------------------------------------------------------
# Test 6 : ajout de la provenance
# ---------------------------------------------------------------------------

def test_provenance_added():
    """Les colonnes source, source_url et extraction_date doivent être présentes."""
    df = make_raw([("JJA", 2005, 27.0, 1.2)])
    df_clean = clean(df)
    provenance = {
        "source": "NOAA CPC - ONI v6",
        "source_url": "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt",
        "extraction_date": "2026-11-05T00:00:00+00:00",
    }
    result = add_provenance(df_clean, provenance)

    assert result.iloc[0]["source"] == "NOAA CPC - ONI v6"
    assert "source_url" in result.columns
    assert "extraction_date" in result.columns
