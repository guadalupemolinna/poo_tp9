from app.database import Base, SessionLocal, engine
from app import models  # noqa: F401
from app.models import Cliente, Entrada, Evento, Lugar, PrecioSectorEvento, Sector


def cargar_datos_prueba():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        db.add(Cliente(nombre="Juan Pérez", email="juan@email.com"))

        lugar = Lugar(nombre="Estadio Municipal", direccion="Av. Costanera 123")
        db.add(lugar)
        db.commit()
        db.refresh(lugar)

        sector = Sector(nombre="Platea", capacidad=10, lugar_id=lugar.id)
        evento = Evento(nombre="Rock Fest", lugar_id=lugar.id)
        db.add_all([sector, evento])
        db.commit()
        db.refresh(sector)
        db.refresh(evento)

        db.add(PrecioSectorEvento(evento_id=evento.id, sector_id=sector.id, precio=12000.0))

        # Una entrada por cada lugar de la capacidad del sector
        for i in range(1, sector.capacidad + 1):
            db.add(Entrada(
                evento_id=evento.id,
                sector_id=sector.id,
                estado="Disponible",
                codigo_qr=f"QR-ROCKFEST-PLATEA-{i:03d}",
            ))

        db.commit()
        print("¡Datos de prueba cargados con éxito!")
        print(f"Evento ID: {evento.id} | Sector ID: {sector.id}")

    except Exception as e:
        db.rollback()
        print(f"Error al cargar los datos: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    cargar_datos_prueba()
