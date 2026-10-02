from fastapi import FastAPI

from .database import Base, engine
from . import models
from .routers import pagos

Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="API de Eventos",
    version="1.0.0"
)
app.include_router(pagos.router)

@app.get("/")
def inicio():
    return {"mensaje": "API funcionando"}