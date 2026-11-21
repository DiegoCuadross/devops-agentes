import logging
import time

from fastapi import Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST 
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from analizador import analizar_oferta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="Analizador de ofertas de empleo")

ANALISIS = Counter(
    "analisis_total",
    "Análisis de ofertas realizados",
    ["resultado"],
)

DURACION = Histogram(
    "analisis_duracion_segundos",
    "Tiempo que tarda un análisis completo",
    buckets=(1, 2, 5, 10, 20, 30, 60, 120),
)
class Solicitud(BaseModel):
    oferta: str = Field(min_length=50, max_length=8000)
    perfil: str = Field(min_length=20, max_length=3000)


@app.get("/health")
def health():
    return {"estado": "ok"}
@app.get("/metrics")
def metricas():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/analizar")
def analizar(solicitud: Solicitud):
    logger.info("Analizando oferta de %d caracteres", len(solicitud.oferta))
    inicio = time.perf_counter()
    try:
        informe = analizar_oferta(solicitud.oferta, solicitud.perfil)
    except Exception:
        ANALISIS.labels(resultado="error").inc()
        logger.exception("Falló el análisis")
        raise HTTPException(
            status_code=503,
            detail="El modelo no está disponible, intenta de nuevo en unos minutos",
        )
    finally:
        DURACION.observe(time.perf_counter() - inicio)
    ANALISIS.labels(resultado="exito").inc()
    logger.info("Análisis completado")
    return {"informe": informe}