import io
import logging
import numpy as np
import pandas as pd
from datetime import date

logger = logging.getLogger(__name__)

# Mapping saison → mois de représentation (1er jour du mois central)
# Ex : DJF (Déc-Jan-Fév) → mois 1 (Janvier) de l'année indiquée par la NOAA
SEASON_TO_MONTH = {
    "DJF": 1,
    "JFM": 2,
    "FMA": 3,
    "MAM": 4,
    "AMJ": 5,
    "MJJ": 6,
    "JJA": 7,
    "JAS": 8,
    "ASO": 9,
    "SON": 10,
    "OND": 11,
    "NDJ": 12,
}

VALID_SEASONS = set(SEASON_TO_MONTH.keys())

# Valeur sentinelle NOAA pour les données manquantes
MISSING_VALUE = -999.0


def parse_raw(raw_text: str) -> pd.DataFrame:
    """Parse le texte brut NOAA (séparé par espaces) en DataFrame."""
    df = pd.read_csv(io.StringIO(raw_text), sep=r"\s+")
    logger.info(f"Lignes brutes lues : {len(df)}")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Nettoie, transforme et valide les données ONI brutes.

    Étapes :
    1. Renommage des colonnes
    2. Suppression des saisons invalides
    3. Conversion des types numériques
    4. Remplacement des valeurs sentinelles (-999) par NaN
    5. Suppression des lignes sans année ou sans valeur ONI
    6. Création de la colonne period_start (date du 1er du mois)
    7. Détection et suppression des doublons
    8. Tri chronologique
    """
    df = df.copy()

    # 1. Renommer les colonnes
    df.columns = ["season", "year", "sst_total", "oni"]

    # 2. Supprimer les lignes avec saisons invalides
    before = len(df)
    df = df[df["season"].isin(VALID_SEASONS)]
    dropped = before - len(df)
    if dropped:
        logger.warning(f"{dropped} lignes supprimées : saison invalide")

    # 3. Convertir les types numériques
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["sst_total"] = pd.to_numeric(df["sst_total"], errors="coerce")
    df["oni"] = pd.to_numeric(df["oni"], errors="coerce")

    # 4. Remplacer les valeurs sentinelles NOAA par NaN
    df["sst_total"] = df["sst_total"].replace(MISSING_VALUE, np.nan)
    df["oni"] = df["oni"].replace(MISSING_VALUE, np.nan)

    # 5. Supprimer les lignes sans year ou sans oni
    before = len(df)
    df = df.dropna(subset=["year", "oni"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"{dropped} lignes supprimées : year ou oni manquant")

    # 6. Créer period_start : 1er jour du mois correspondant à la saison
    df["period_start"] = df.apply(
        lambda row: date(int(row["year"]), SEASON_TO_MONTH[row["season"]], 1),
        axis=1,
    )

    # 7. Supprimer les doublons (même saison + même année)
    before = len(df)
    df = df.drop_duplicates(subset=["season", "year"])
    dropped = before - len(df)
    if dropped:
        logger.warning(f"{dropped} doublons supprimés")

    # 8. Trier par date croissante
    df = df.sort_values("period_start").reset_index(drop=True)

    logger.info(f"Données nettoyées : {len(df)} observations valides")
    return df


def add_provenance(df: pd.DataFrame, provenance: dict) -> pd.DataFrame:
    """Ajoute les colonnes de traçabilité de la source."""
    df = df.copy()
    df["source"] = provenance["source"]
    df["source_url"] = provenance["source_url"]
    df["extraction_date"] = provenance["extraction_date"]
    return df
