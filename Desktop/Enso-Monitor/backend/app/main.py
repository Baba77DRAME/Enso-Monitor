from fastapi import FastAPI

app = FastAPI(
    title="ENSO Monitor API",
    description="API de visualisation des données climatiques ENSO (indice ONI - NOAA)",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "ENSO Monitor API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}
