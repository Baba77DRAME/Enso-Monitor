from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Importation de la config applicative et des modèles
# Les modèles doivent être importés pour qu'Alembic les détecte via autogenerate
from app.core.config import settings
from app.core.database import Base
import app.models  # noqa: F401 — enregistre les modèles dans Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic détecte automatiquement les changements de schéma grâce à target_metadata
target_metadata = Base.metadata

# Injection de l'URL de BDD depuis Pydantic Settings (lit le .env)
config.set_main_option("sqlalchemy.url", settings.database_url)


def run_migrations_offline() -> None:
    """Migration sans connexion active (génère du SQL brut)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Migration avec connexion active à PostgreSQL."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
