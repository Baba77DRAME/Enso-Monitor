# ENSO Monitor

Application web de visualisation des données climatiques ENSO basée sur l'indice ONI officiel de la NOAA.

## Stack technique

- **Frontend** : React + TypeScript + Vite
- **Backend** : Python + FastAPI + Pydantic
- **Base de données** : PostgreSQL + SQLAlchemy + Alembic
- **ETL** : Pandas + NumPy
- **Tests** : Pytest (backend) + Vitest (frontend)

## Démarrage rapide

### Prérequis

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### ETL

```bash
cd etl
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Documentation complète : voir `Documentation.txt` à la racine.
