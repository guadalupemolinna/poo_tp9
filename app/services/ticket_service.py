from datetime import datetime
from typing import List

from app.models import EstadoEntrada, EstadoVenta, Venta
from app.repositories import (ClienteRepository, EntradaRepository,
                              PrecioRepository, VentaRepository)
from app.services.excepciones import (CantidadInvalida, CapacidadInsuficiente,
                                      ClienteNoEncontrado, EntradasNoDisponibles,
                                      EntradaYaUtilizada, PagoDenegado,
                                      PrecioNoDefinido, TicketInvalido,
                                      TicketNoEmitido)
from app.services.pasarela_pago import PasarelaPago


class TicketService:
    """Lógica de negocio. Recibe sus dependencias por constructor (DIP)."""

    def __init__(
        self,
        entradas: EntradaRepository,
        precios: PrecioRepository,
        clientes: ClienteRepository,
        ventas: VentaRepository,
        pasarela: PasarelaPago,
    ):
        self.entradas = entradas
        self.precios = precios
        self.clientes = clientes
        self.ventas = ventas
        self.pasarela = pasarela

    # ---------------- HU1 ----------------
    def cotizar(self, evento_id: int, sector_id: int, cantidad: int) -> float:
        if cantidad <= 0:
            raise CantidadInvalida(
                "La cantidad de entradas solicitadas debe ser mayor a cero"
            )

        precio = self.precios.obtener(evento_id, sector_id)
        if precio is None:
            raise PrecioNoDefinido("No hay precio definido para ese evento y sector")

        if self.entradas.contar_disponibles(evento_id, sector_id) < cantidad:
            raise CapacidadInsuficiente("Capacidad insuficiente o entradas no disponibles")

        return precio.calcular_subtotal(cantidad)

    # ---------------- HU2 ----------------
    def iniciar_pago(self, cliente_id: int, entradas_ids: List[int], numero_tarjeta: str) -> Venta:
        if not entradas_ids:
            raise CantidadInvalida("Debe seleccionar al menos una entrada")
        ids = list(dict.fromkeys(entradas_ids))  # sin duplicados, mantiene orden

        if self.clientes.obtener(cliente_id) is None:
            raise ClienteNoEncontrado("Cliente no encontrado")

        entradas = self.entradas.listar_por_ids(ids)
        if len(entradas) != len(ids) or not all(e.esta_disponible for e in entradas):
            raise EntradasNoDisponibles(
                "Los lugares seleccionados ya no se encuentran disponibles"
            )

        total = 0.0
        for e in entradas:
            precio = self.precios.obtener(e.evento_id, e.sector_id)
            if precio is None:
                raise PrecioNoDefinido("No hay precio definido para una de las entradas")
            total += precio.precio

        # Reserva atómica ANTES de consultar la pasarela (concurrencia).
        if not self.entradas.reservar(ids):
            raise EntradasNoDisponibles(
                "Los lugares seleccionados ya no se encuentran disponibles"
            )

        try:
            aprobado = self.pasarela.procesar_pago(total, numero_tarjeta)
        except Exception:
            self.entradas.liberar(ids)
            raise

        if not aprobado:
            self.entradas.liberar(ids)
            raise PagoDenegado("Pago denegado")

        venta = self.ventas.guardar(
            Venta(cliente_id=cliente_id, estado=EstadoVenta.PAGADA, total=total)
        )
        for e in self.entradas.listar_por_ids(ids):
            e.venta_id = venta.id
            e.emitir()
        self.ventas.commit()
        return venta

    # ---------------- HU3 ----------------
    def escanear_acceso(self, codigo_qr: str) -> datetime:
        entrada = self.entradas.buscar_por_qr(codigo_qr)
        if entrada is None:
            raise TicketInvalido("Ticket Inválido o Inexistente")

        if entrada.estado == EstadoEntrada.UTILIZADA:
            raise EntradaYaUtilizada("Entrada ya utilizada")

        if entrada.estado != EstadoEntrada.EMITIDA:
            raise TicketNoEmitido("Ticket no emitido / Falta de pago")

        hora = entrada.registrar_ingreso()
        self.entradas.commit()
        return hora
