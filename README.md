# TP 9 - POO — SmartTicket

API para gestión de entradas y pagos de eventos, desarrollada con **FastAPI**, **SQLAlchemy** y **SQLite**.

## 📋 Tecnologías

* Python 3.13
* FastAPI
* Uvicorn
* SQLAlchemy
* SQLite
* Pydantic

---

## 📁 Estructura del proyecto

```text
TP_9_POO/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   └── pagos.py
│   │
│   └── services/
│       ├── ticket_service.py
│       └── pasarela_pago.py
│
├── seed.py
├── database.db
├── .gitignore
└── README.md
```

---

# 🚀 Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/guadalupemolinna/poo_tp9.git
cd poo_tp9
```

## 2. Crear el entorno virtual

### Windows

```powershell
py -3.13 -m venv .venv
```

Activarlo:

```powershell
.venv\Scripts\activate
```

Si aparece `(.venv)` al comienzo de la terminal, está activado correctamente.

---

## 3. Instalar las dependencias

```powershell
python -m pip install fastapi uvicorn sqlalchemy
```

---

# ▶️ Ejecutar la API

Con el entorno virtual activado:

```powershell
python -m uvicorn app.main:app --reload
```

La API queda disponible en:

```text
http://127.0.0.1:8000
```

La documentación interactiva de Swagger está en:

```text
http://127.0.0.1:8000/docs
```

Desde Swagger se pueden probar todos los endpoints.

---

# 🗃️ Base de datos

El proyecto utiliza **SQLite** mediante SQLAlchemy.

La base de datos utilizada es:

```text
database.db
```

El proyecto ya incluye datos de prueba para poder probar las historias de usuario.

Si se necesita generar nuevamente una base de datos desde cero, primero eliminar `database.db` y luego ejecutar:

```powershell
python seed.py
```

> ⚠️ No ejecutar `seed.py` sobre una base de datos que ya tenga los datos cargados, porque puede generar registros duplicados.

---

# 🎟️ Datos de prueba

Actualmente se dispone de:

### Evento

```text
ID: 1
Nombre: Rock Fest
```

### Sector

```text
ID: 1
Nombre: Platea
Capacidad: 10
Precio: $12000
```

### Cliente

```text
ID: 1
Nombre: Juan Pérez
Email: juan@email.com
```

---

# 🧪 Historias de Usuario

## HU1 — Cotización de entradas

Endpoint:

```text
POST /pagos/cotizar
```

Ejemplo:

```json
{
  "evento_id": 1,
  "sector_id": 1,
  "cantidad": 2
}
```

Respuesta esperada:

```json
{
  "subtotal": 24000
}
```

### Validaciones

Si la cantidad es `0` o negativa:

```text
La cantidad de entradas solicitadas debe ser mayor a cero
```

Si no hay suficientes entradas disponibles:

```text
Capacidad insuficiente o entradas no disponibles
```

---

# 💳 HU2 — Iniciar pago

Endpoint:

```text
POST /pagos/iniciar-pago
```

Ejemplo:

```json
{
  "cliente_id": 1,
  "entradas_ids": [1, 2],
  "datos_tarjeta": {
    "numero": "1234567890123456"
  }
}
```

Respuesta:

```json
{
  "venta_id": 1,
  "estado": "Pagada",
  "total": 24000
}
```

Las entradas utilizadas para una compra aprobada pasan a estado:

```text
Emitida
```

### Pago rechazado

La pasarela de pago está simulada.

Si el número de tarjeta termina en:

```text
0000
```

el pago es rechazado.

Ejemplo:

```json
{
  "cliente_id": 1,
  "entradas_ids": [3],
  "datos_tarjeta": {
    "numero": "1234567890120000"
  }
}
```

Respuesta:

```text
Pago denegado
```

Las entradas no se emiten si el pago es rechazado.

---

# 📱 HU3 — Escanear acceso

Endpoint:

```text
POST /pagos/escanear-acceso
```

Para una entrada emitida se utiliza el código QR que tenga almacenado.

Ejemplo:

```json
{
  "codigo_qr": "CODIGO_DEL_TICKET"
}
```

Si el ticket es válido y está emitido:

```json
{
  "mensaje": "Acceso Permitido",
  "hora_ingreso": "2026-10-02T18:39:22.917393"
}
```

La entrada pasa de:

```text
Emitida → Utilizada
```

y se registra la hora de ingreso.

### Casos de error

#### QR inexistente

Respuesta:

```text
Ticket Inválido o Inexistente
```

#### Ticket ya utilizado

Respuesta:

```text
Entrada ya utilizada
```

#### Ticket sin emitir

Si la entrada está `Disponible` o `Reservada`:

```text
Ticket no emitido / Falta de pago
```

---

# 🔌 Otros endpoints

## Webhook de pagos

```text
POST /pagos/webhook-pagos
```

Endpoint preparado para recibir notificaciones de una pasarela de pagos.

---

# 🧱 Arquitectura

El proyecto está organizado separando responsabilidades:

### `models.py`

Contiene los modelos de SQLAlchemy que representan las entidades de la base de datos.

### `schemas.py`

Contiene los modelos de Pydantic utilizados para validar las solicitudes y respuestas de la API.

### `ticket_service.py`

Contiene la lógica principal del negocio:

* Cotización.
* Procesamiento de pagos.
* Emisión de entradas.
* Validación de tickets.
* Registro de acceso.

### `pasarela_pago.py`

Contiene la abstracción de la pasarela de pago y una implementación simulada.

Se utiliza una clase abstracta:

```python
PasarelaPago
```

y una implementación concreta:

```python
PasarelaPagoSimulada
```

### `pagos.py`

Contiene los endpoints de FastAPI relacionados con pagos, cotizaciones y acceso.

### `database.py`

Configura la conexión con SQLite y las sesiones de SQLAlchemy.

---

# 🛑 Detener el servidor

Para detener Uvicorn:

```text
Ctrl + C
```

---

# 👥 Integrantes

TP 9 — Programación Orientada a Objetos

Repositorio:

https://github.com/guadalupemolinna/poo_tp9
