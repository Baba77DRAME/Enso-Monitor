from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ObservationOut(BaseModel):
    """
    Schéma de sortie pour une observation ONI.
    Utilisé par l'API pour sérialiser les réponses JSON.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    season: str
    year: int
    period_start: date
    sst_total: Optional[float]
    oni: float
    source: str


class ObservationPage(BaseModel):
    """
    Réponse paginée pour la liste des observations.

    Champs :
    - total     : nombre total d'observations correspondant aux filtres
    - page      : numéro de la page courante (commence à 1)
    - page_size : nombre d'observations par page
    - results   : observations de la page courante
    """

    total: int
    page: int
    page_size: int
    results: List[ObservationOut]
