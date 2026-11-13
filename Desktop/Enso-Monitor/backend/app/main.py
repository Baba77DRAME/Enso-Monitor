from fastapi import FastAPI

from app.core.config import settings
from app.routers import health
from app.routers import observations

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
)

# Routes système
app.include_router(health.router)

# Routes métier sous /api/v1
app.include_router(observations.router, prefix="/api/v1")


@app.get("/", tags=["root"])
def root():
    """Point d'entrée de l'API. Retourne le nom, la version et le lien vers la doc."""
    return {
        "message": f"{settings.app_name} is running",
        "version": settings.app_version,
        "docs": "/docs",
    }
