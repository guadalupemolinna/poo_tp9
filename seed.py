from app.database import SessionLocal
from app.models import Lugar, Sector, Evento, PrecioSectorEvento, Entrada, Cliente

cliente = Cliente(
    nombre="Juan Pérez",
    email="juan@email.com"
)
db.add(cliente)
db.commit()
db.refresh(cliente)

def cargar_datos_prueba():
    db = SessionLocal()

    try:
        # 1. Crear un Lugar
        lugar = Lugar(
            nombre="Estadio Municipal",
            direccion="Av. Costanera 123"
        )
        db.add(lugar)
        db.commit()
        db.refresh(lugar)

        # 2. Crear un Sector
        sector = Sector(
            nombre="Platea",
            capacidad=10,
            lugar_id=lugar.id
        )
        db.add(sector)
        db.commit()
        db.refresh(sector)

        # 3. Crear el Evento
        evento = Evento(
            nombre="Rock Fest",
            lugar_id=lugar.id
        )
        db.add(evento)
        db.commit()
        db.refresh(evento)

        # 4. Definir el precio
        precio_sector = PrecioSectorEvento(
            evento_id=evento.id,
            sector_id=sector.id,
            precio=12000.0
        )
        db.add(precio_sector)

        # 5. Crear 5 entradas disponibles
        for i in range(1, 6):
            entrada = Entrada(
                evento_id=evento.id,
                sector_id=sector.id,
                estado="Disponible",
                codigo_qr=f"QR-ROCKFEST-PLATEA-00{i}"
            )
            db.add(entrada)

        db.commit()

        print("¡Datos de prueba cargados con éxito!")
        print(f"Evento ID: {evento.id}")
        print(f"Sector ID: {sector.id}")

    except Exception as e:
        db.rollback()
        print(f"Error al cargar los datos: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    cargar_datos_prueba()