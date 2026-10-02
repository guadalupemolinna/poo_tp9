from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import (
    CotizacionRequest,
    CotizacionResponse,
    PagoRequest,
    PagoResponse,
    EscanearAccesoRequest,
    EscanearAccesoResponse
)
from ..services.ticket_service import (
    TicketService,
    EntradasNoDisponiblesError,
    PagoDenegadoError,
    TicketInvalidoError,
    EntradaYaUtilizadaError,
    TicketNoEmitidoError
)
from ..services.pasarela_pago import PasarelaPagoSimulada


router = APIRouter(
    prefix="/pagos",
    tags=["Pagos"]
)


@router.post("/cotizar", response_model=CotizacionResponse)
def cotizar(
    datos: CotizacionRequest,
    db: Session = Depends(get_db)
):
    servicio = TicketService(
        db,
        PasarelaPagoSimulada()
    )

    try:
        subtotal = servicio.cotizar(
            evento_id=datos.evento_id,
            sector_id=datos.sector_id,
            cantidad=datos.cantidad
        )

        return CotizacionResponse(subtotal=subtotal)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/iniciar-pago", response_model=PagoResponse)
def iniciar_pago(
    datos: PagoRequest,
    db: Session = Depends(get_db)
):
    servicio = TicketService(
        db,
        PasarelaPagoSimulada()
    )

    try:
        venta = servicio.procesar_pago(
            cliente_id=datos.cliente_id,
            entradas_ids=datos.entradas_ids,
            datos_tarjeta=datos.datos_tarjeta
        )

        return PagoResponse(
            venta_id=venta.id,
            estado=venta.estado,
            total=venta.total
        )

    except EntradasNoDisponiblesError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    except PagoDenegadoError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("/webhook-pagos")
def webhook_pagos():
    pass


@router.post(
    "/escanear-acceso",
    response_model=EscanearAccesoResponse
)
def escanear_acceso(
    datos: EscanearAccesoRequest,
    db: Session = Depends(get_db)
):
    servicio = TicketService(
        db,
        PasarelaPagoSimulada()
    )

    try:
        hora_ingreso = servicio.escanear_acceso(
            datos.codigo_qr
        )

        return EscanearAccesoResponse(
            mensaje="Acceso Permitido",
            hora_ingreso=hora_ingreso
        )

    except TicketInvalidoError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )

    except EntradaYaUtilizadaError as error:
        raise HTTPException(
            status_code=409,
            detail=str(error)
        )

    except TicketNoEmitidoError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )