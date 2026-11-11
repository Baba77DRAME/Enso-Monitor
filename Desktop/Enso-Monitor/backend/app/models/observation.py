from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Index, Numeric, SmallInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Observation(Base):
    """
    Modèle SQLAlchemy pour une observation ONI.

    Chaque ligne représente une saison glissante de 3 mois (ex : DJF 1950)
    avec sa valeur d'anomalie ONI et les métadonnées de provenance.
    """

    __tablename__ = "observations"

    # Clé primaire auto-incrémentée
    id: Mapped[int] = mapped_column(primary_key=True)

    # Saison glissante : DJF, JFM, FMA... NDJ (3 lettres)
    season: Mapped[str] = mapped_column(String(3), nullable=False)

    # Année associée à la saison (ex : 1950)
    year: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    # Date de début du mois représentatif de la saison (ex : 1950-01-01 pour DJF)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)

    # Température absolue SST dans la région Niño 3.4 (peut être absente)
    sst_total: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)

    # Anomalie ONI par rapport à la climatologie de référence (indice principal)
    oni: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)

    # Traçabilité de la source
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    source_url: Mapped[str] = mapped_column(String(255), nullable=False)
    extraction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        # Empêche les doublons lors d'imports successifs
        UniqueConstraint("season", "year", name="uq_observation_season_year"),
        # Index pour accélérer les recherches et tris temporels
        Index("ix_observations_period_start", "period_start"),
    )

    def __repr__(self) -> str:
        return f"<Observation {self.season} {self.year} ONI={self.oni}>"
