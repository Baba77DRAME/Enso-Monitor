from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Moteur SQLAlchemy : gère la connexion physique à PostgreSQL
engine = create_engine(settings.database_url)

# Factory de sessions : chaque session = une transaction indépendante
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe de base dont héritent tous les modèles SQLAlchemy."""
    pass


def get_db():
    """
    Générateur de session pour l'injection de dépendances FastAPI.
    Garantit la fermeture de la session même en cas d'erreur.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
