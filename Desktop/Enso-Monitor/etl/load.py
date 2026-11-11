import logging
import pandas as pd

logger = logging.getLogger(__name__)

# Colonnes exportées vers la base de données
DB_COLUMNS = [
    "season",
    "year",
    "period_start",
    "sst_total",
    "oni",
    "source",
    "source_url",
    "extraction_date",
]


def prepare_for_db(df: pd.DataFrame) -> list[dict]:
    """
    Prépare les données transformées pour l'insertion en base de données.

    Sélectionne uniquement les colonnes utiles et retourne
    une liste de dicts prêts pour SQLAlchemy (insert par batch).
    L'insertion réelle dans PostgreSQL sera faite à l'étape suivante.
    """
    df_db = df[DB_COLUMNS].copy()
    records = df_db.to_dict(orient="records")
    logger.info(f"{len(records)} enregistrements prêts pour la base de données")
    return records
