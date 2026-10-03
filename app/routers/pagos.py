from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import (ClienteRepository, EntradaRepository,
                              PrecioRepository, VentaRepository)
from app.schemas import (CotizacionRequest, CotizacionResponse, EscaneoRequest,
                         EscaneoResponse, IniciarPagoRequest,
                         IniciarPagoResponse)
from app.services.pasarela_pago import PasarelaPago, PasarelaPagoSimulada
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/pagos", tags=["Pagos y accesos"])


def get_pasarela() -> PasarelaPago:
    return PasarelaPagoSimulada()


def get_ticket_service(
    db: Session = Depends(get_db),
    pasarela: PasarelaPago = Depends(get_pasarela),
) -> TicketService:
    return TicketService(
        entradas=EntradaRepository(db),
        precios=PrecioRepository(db),
        clientes=ClienteRepository(db),
        ventas=VentaRepository(db),
        pasarela=pasarela,
    )


# Los controladores solo reciben la petición, delegan y devuelven la respuesta.
# Los errores de negocio se traducen a HTTP en el handler global de main.py.

@router.post("/cotizar", response_model=CotizacionResponse,
             summary="HU1 - Cotizar entradas")
def cotizar(datos: CotizacionRequest, service: TicketService = Depends(get_ticket_service)):
    subtotal = service.cotizar(datos.evento_id, datos.sector_id, datos.cantidad)
    return CotizacionResponse(subtotal=subtotal)


@router.post("/iniciar-pago", response_model=IniciarPagoResponse,
             summary="HU2 - Pagar y emitir entradas")
def iniciar_pago(datos: IniciarPagoRequest, service: TicketService = Depends(get_ticket_service)):
    venta = service.iniciar_pago(datos.cliente_id, datos.entradas_ids, datos.datos_tarjeta.numero)
    return IniciarPagoResponse(venta_id=venta.id, estado=venta.estado, total=venta.total)


@router.post("/escanear-acceso", response_model=EscaneoResponse,
             summary="HU3 - Escanear QR en puerta")
def escanear_acceso(datos: EscaneoRequest, service: TicketService = Depends(get_ticket_service)):
    hora = service.escanear_acceso(datos.codigo_qr)
    return EscaneoResponse(mensaje="Acceso Permitido", hora_ingreso=hora)

