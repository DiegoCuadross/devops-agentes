from fastapi import FastAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api")

app = FastAPI(title="DevOps Agentes API")


@app.get("/")
def raiz():
    logger.info("Petición recibida en /")
    return {"mensaje": "Hola desde mi primer contenedor"}


@app.get("/health")
def health():
    return {"estado": "ok"}