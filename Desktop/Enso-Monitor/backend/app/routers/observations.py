from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.observation import ObservationPage
from app.services.observation_service import get_observations

router = APIRouter(prefix="/observations", tags=["observations"])


@router.get(
    "",
    response_model=ObservationPage,
    summary="Lister les observations ONI",
    description=(
        "Retourne la liste paginée des observations ONI issues de la NOAA. "
        "Les filtres start_date et end_date s'appliquent sur le champ period_start "
        "(date du 1er jour du mois représentatif de la saison)."
    ),
)
def list_observations(
    start_date: Optional[date] = Query(
        default=None,
        description="Date de début (incluse), format YYYY-MM-DD. Ex : 2000-01-01",
    ),
    end_date: Optional[date] = Query(
        default=None,
        description="Date de fin (incluse), format YYYY-MM-DD. Ex : 2010-12-01",
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="Numéro de page (commence à 1)",
    ),
    page_size: int = Query(
        default=50,
        ge=1,
        le=200,
        description="Nombre de résultats par page (max 200)",
    ),
    db: Session = Depends(get_db),
) -> ObservationPage:
    # Validation croisée : start_date ne peut pas dépasser end_date
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date ne peut pas être postérieure à end_date.",
        )

    total, results = get_observations(
        db=db,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    return ObservationPage(
        total=total,
        page=page,
        page_size=page_size,
        results=results,
    )
