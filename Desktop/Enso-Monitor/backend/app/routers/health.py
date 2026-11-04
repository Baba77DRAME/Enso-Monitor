from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    """Vérifie que l'API est en ligne et opérationnelle."""
    return {"status": "ok", "service": "ENSO Monitor API"}
