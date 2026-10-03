from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class EstadoEntrada:
    DISPONIBLE = "Disponible"
    RESERVADA = "Reservada"
    EMITIDA = "Emitida"
    UTILIZADA = "Utilizada"


class EstadoVenta:
    PENDIENTE = "Pendiente"
    PAGADA = "Pagada"
    CANCELADA = "Cancelada"


class Lugar(Base):
    __tablename__ = "lugares"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)

    sectores = relationship("Sector", back_populates="lugar")
    eventos = relationship("Evento", back_populates="lugar")


class Sector(Base):
    __tablename__ = "sectores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    capacidad = Column(Integer, nullable=False)
    lugar_id = Column(Integer, ForeignKey("lugares.id"), nullable=False)

    lugar = relationship("Lugar", back_populates="sectores")


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    lugar_id = Column(Integer, ForeignKey("lugares.id"), nullable=False)

    lugar = relationship("Lugar", back_populates="eventos")
    precios = relationship("PrecioSectorEvento", back_populates="evento")


class PrecioSectorEvento(Base):
    """Precio de un sector para un evento puntual."""

    __tablename__ = "precios_sector_evento"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectores.id"), nullable=False)
    precio = Column(Float, nullable=False)

    evento = relationship("Evento", back_populates="precios")

    # GRASP Experto en Información: quien tiene el precio calcula el subtotal.
    def calcular_subtotal(self, cantidad: int) -> float:
        return self.precio * cantidad


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)

    ventas = relationship("Venta", back_populates="cliente")


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    estado = Column(String, default=EstadoVenta.PENDIENTE, nullable=False)
    total = Column(Float, default=0.0, nullable=False)
    fecha = Column(DateTime, default=datetime.now)

    cliente = relationship("Cliente", back_populates="ventas")
    entradas = relationship("Entrada", back_populates="venta")


class Entrada(Base):
    __tablename__ = "entradas"

    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectores.id"), nullable=False)
    venta_id = Column(Integer, ForeignKey("ventas.id"), nullable=True)
    estado = Column(String, default=EstadoEntrada.DISPONIBLE, nullable=False)
    codigo_qr = Column(String, unique=True, index=True, nullable=False)
    hora_ingreso = Column(DateTime, nullable=True)

    venta = relationship("Venta", back_populates="entradas")

    # Comportamiento propio de la entrada (Experto en Información)
    @property
    def esta_disponible(self) -> bool:
        return self.estado == EstadoEntrada.DISPONIBLE

    def emitir(self) -> None:
        self.estado = EstadoEntrada.EMITIDA

    def registrar_ingreso(self) -> datetime:
        self.hora_ingreso = datetime.now()
        self.estado = EstadoEntrada.UTILIZADA
        return self.hora_ingreso
