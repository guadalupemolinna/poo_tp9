from abc import ABC, abstractmethod


class PasarelaPago(ABC):

    @abstractmethod
    def cobrar(self, monto: float, datos_tarjeta: dict) -> str:
        pass


class PasarelaPagoSimulada(PasarelaPago):

    def cobrar(self, monto: float, datos_tarjeta: dict) -> str:
        numero_tarjeta = datos_tarjeta.get("numero", "")

        if numero_tarjeta.endswith("0000"):
            return "Rechazado"

        return "Aprobado"
    