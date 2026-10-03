from typing import List, Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import (Cliente, Entrada, EstadoEntrada, PrecioSectorEvento,
                        Venta)


class PrecioRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener(self, evento_id: int, sector_id: int) -> Optional[PrecioSectorEvento]:
        return (
            self.db.query(PrecioSectorEvento)
            .filter_by(evento_id=evento_id, sector_id=sector_id)
            .first()
        )


class ClienteRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener(self, cliente_id: int) -> Optional[Cliente]:
        return self.db.get(Cliente, cliente_id)


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
        """Pasa Disponible -> Reservada de forma atómica (evita doble venta).

        El UPDATE condicional solo afecta filas todavía Disponibles; si alguna
        ya fue tomada por otro usuario, se deshace todo y devuelve False.
        """
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
        """Reservada -> Disponible (pago rechazado o error)."""
        self.db.execute(
            update(Entrada)
            .where(Entrada.id.in_(ids), Entrada.estado == EstadoEntrada.RESERVADA)
            .values(estado=EstadoEntrada.DISPONIBLE)
        )
        self.db.commit()
        self.db.expire_all()

    def commit(self) -> None:
        self.db.commit()
