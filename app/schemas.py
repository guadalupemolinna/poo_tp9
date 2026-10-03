from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


# ---- HU1: cotizar ----
class CotizacionRequest(BaseModel):
    evento_id: int
    sector_id: int
    # Sin gt=0 a propósito: la validación la hace el servicio (400 con mensaje propio).
    cantidad: int = Field(..., examples=[2])


class CotizacionResponse(BaseModel):
    subtotal: float


# ---- HU2: iniciar pago ----
class DatosTarjeta(BaseModel):
    numero: str = Field(..., examples=["1234567890123456"])


class IniciarPagoRequest(BaseModel):
    cliente_id: int
    entradas_ids: List[int]
    datos_tarjeta: DatosTarjeta


class IniciarPagoResponse(BaseModel):
    venta_id: int
    estado: str
    total: float


# ---- HU3: escanear acceso ----
class EscaneoRequest(BaseModel):
    codigo_qr: str


class EscaneoResponse(BaseModel):
    mensaje: str
    hora_ingreso: datetime

