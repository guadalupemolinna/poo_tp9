class DominioError(Exception):
    """Error de negocio. Lleva su propio código HTTP; el controlador no decide nada."""

    status_code = 400

    def __init__(self, mensaje: str):
        super().__init__(mensaje)
        self.mensaje = mensaje


class CantidadInvalida(DominioError):
    status_code = 400


class CapacidadInsuficiente(DominioError):
    status_code = 400


class PrecioNoDefinido(DominioError):
    status_code = 404


class ClienteNoEncontrado(DominioError):
    status_code = 404


class EntradasNoDisponibles(DominioError):
    status_code = 409


class PagoDenegado(DominioError):
    status_code = 402


class TicketInvalido(DominioError):
    status_code = 404


class EntradaYaUtilizada(DominioError):
    status_code = 409


class TicketNoEmitido(DominioError):
    status_code = 400
