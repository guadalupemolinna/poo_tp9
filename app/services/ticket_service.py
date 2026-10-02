from uuid import uuid4

from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Entrada, PrecioSectorEvento, Venta
from .pasarela_pago import PasarelaPago


class EntradasNoDisponiblesError(Exception):
    pass


class PagoDenegadoError(Exception):
    pass

class TicketInvalidoError(Exception):
    pass


class EntradaYaUtilizadaError(Exception):
    pass


class TicketNoEmitidoError(Exception):
    pass


class TicketService:

    def __init__(self, db: Session, pasarela: PasarelaPago):
        self.db = db
        self.pasarela = pasarela

    def cotizar(
        self,
        evento_id: int,
        sector_id: int,
        cantidad: int
    ) -> float:

        if cantidad <= 0:
            raise ValueError(
                "La cantidad de entradas solicitadas debe ser mayor a cero"
            )

        precio_sector = (
            self.db.query(PrecioSectorEvento)
            .filter(
                PrecioSectorEvento.evento_id == evento_id,
                PrecioSectorEvento.sector_id == sector_id
            )
            .first()
        )

        if precio_sector is None:
            raise ValueError(
                "Capacidad insuficiente o entradas no disponibles"
            )

        entradas_disponibles = (
            self.db.query(Entrada)
            .filter(
                Entrada.evento_id == evento_id,
                Entrada.sector_id == sector_id,
                Entrada.estado == "Disponible"
            )
            .count()
        )

        if cantidad > entradas_disponibles:
            raise ValueError(
                "Capacidad insuficiente o entradas no disponibles"
            )

        return precio_sector.precio * cantidad

    def procesar_pago(
        self,
        cliente_id: int,
        entradas_ids: list[int],
        datos_tarjeta: dict
    ) -> Venta:

        if not entradas_ids:
            raise ValueError("Debe seleccionar al menos una entrada")

        # Revalidación de disponibilidad JUSTO antes del pago
        entradas = (
            self.db.query(Entrada)
            .filter(Entrada.id.in_(entradas_ids))
            .all()
        )

        if len(entradas) != len(set(entradas_ids)):
            raise EntradasNoDisponiblesError(
                "Los lugares seleccionados ya no se encuentran disponibles"
            )

        if any(entrada.estado != "Disponible" for entrada in entradas):
            raise EntradasNoDisponiblesError(
                "Los lugares seleccionados ya no se encuentran disponibles"
            )

        # Calcular el total de las entradas seleccionadas
        total = 0.0

        for entrada in entradas:
            precio = (
                self.db.query(PrecioSectorEvento)
                .filter(
                    PrecioSectorEvento.evento_id == entrada.evento_id,
                    PrecioSectorEvento.sector_id == entrada.sector_id
                )
                .first()
            )

            if precio is None:
                raise ValueError(
                    "No se encontró el precio de una de las entradas"
                )

            total += precio.precio

        # IMPORTANTE:
        # La pasarela se invoca solamente después
        # de haber revalidado el stock.
        resultado = self.pasarela.cobrar(
            total,
            datos_tarjeta
        )

        if resultado == "Rechazado":
            self.db.rollback()

            raise PagoDenegadoError("Pago denegado")

        # Pago aprobado: crear la venta
        venta = Venta(
            cliente_id=cliente_id,
            estado="Pagada",
            total=total
        )

        self.db.add(venta)

        # Emitir las entradas
        for entrada in entradas:
            entrada.estado = "Emitida"
            entrada.codigo_qr = str(uuid4())

        self.db.commit()
        self.db.refresh(venta)

        return venta

    def escanear_acceso(self, codigo_qr: str) -> datetime:

        entrada = (
            self.db.query(Entrada)
            .filter(Entrada.codigo_qr == codigo_qr)
            .first()
        )

        # QR inexistente
        if entrada is None:
            raise TicketInvalidoError(
                "Ticket Inválido o Inexistente"
            )

        # Entrada ya utilizada
        if entrada.estado == "Utilizada":
            raise EntradaYaUtilizadaError(
                "Entrada ya utilizada"
            )

        # Entrada todavía no emitida
        if entrada.estado in ("Disponible", "Reservada"):
            raise TicketNoEmitidoError(
                "Ticket no emitido / Falta de pago"
            )

        # Camino feliz: entrada Emitida
        if entrada.estado == "Emitida":
            hora_ingreso = datetime.now()

            entrada.estado = "Utilizada"
            entrada.hora_ingreso = hora_ingreso

            self.db.commit()

            return hora_ingreso

        # Por seguridad, cualquier estado no contemplado
        raise TicketNoEmitidoError(
            "Ticket no emitido / Falta de pago"
        )