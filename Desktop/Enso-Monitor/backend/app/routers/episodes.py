from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.episode import EpisodeDetail, EpisodeSummary
from app.services.episode_service import get_all_episodes, get_episode_detail

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.get("/", response_model=List[EpisodeSummary])
def list_episodes(db: Session = Depends(get_db)):
    """
    Retourne tous les épisodes ENSO identifiés selon le critère NOAA
    (≥5 saisons consécutives avec ONI ≥ +0.5°C ou ≤ -0.5°C).
    """
    return get_all_episodes(db)


@router.get("/{episode_id}", response_model=EpisodeDetail)
def get_episode(episode_id: int, db: Session = Depends(get_db)):
    """
    Retourne un épisode avec sa série ONI complète.
    Utilisé pour la comparaison de deux épisodes dans le frontend.
    """
    episode = get_episode_detail(db, episode_id)
    if episode is None:
        raise HTTPException(
            status_code=404,
            detail=f"Épisode {episode_id} introuvable.",
        )
    return episode
