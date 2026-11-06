from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import (Cliente, Entrada, EstadoEntrada, PrecioSectorEvento,
                        Venta, Lugar, Sector, Evento)


class LugarRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, lugar: Lugar) -> Lugar:
        self.db.add(lugar)
        self.db.commit()
        self.db.refresh(lugar)
        return lugar

    def listar(self) -> List[Lugar]:
        return self.db.query(Lugar).all()

    def obtener(self, lugar_id: int) -> Optional[Lugar]:
        return self.db.get(Lugar, lugar_id)


class SectorRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, sector: Sector) -> Sector:
        self.db.add(sector)
        self.db.commit()
        self.db.refresh(sector)
        return sector

    def listar(self) -> List[Sector]:
        return self.db.query(Sector).all()

    def obtener(self, sector_id: int) -> Optional[Sector]:
        return self.db.get(Sector, sector_id)


class EventoRepository:
    def __init__(self, db: Session):
        self.db = db

    def crear(self, evento: Evento) -> Evento:
        self.db.add(evento)
        self.db.commit()
        self.db.refresh(evento)
        return evento

    def listar(self) -> List[Evento]:
        return self.db.query(Evento).all()

    def obtener(self, evento_id: int) -> Optional[Evento]:
        return self.db.get(Evento, evento_id)


class PrecioRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener(self, evento_id: int, sector_id: int) -> Optional[PrecioSectorEvento]:
        return (
            self.db.query(PrecioSectorEvento)
            .filter_by(evento_id=evento_id, sector_id=sector_id)
            .first()
        )

    def crear(self, precio: PrecioSectorEvento) -> PrecioSectorEvento:
        self.db.add(precio)
        self.db.commit()
        self.db.refresh(precio)
        return precio

    def listar(self) -> List[PrecioSectorEvento]:
        return self.db.query(PrecioSectorEvento).all()

    def obtener_por_id(self, precio_id: int) -> Optional[PrecioSectorEvento]:
        return self.db.get(PrecioSectorEvento, precio_id)


class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener(self, cliente_id: int) -> Optional[Cliente]:
        return self.db.get(Cliente, cliente_id)

    def crear(self, cliente: Cliente) -> Cliente:
        self.db.add(cliente)
        self.db.commit()
        self.db.refresh(cliente)
        return cliente

    def listar(self) -> List[Cliente]:
        return self.db.query(Cliente).all()


class VentaRepository:
    def __init__(self, db: Session):
        self.db = db

    def guardar(self, venta: Venta) -> Venta:
        self.db.add(venta)
        self.db.flush()
        return venta

    def obtener(self, venta_id: int) -> Optional[Venta]:
        return self.db.get(Venta, venta_id)

    def commit(self) -> None:
        self.db.commit()


class EntradaRepository:
    def __init__(self, db: Session):
        self.db = db

    def contar_disponibles(self, evento_id: int, sector_id: int) -> int:
        return (
            self.db.query(Entrada)
            .filter_by(evento_id=evento_id, sector_id=sector_id,
                       estado=EstadoEntrada.DISPONIBLE)
            .count()
        )

    def listar_por_ids(self, ids: List[int]) -> List[Entrada]:
        return self.db.query(Entrada).filter(Entrada.id.in_(ids)).all()

    def buscar_por_qr(self, codigo_qr: str) -> Optional[Entrada]:
        return self.db.query(Entrada).filter_by(codigo_qr=codigo_qr).first()

    def reservar(self, ids: List[int]) -> bool:
        """Pasa Disponible -> Reservada de forma atómica."""
        res = self.db.execute(
            update(Entrada)
            .where(Entrada.id.in_(ids), Entrada.estado == EstadoEntrada.DISPONIBLE)
            .values(estado=EstadoEntrada.RESERVADA)
        )
        if res.rowcount != len(ids):
            self.db.rollback()
            return False
        self.db.commit()
        self.db.expire_all()
        return True

    def liberar(self, ids: List[int]) -> None:
        """Reservada -> Disponible (pago rechazado)."""
        self.db.execute(
            update(Entrada)
            .where(Entrada.id.in_(ids), Entrada.estado == EstadoEntrada.RESERVADA)
            .values(estado=EstadoEntrada.DISPONIBLE)
        )
        self.db.commit()
        self.db.expire_all()

    def commit(self) -> None:
        self.db.commit()