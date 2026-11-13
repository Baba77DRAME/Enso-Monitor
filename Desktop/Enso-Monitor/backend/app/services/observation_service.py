from datetime import date
from typing import Optional, Tuple, List

from sqlalchemy.orm import Session

from app.models.observation import Observation


def get_observations(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 50,
) -> Tuple[int, List[Observation]]:
    """
    Récupère les observations ONI depuis PostgreSQL avec filtres et pagination.

    Paramètres :
    - start_date : filtrer les observations à partir de cette date (incluse)
    - end_date   : filtrer les observations jusqu'à cette date (incluse)
    - page       : numéro de page (commence à 1)
    - page_size  : nombre de résultats par page

    Retourne :
    - total   : nombre total d'observations correspondant aux filtres
    - results : liste des observations de la page courante, triées par period_start
    """
    query = db.query(Observation)

    if start_date is not None:
        query = query.filter(Observation.period_start >= start_date)

    if end_date is not None:
        query = query.filter(Observation.period_start <= end_date)

    total = query.count()

    results = (
        query
        .order_by(Observation.period_start)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return total, results
