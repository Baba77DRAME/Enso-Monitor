from datetime import date, datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.models.observation import Observation

# ---------------------------------------------------------------------------
# Base de données SQLite en mémoire (tests uniquement, sans PostgreSQL)
# StaticPool : toutes les connexions partagent la même base en mémoire
# ---------------------------------------------------------------------------
TEST_DB_URL = "sqlite://"

engine_test = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionTest = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    """Remplace get_db par une session SQLite pour les tests."""
    db = SessionTest()
    try:
        yield db
    finally:
        db.close()


def _make_test_observations():
    """
    Crée de nouvelles instances d'Observation pour chaque appel.
    Les données sont fictives — jamais présentées comme des valeurs NOAA.
    """
    return [
        Observation(
            season="DJF", year=2000, period_start=date(2000, 1, 1),
            sst_total=27.5, oni=0.5,
            source="TEST", source_url="http://test",
            extraction_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ),
        Observation(
            season="JJA", year=2000, period_start=date(2000, 7, 1),
            sst_total=28.0, oni=1.2,
            source="TEST", source_url="http://test",
            extraction_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ),
        Observation(
            season="DJF", year=2005, period_start=date(2005, 1, 1),
            sst_total=26.5, oni=-0.8,
            source="TEST", source_url="http://test",
            extraction_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ),
        Observation(
            season="DJF", year=2010, period_start=date(2010, 1, 1),
            sst_total=None, oni=-1.5,
            source="TEST", source_url="http://test",
            extraction_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
        ),
    ]


@pytest.fixture
def client():
    """Client HTTP sans base de données (tests routes /, /health)."""
    return TestClient(app)


@pytest.fixture
def db_client():
    """
    Client HTTP avec base SQLite en mémoire.
    Utilisé pour tester les routes /api/v1/observations.
    Crée des instances fraîches à chaque appel pour éviter les conflits de session.
    """
    Base.metadata.create_all(bind=engine_test)
    app.dependency_overrides[get_db] = override_get_db

    db = SessionTest()
    db.add_all(_make_test_observations())
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c

    # Nettoyage après chaque test
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.clear()
