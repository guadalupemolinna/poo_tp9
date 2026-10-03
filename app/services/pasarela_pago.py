from abc import ABC, abstractmethod


class PasarelaPago(ABC):
    """Abstracción de la pasarela (DIP): el servicio depende de esto, no de una implementación."""

    @abstractmethod
    def procesar_pago(self, monto: float, numero_tarjeta: str) -> bool:
        """Devuelve True si el pago fue aprobado."""


class PasarelaPagoSimulada(PasarelaPago):
    """Rechaza toda tarjeta cuyo número termine en 0000."""

    def procesar_pago(self, monto: float, numero_tarjeta: str) -> bool:
        return not numero_tarjeta.endswith("0000")
