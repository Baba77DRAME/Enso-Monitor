"""
Service d'identification des épisodes ENSO.

MÉTHODE :
  Critère NOAA officiel — un épisode est reconnu quand l'indice ONI
  dépasse le seuil ±0.5°C pendant au moins 5 saisons glissantes
  de 3 mois consécutives.

LIMITES CONNUES :
  - L'algorithme est strict : une saison neutre entre deux séquences
    crée deux épisodes distincts, même si NOAA les regroupe parfois.
  - Le seuil de 5 saisons est appliqué sans tolérance d'interruption.
  - Les données NOAA sont révisées périodiquement : les identifiants
    d'épisodes peuvent changer lors d'une mise à jour des observations.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.observation import Observation
from app.schemas.episode import EpisodeDetail, EpisodeSummary
from app.schemas.observation import ObservationOut

# Seuil NOAA (°C)
THRESHOLD = 0.5
# Durée minimale NOAA (saisons)
MIN_DURATION = 5


def _build_episodes(observations: List[Observation]) -> List[dict]:
    """
    Identifie les épisodes El Niño et La Niña depuis une liste
    d'observations triées par period_start.

    Retourne une liste de dicts contenant les métadonnées et les
    observations brutes de chaque épisode.
    """
    episodes: List[dict] = []
    n = len(observations)
    i = 0
    ep_id = 1

    while i < n:
        obs = observations[i]
        oni = float(obs.oni)

        if oni >= THRESHOLD:
            phase = "el_nino"
        elif oni <= -THRESHOLD:
            phase = "la_nina"
        else:
            i += 1
            continue

        # Avance tant que la condition est vérifiée
        j = i
        while j < n:
            v = float(observations[j].oni)
            if phase == "el_nino" and v >= THRESHOLD:
                j += 1
            elif phase == "la_nina" and v <= -THRESHOLD:
                j += 1
            else:
                break

        episode_obs = observations[i:j]

        if len(episode_obs) >= MIN_DURATION:
            if phase == "el_nino":
                peak = max(episode_obs, key=lambda x: float(x.oni))
            else:
                peak = min(episode_obs, key=lambda x: float(x.oni))

            episodes.append(
                {
                    "id": ep_id,
                    "type": phase,
                    "start_season": episode_obs[0].season,
                    "start_year": int(episode_obs[0].year),
                    "end_season": episode_obs[-1].season,
                    "end_year": int(episode_obs[-1].year),
                    "duration": len(episode_obs),
                    "peak_oni": float(peak.oni),
                    "peak_season": peak.season,
                    "peak_year": int(peak.year),
                    "observations": episode_obs,
                }
            )
            ep_id += 1

        i = j

    return episodes


def get_all_episodes(db: Session) -> List[EpisodeSummary]:
    """Retourne la liste de tous les épisodes identifiés (sans observations)."""
    observations = (
        db.query(Observation).order_by(Observation.period_start).all()
    )
    raw = _build_episodes(observations)
    return [
        EpisodeSummary(**{k: v for k, v in ep.items() if k != "observations"})
        for ep in raw
    ]


def get_episode_detail(db: Session, episode_id: int) -> Optional[EpisodeDetail]:
    """Retourne un épisode avec sa série ONI complète, ou None si introuvable."""
    observations = (
        db.query(Observation).order_by(Observation.period_start).all()
    )
    raw = _build_episodes(observations)

    for ep in raw:
        if ep["id"] == episode_id:
            obs_out = [ObservationOut.model_validate(o) for o in ep["observations"]]
            return EpisodeDetail(
                **{k: v for k, v in ep.items() if k != "observations"},
                observations=obs_out,
            )

    return None
