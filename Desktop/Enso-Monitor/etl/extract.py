import logging
import requests
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

NOAA_ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
SOURCE_NAME = "NOAA CPC - ONI v6"


def fetch_oni_raw() -> tuple[str, dict]:
    """
    Télécharge les données ONI brutes depuis la NOAA.
    Retourne le texte brut et les métadonnées de provenance.
    """
    logger.info(f"Téléchargement des données ONI depuis {NOAA_ONI_URL}")

    response = requests.get(NOAA_ONI_URL, timeout=30)
    response.raise_for_status()

    provenance = {
        "source": SOURCE_NAME,
        "source_url": NOAA_ONI_URL,
        "extraction_date": datetime.now(timezone.utc).isoformat(),
    }

    logger.info(f"Données récupérées : {len(response.text)} caractères")
    return response.text, provenance
