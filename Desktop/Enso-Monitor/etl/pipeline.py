"""
Pipeline ETL ENSO Monitor.

Orchestration complète : Extract → Transform → Load (préparation BDD).
L'insertion réelle dans PostgreSQL sera réalisée à l'étape suivante.

Usage :
    cd /Users/babadrame/Desktop/Enso-Monitor
    source etl/.venv/bin/activate
    python -m etl.pipeline
"""

import logging

from etl.extract import fetch_oni_raw
from etl.load import prepare_for_db
from etl.transform import add_provenance, clean, parse_raw

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)


def run() -> tuple:
    """
    Exécute le pipeline ETL complet.

    Retourne :
        df_final  : DataFrame nettoyé avec colonnes de provenance
        records   : liste de dicts prêts pour SQLAlchemy
    """
    logger.info("=== Démarrage du pipeline ETL ENSO Monitor ===")

    # --- EXTRACT ---
    raw_text, provenance = fetch_oni_raw()

    # --- TRANSFORM ---
    df_raw = parse_raw(raw_text)
    df_clean = clean(df_raw)
    df_final = add_provenance(df_clean, provenance)

    # --- LOAD (préparation) ---
    records = prepare_for_db(df_final)

    logger.info(f"=== Pipeline terminé : {len(records)} observations préparées ===")
    logger.info(
        f"Période couverte : "
        f"{df_final['period_start'].min()} → {df_final['period_start'].max()}"
    )

    return df_final, records


if __name__ == "__main__":
    run()
