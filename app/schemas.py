from datetime import datetime

from pydantic import BaseModel


class CotizacionRequest(BaseModel):
    evento_id: int
    sector_id: int
    cantidad: int


class CotizacionResponse(BaseModel):
    subtotal: float


class PagoRequest(BaseModel):
    cliente_id: int
    entradas_ids: list[int]
    datos_tarjeta: dict


class PagoResponse(BaseModel):
    venta_id: int
    estado: str
    total: float


class EscanearAccesoRequest(BaseModel):
    codigo_qr: str


class EscanearAccesoResponse(BaseModel):
    mensaje: str
    hora_ingreso: datetime