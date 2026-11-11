"""
Pipeline ETL ENSO Monitor.

Orchestration complète : Extract → Transform → Load (insertion PostgreSQL).

Usage :
    cd /Users/babadrame/Desktop/Enso-Monitor
    source etl/.venv/bin/activate
    python -m etl.pipeline
    python -m etl.pipeline --db-url postgresql://enso_user:enso_password@localhost:5432/enso_monitor
"""

import argparse
import logging

from etl.extract import fetch_oni_raw
from etl.load import insert_observations, prepare_for_db
from etl.transform import add_provenance, clean, parse_raw

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

DEFAULT_DB_URL = "postgresql://enso_user:enso_password@localhost:5432/enso_monitor"


def run(database_url: str = DEFAULT_DB_URL) -> tuple:
    """
    Exécute le pipeline ETL complet.

    Étapes :
    1. Extract  : télécharge les données ONI depuis la NOAA
    2. Transform: nettoie, valide et enrichit les données
    3. Load     : insère dans PostgreSQL (ON CONFLICT DO NOTHING)

    Retourne :
        df_final : DataFrame nettoyé avec colonnes de provenance
        stats    : dict {"inserted": N, "skipped": N}
    """
    logger.info("=== Démarrage du pipeline ETL ENSO Monitor ===")

    # --- EXTRACT ---
    raw_text, provenance = fetch_oni_raw()

    # --- TRANSFORM ---
    df_raw = parse_raw(raw_text)
    df_clean = clean(df_raw)
    df_final = add_provenance(df_clean, provenance)

    # --- LOAD ---
    records = prepare_for_db(df_final)
    stats = insert_observations(records, database_url)

    logger.info(f"=== Pipeline terminé : {stats['inserted']} insérées, {stats['skipped']} ignorées ===")
    logger.info(
        f"Période couverte : "
        f"{df_final['period_start'].min()} → {df_final['period_start'].max()}"
    )

    return df_final, stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline ETL ENSO Monitor")
    parser.add_argument(
        "--db-url",
        default=DEFAULT_DB_URL,
        help="URL de connexion PostgreSQL",
    )
    args = parser.parse_args()
    run(database_url=args.db_url)
