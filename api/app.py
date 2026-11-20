import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from analizador import analizar_oferta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Analizador de ofertas de empleo")


class Solicitud(BaseModel):
    oferta: str = Field(min_length=50, max_length=8000)
    perfil: str = Field(min_length=20, max_length=3000)


@app.get("/health")
def health():
    return {"estado": "ok"}


@app.post("/analizar")
def analizar(solicitud: Solicitud):
    logger.info("Analizando oferta de %d caracteres", len(solicitud.oferta))
    try:
        informe = analizar_oferta(solicitud.oferta, solicitud.perfil)
    except Exception:
        logger.exception("Falló el análisis")
        raise HTTPException(
            status_code=503,
            detail="El modelo no está disponible, intenta de nuevo en unos minutos",
        )
    logger.info("Análisis completado")
    return {"informe": informe}