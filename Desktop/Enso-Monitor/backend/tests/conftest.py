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


def _make_episode_observations():
    """
    Crée des observations formant 2 épisodes identifiables :
      - El Niño : 6 saisons (1997), pic à 2.3°C
      - La Niña : 5 saisons (1999), pic à -1.2°C
    Ces données sont fictives — identifiées comme fixtures de test.
    """
    nino = [
        ("DJF", 1, 1997, 1.2),
        ("JFM", 2, 1997, 1.6),
        ("FMA", 3, 1997, 1.9),
        ("MAM", 4, 1997, 2.3),
        ("AMJ", 5, 1997, 2.1),
        ("MJJ", 6, 1997, 1.8),
    ]
    neutral = [("ASO", 9, 1998, 0.1)]
    nina = [
        ("DJF", 1, 1999, -0.8),
        ("JFM", 2, 1999, -1.0),
        ("FMA", 3, 1999, -1.2),
        ("MAM", 4, 1999, -1.1),
        ("AMJ", 5, 1999, -0.9),
    ]
    result = []
    for rows in (nino, neutral, nina):
        for season, month, year, oni in rows:
            result.append(
                Observation(
                    season=season, year=year,
                    period_start=date(year, month, 1),
                    oni=oni, sst_total=27.0,
                    source="TEST", source_url="http://test",
                    extraction_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                )
            )
    return result


@pytest.fixture
def client():
    """Client HTTP sans base de données (tests routes /, /health)."""
    return TestClient(app)


@pytest.fixture
def empty_db_client():
    """Client HTTP avec SQLite vide — aucune observation en base."""
    empty_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=empty_engine)
    EmptySession = sessionmaker(autocommit=False, autoflush=False, bind=empty_engine)

    def override():
        s = EmptySession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=empty_engine)
    app.dependency_overrides.clear()


@pytest.fixture
def episode_client():
    """
    Client HTTP avec SQLite peuplé d'observations formant 2 épisodes.
    Utilisé pour tester /api/v1/episodes/.
    """
    ep_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=ep_engine)
    EpSession = sessionmaker(autocommit=False, autoflush=False, bind=ep_engine)

    db = EpSession()
    db.add_all(_make_episode_observations())
    db.commit()
    db.close()

    def override():
        s = EpSession()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c

    Base.metadata.drop_all(bind=ep_engine)
    app.dependency_overrides.clear()


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
