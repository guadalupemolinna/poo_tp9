from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


# ---- HU1: cotizar ----
class CotizacionRequest(BaseModel):
    evento_id: int
    sector_id: int
    # Sin gt=0 a propósito: la validación la hace el servicio.
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


# ---- CRUD BÁSICO ----
class LugarCreate(BaseModel):
    nombre: str
    direccion: str

class LugarRead(BaseModel):
    id: int
    nombre: str
    direccion: str
    class Config:
        from_attributes = True

class SectorCreate(BaseModel):
    nombre: str
    capacidad: int
    lugar_id: int

class SectorRead(BaseModel):
    id: int
    nombre: str
    capacidad: int
    lugar_id: int
    class Config:
        from_attributes = True

class EventoCreate(BaseModel):
    nombre: str
    lugar_id: int

class EventoRead(BaseModel):
    id: int
    nombre: str
    lugar_id: int
    class Config:
        from_attributes = True

class ClienteCreate(BaseModel):
    nombre: str
    email: str

class ClienteRead(BaseModel):
    id: int
    nombre: str
    email: str
    class Config:
        from_attributes = True

class PrecioSectorEventoCreate(BaseModel):
    evento_id: int
    sector_id: int
    precio: float

class PrecioSectorEventoRead(BaseModel):
    id: int
    evento_id: int
    sector_id: int
    precio: float
    class Config:
        from_attributes = True