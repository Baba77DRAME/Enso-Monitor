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


# ===========================================================================
# TEST FONCTIONNEL 1 — ETL
# Vérifier qu'une observation ONI est correctement transformée depuis le
# format texte brut NOAA vers le format interne.
# ===========================================================================

def test_functional_etl_parse_raw_noaa_text_to_internal_format():
    """
    TEST FONCTIONNEL 1 — ETL (exigé) :
    Transforme une observation depuis le format texte brut NOAA
    (colonnes SEAS YR TOTAL ANOM séparées par espaces) jusqu'au
    format interne (season, year, sst_total, oni, period_start).

    Simule exactement ce que fait extract.py + transform.py en production.
    """
    from etl.transform import parse_raw

    # Texte au format exact du fichier NOAA (en-tête + 2 lignes de données)
    raw_text = (
        "SEAS  YR TOTAL ANOM\n"
        " DJF 1997 28.11  2.09\n"
        " JFM 1997 28.33  2.21\n"
    )

    df_raw = parse_raw(raw_text)
    df_clean = clean(df_raw)

    # Structure attendue
    assert len(df_clean) == 2
    assert list(df_clean.columns[:4]) == ["season", "year", "sst_total", "oni"]
    assert "period_start" in df_clean.columns

    # Première observation : DJF 1997
    row = df_clean.iloc[0]
    assert row["season"] == "DJF"
    assert row["year"] == 1997
    assert row["oni"] == pytest.approx(2.09)
    assert row["sst_total"] == pytest.approx(28.11)
    assert row["period_start"] == date(1997, 1, 1)   # DJF → janvier

    # Deuxième observation : JFM 1997
    row2 = df_clean.iloc[1]
    assert row2["season"] == "JFM"
    assert row2["period_start"] == date(1997, 2, 1)  # JFM → février


def test_functional_etl_negative_oni_la_nina_preserved():
    """
    TEST FONCTIONNEL 1b — ETL (cas La Niña) :
    Une valeur ONI négative doit traverser la transformation sans modification
    de signe ni d'arrondi, pour ne pas inverser un épisode La Niña en El Niño.
    """
    from etl.transform import parse_raw

    raw_text = (
        "SEAS  YR TOTAL ANOM\n"
        " DJF 1988 25.90 -1.85\n"
    )

    df_raw = parse_raw(raw_text)
    df_clean = clean(df_raw)

    oni_value = df_clean.iloc[0]["oni"]
    assert oni_value < 0, "Une valeur ONI La Niña doit rester négative"
    assert oni_value == pytest.approx(-1.85)


def test_functional_etl_output_types_are_correct():
    """
    TEST FONCTIONNEL 1c — ETL (types de données) :
    Les types de sortie doivent être compatibles avec l'insertion en BDD :
    - year : entier
    - oni : float
    - sst_total : float ou NaN
    - period_start : datetime.date
    """
    from etl.transform import parse_raw

    raw_text = (
        "SEAS  YR TOTAL ANOM\n"
        " ASO 2023 27.50  1.60\n"
    )

    df_raw = parse_raw(raw_text)
    df_clean = clean(df_raw)
    row = df_clean.iloc[0]

    assert isinstance(row["period_start"], date)
    assert isinstance(float(row["oni"]), float)
    assert isinstance(float(row["sst_total"]), float)
