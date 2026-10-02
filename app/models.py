from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class Lugar(Base):
    __tablename__ = "lugares"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String, nullable=False)

    sectores = relationship(
        "Sector",
        back_populates="lugar",
        cascade="all, delete-orphan"
    )

    eventos = relationship(
        "Evento",
        back_populates="lugar"
    )


class Sector(Base):
    __tablename__ = "sectores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    capacidad = Column(Integer, nullable=False)

    lugar_id = Column(Integer, ForeignKey("lugares.id"), nullable=False)

    lugar = relationship(
        "Lugar",
        back_populates="sectores"
    )

    precios_eventos = relationship(
        "PrecioSectorEvento",
        back_populates="sector"
    )

    entradas = relationship(
        "Entrada",
        back_populates="sector"
    )


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    lugar_id = Column(Integer, ForeignKey("lugares.id"), nullable=False)

    lugar = relationship(
        "Lugar",
        back_populates="eventos"
    )

    precios_sectores = relationship(
        "PrecioSectorEvento",
        back_populates="evento"
    )

    entradas = relationship(
        "Entrada",
        back_populates="evento"
    )


class PrecioSectorEvento(Base):
    __tablename__ = "precios_sector_evento"

    id = Column(Integer, primary_key=True, index=True)

    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectores.id"), nullable=False)

    precio = Column(Float, nullable=False)

    evento = relationship(
        "Evento",
        back_populates="precios_sectores"
    )

    sector = relationship(
        "Sector",
        back_populates="precios_eventos"
    )


class Entrada(Base):
    __tablename__ = "entradas"

    id = Column(Integer, primary_key=True, index=True)

    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    sector_id = Column(Integer, ForeignKey("sectores.id"), nullable=False)

    estado = Column(
        Enum(
            "Disponible",
            "Reservada",
            "Emitida",
            "Utilizada",
            name="estado_entrada"
        ),
        nullable=False,
        default="Disponible"
    )

    codigo_qr = Column(String, unique=True, nullable=False)
    hora_ingreso = Column(DateTime, nullable=True)

    evento = relationship(
        "Evento",
        back_populates="entradas"
    )

    sector = relationship(
        "Sector",
        back_populates="entradas"
    )


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)

    ventas = relationship(
        "Venta",
        back_populates="cliente"
    )


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    estado = Column(
        Enum(
            "Pendiente",
            "Pagada",
            "Cancelada",
            name="estado_venta"
        ),
        nullable=False,
        default="Pendiente"
    )

    total = Column(Float, nullable=False, default=0)

    cliente = relationship(
        "Cliente",
        back_populates="ventas"
    )