# TP 9 - POO — SmartTicket

API para gestión de entradas, pagos y control de acceso a eventos, desarrollada con **FastAPI**, **SQLAlchemy** y **SQLite**.

## Tecnologías

Python 3.13 · FastAPI · Uvicorn · SQLAlchemy · SQLite · Pydantic

## Estructura del proyecto

```text
poo_tp9/
├── app/
│   ├── main.py             # App FastAPI, creación de tablas y manejo de errores de negocio
│   ├── database.py         # Conexión SQLite y sesiones
│   ├── models.py           # Entidades (Lugar, Sector, Evento, PrecioSectorEvento, Entrada, Cliente, Venta)
│   ├── schemas.py          # Esquemas Pydantic
│   ├── repositories.py     # Acceso a datos
│   ├── routers/
│   │   └── pagos.py        # Endpoints
│   └── services/
│       ├── ticket_service.py   # Lógica de negocio
│       ├── pasarela_pago.py    # PasarelaPago (abstracta) y PasarelaPagoSimulada
│       └── excepciones.py      # Errores de dominio con su código HTTP
├── seed.py                 # Datos de prueba
├── requirements.txt
└── README.md
```

## Instalación y ejecución

```powershell
git clone https://github.com/guadalupemolinna/poo_tp9.git
cd poo_tp9
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python seed.py
python -m uvicorn app.main:app --reload
```

Si PowerShell bloquea la activación: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`.

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

## Base de datos

`seed.py` crea las tablas y carga los datos de prueba en `database.db` (no se sube al repositorio). Para regenerarla: detener el servidor, borrar `database.db` y volver a ejecutar `python seed.py`.

> No ejecutar `seed.py` dos veces sobre la misma base: duplica los datos.

### Datos de prueba

| Entidad | Datos |
|---|---|
| Evento | ID 1 — Rock Fest |
| Sector | ID 1 — Platea, capacidad 10, precio $12000 |
| Cliente | ID 1 — Juan Pérez (juan@email.com) |
| Entradas | IDs 1 a 10, QR `QR-ROCKFEST-PLATEA-001` a `QR-ROCKFEST-PLATEA-010` |

## Endpoints

### HU1 — `POST /pagos/cotizar`

```json
{ "evento_id": 1, "sector_id": 1, "cantidad": 2 }
```
Respuesta `200`: `{ "subtotal": 24000.0 }`

| Caso | HTTP | Mensaje |
|---|---|---|
| Cantidad 0 o negativa | 400 | La cantidad de entradas solicitadas debe ser mayor a cero |
| Sin disponibilidad | 400 | Capacidad insuficiente o entradas no disponibles |

### HU2 — `POST /pagos/iniciar-pago`

```json
{
  "cliente_id": 1,
  "entradas_ids": [1, 2],
  "datos_tarjeta": { "numero": "1234567890123456" }
}
```
Respuesta `200`: `{ "venta_id": 1, "estado": "Pagada", "total": 24000.0 }`. Las entradas pasan a **Emitida**.

La pasarela es simulada: **toda tarjeta que termina en `0000` es rechazada**.

| Caso | HTTP | Mensaje |
|---|---|---|
| Pago rechazado (entradas siguen Disponibles) | 402 | Pago denegado |
| Entradas ya no disponibles (se aborta antes de la pasarela) | 409 | Los lugares seleccionados ya no se encuentran disponibles |

### HU3 — `POST /pagos/escanear-acceso`

```json
{ "codigo_qr": "QR-ROCKFEST-PLATEA-001" }
```
Respuesta `200`: `{ "mensaje": "Acceso Permitido", "hora_ingreso": "..." }`. La entrada pasa de **Emitida** a **Utilizada**.

| Caso | HTTP | Mensaje |
|---|---|---|
| QR inexistente | 404 | Ticket Inválido o Inexistente |
| Entrada ya utilizada | 409 | Entrada ya utilizada |
| Entrada Disponible o Reservada | 400 | Ticket no emitido / Falta de pago |

## Arquitectura (GRASP y SOLID)

- **SRP:** el router solo recibe la petición y responde; la lógica está en `TicketService`.
- **Experto en Información:** `PrecioSectorEvento` calcula el subtotal y `Entrada` maneja sus propios cambios de estado.
- **DIP / inyección de dependencias:** `TicketService` recibe repositorios y `PasarelaPago` por constructor; el router los arma con `Depends`.
- **Abierto/Cerrado:** se puede reemplazar la pasarela simulada por una real implementando `PasarelaPago`.
- **Concurrencia:** las entradas se reservan con un `UPDATE` condicional (Disponible → Reservada) antes de consultar la pasarela, y se liberan si el pago es rechazado.

## Flujo de estados

- Entrada: `Disponible → Reservada → Emitida → Utilizada`
- Venta: `Pendiente`, `Pagada`, `Cancelada`

## Repositorio

https://github.com/guadalupemolinna/poo_tp9
