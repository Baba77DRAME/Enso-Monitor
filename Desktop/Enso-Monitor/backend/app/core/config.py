from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "ENSO Monitor API"
    app_version: str = "0.1.0"
    app_description: str = (
        "API de visualisation des données climatiques ENSO "
        "(indice ONI - NOAA)"
    )
    debug: bool = False

    # Base de données (sera utilisée aux étapes suivantes)
    database_url: str = "postgresql://user:password@localhost:5432/enso_monitor"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Instance unique importée dans toute l'application
settings = Settings()
