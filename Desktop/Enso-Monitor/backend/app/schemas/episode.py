from typing import List
from pydantic import BaseModel
from .observation import ObservationOut


class EpisodeSummary(BaseModel):
    """
    Résumé d'un épisode ENSO identifié selon les critères NOAA.
    Critère : ONI >= +0.5°C (El Niño) ou <= -0.5°C (La Niña)
    pendant au moins 5 saisons glissantes consécutives.
    """

    id: int
    type: str           # 'el_nino' | 'la_nina'
    start_season: str
    start_year: int
    end_season: str
    end_year: int
    duration: int       # nombre de saisons
    peak_oni: float
    peak_season: str
    peak_year: int


class EpisodeDetail(EpisodeSummary):
    """Épisode avec la série ONI complète."""
    observations: List[ObservationOut]
