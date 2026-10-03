from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (registra las tablas)
from app.database import Base, engine
from app.routers import pagos
from app.services.excepciones import DominioError

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartTicket API",
    description="Gestión de entradas, pagos y control de acceso a eventos.",
    version="1.0.0",
)


@app.exception_handler(DominioError)
async def manejar_error_dominio(request: Request, exc: DominioError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.mensaje})


app.include_router(pagos.router)


@app.get("/", tags=["Root"])
def root():
    return {"mensaje": "SmartTicket API funcionando. Documentación en /docs"}
