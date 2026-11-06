from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Lugar, Sector, Evento, Cliente, PrecioSectorEvento
from app.repositories import (LugarRepository, SectorRepository, EventoRepository,
                              ClienteRepository, PrecioRepository)
from app.schemas import (LugarCreate, LugarRead, SectorCreate, SectorRead,
                         EventoCreate, EventoRead, ClienteCreate, ClienteRead,
                         PrecioSectorEventoCreate, PrecioSectorEventoRead)

router = APIRouter(prefix="/admin", tags=["Administración / CRUD"])

# --- LUGARES ---
@router.post("/lugares", response_model=LugarRead, summary="Crear un Lugar")
def crear_lugar(datos: LugarCreate, db: Session = Depends(get_db)):
    repo = LugarRepository(db)
    return repo.crear(Lugar(**datos.model_dump()))

@router.get("/lugares", response_model=List[LugarRead], summary="Listar Lugares")
def listar_lugares(db: Session = Depends(get_db)):
    repo = LugarRepository(db)
    return repo.listar()

@router.get("/lugares/{lugar_id}", response_model=LugarRead, summary="Buscar Lugar por ID")
def obtener_lugar(lugar_id: int, db: Session = Depends(get_db)):
    repo = LugarRepository(db)
    lugar = repo.obtener(lugar_id)
    if not lugar:
        raise HTTPException(status_code=404, detail="Lugar no encontrado")
    return lugar

# --- SECTORES ---
@router.post("/sectores", response_model=SectorRead, summary="Crear un Sector")
def crear_sector(datos: SectorCreate, db: Session = Depends(get_db)):
    repo = SectorRepository(db)
    return repo.crear(Sector(**datos.model_dump()))

@router.get("/sectores", response_model=List[SectorRead], summary="Listar Sectores")
def listar_sectores(db: Session = Depends(get_db)):
    repo = SectorRepository(db)
    return repo.listar()

@router.get("/sectores/{sector_id}", response_model=SectorRead, summary="Buscar Sector por ID")
def obtener_sector(sector_id: int, db: Session = Depends(get_db)):
    repo = SectorRepository(db)
    sector = repo.obtener(sector_id)
    if not sector:
        raise HTTPException(status_code=404, detail="Sector no encontrado")
    return sector

# --- EVENTOS ---
@router.post("/eventos", response_model=EventoRead, summary="Crear un Evento")
def crear_evento(datos: EventoCreate, db: Session = Depends(get_db)):
    repo = EventoRepository(db)
    return repo.crear(Evento(**datos.model_dump()))

@router.get("/eventos", response_model=List[EventoRead], summary="Listar Eventos")
def listar_eventos(db: Session = Depends(get_db)):
    repo = EventoRepository(db)
    return repo.listar()

@router.get("/eventos/{evento_id}", response_model=EventoRead, summary="Buscar Evento por ID")
def obtener_evento(evento_id: int, db: Session = Depends(get_db)):
    repo = EventoRepository(db)
    evento = repo.obtener(evento_id)
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    return evento

# --- CLIENTES ---
@router.post("/clientes", response_model=ClienteRead, summary="Crear un Cliente")
def crear_cliente(datos: ClienteCreate, db: Session = Depends(get_db)):
    repo = ClienteRepository(db)
    return repo.crear(Cliente(**datos.model_dump()))

@router.get("/clientes", response_model=List[ClienteRead], summary="Listar Clientes")
def listar_clientes(db: Session = Depends(get_db)):
    repo = ClienteRepository(db)
    return repo.listar()

@router.get("/clientes/{cliente_id}", response_model=ClienteRead, summary="Buscar Cliente por ID")
def obtener_cliente(cliente_id: int, db: Session = Depends(get_db)):
    repo = ClienteRepository(db)
    cliente = repo.obtener(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

# --- PRECIOS ---
@router.post("/precios", response_model=PrecioSectorEventoRead, summary="Asignar Precio")
def crear_precio(datos: PrecioSectorEventoCreate, db: Session = Depends(get_db)):
    repo = PrecioRepository(db)
    return repo.crear(PrecioSectorEvento(**datos.model_dump()))

@router.get("/precios", response_model=List[PrecioSectorEventoRead], summary="Listar Precios")
def listar_precios(db: Session = Depends(get_db)):
    repo = PrecioRepository(db)
    return repo.listar()

@router.get("/precios/{precio_id}", response_model=PrecioSectorEventoRead, summary="Buscar Precio por ID")
def obtener_precio(precio_id: int, db: Session = Depends(get_db)):
    repo = PrecioRepository(db)
    precio = repo.obtener_por_id(precio_id)
    if not precio:
        raise HTTPException(status_code=404, detail="Precio no encontrado")
    return precio