import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import insert

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
    Retourne une liste de dicts prêts pour SQLAlchemy.
    """
    df_db = df[DB_COLUMNS].copy()
    records = df_db.to_dict(orient="records")
    logger.info(f"{len(records)} enregistrements prêts pour la base de données")
    return records


def insert_observations(records: list[dict], database_url: str) -> dict:
    """
    Insère les observations dans PostgreSQL.

    Utilise INSERT ... ON CONFLICT DO NOTHING pour éviter les doublons
    lors d'imports successifs (la contrainte uq_observation_season_year
    garantit l'unicité).

    Retourne un dict avec le nombre d'insérés et d'ignorés.
    """
    from sqlalchemy import Table, MetaData

    engine = create_engine(database_url)

    # Charge la table observations depuis la BDD (sans redéfinir le modèle)
    metadata = MetaData()
    metadata.reflect(bind=engine, only=["observations"])
    observations_table = metadata.tables["observations"]

    inserted = 0
    skipped = 0

    with engine.begin() as conn:
        for record in records:
            stmt = (
                insert(observations_table)
                .values(**record)
                .on_conflict_do_nothing(constraint="uq_observation_season_year")
            )
            result = conn.execute(stmt)
            if result.rowcount == 1:
                inserted += 1
            else:
                skipped += 1

    logger.info(f"Insertions : {inserted} nouvelles, {skipped} ignorées (doublons)")
    return {"inserted": inserted, "skipped": skipped}
