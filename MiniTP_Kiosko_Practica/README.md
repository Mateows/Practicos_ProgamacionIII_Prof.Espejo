# Mini TP — Kiosco (FastAPI)
Catálogo de productos con paginación, contratos con Pydantic, errores de dominio
propios y compra concurrente segura. Requiere **Python 3.11+** (se usa
`asyncio.TaskGroup` y `except*`) y **PostgreSQL** (los productos se guardan
en la base `kiosco_db`, usando SQLModel de forma asincronica con asyncpg).

## Sobre este proyecto

Este TP se hizo en dos etapas:

### Parte 1 — Fundamentos, contratos y asincronismo (Capítulos 1 a 3)
Se construyó el Kiosco completo (requisitos R1 a R14): fundamentos de FastAPI
y ASGI, contratos con Pydantic, y ejecución asincrónica. En esta etapa los
productos se guardaban en una **lista en memoria** — al reiniciar el
servidor, los datos se perdían.

### Parte 2 — Persistencia en PostgreSQL
Se migró el almacenamiento en memoria a **PostgreSQL**, usando SQLModel de
forma asincrónica (con `asyncpg`). Los datos ahora persisten entre
reinicios del servidor. Todo el comportamiento de la Parte 1 se mantuvo
intacto: validaciones, paginación, formato de errores propio, y la
protección contra condiciones de carrera al comprar.

## Instalación

```bash
cd MiniTP_Kiosko_Practica
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

## Base de datos

1. Crear la base (una sola vez), por ejemplo con `psql`:

   ```bash
   psql -U postgres -c "CREATE DATABASE kiosco_db;"
   ```

   La tabla `producto` la crea la app sola al arrancar (si no existe).

2. Configurar la variable de entorno `DATABASE_URL` con tu usuario y contraseña
   **en la misma terminal donde vas a correr el server** (la contraseña nunca
   se escribe en el codigo):

   ```bash
   # Git Bash
   export DATABASE_URL="postgresql+asyncpg://postgres:TU_PASSWORD@localhost:5432/kiosco_db"
   ```

   ```powershell
   # PowerShell
   $env:DATABASE_URL = "postgresql+asyncpg://postgres:TU_PASSWORD@localhost:5432/kiosco_db"
   ```

   ```bat
   :: cmd
   set DATABASE_URL=postgresql+asyncpg://postgres:TU_PASSWORD@localhost:5432/kiosco_db
   ```

   Si no se setea, `db.py` usa un placeholder sin credenciales y el server no
   va a poder conectarse.

## Correr el servidor

```bash
uvicorn main:app --reload
```

Documentación interactiva en http://127.0.0.1:8000/docs

## Endpoints principales

| Método y ruta | Descripción |
|---|---|
| `GET /productos?offset=0&limit=10` | Lista paginada. El total real va en el header `X-Total-Count`. |
| `GET /productos/{id}` | Un producto, o error 404 con formato propio. |
| `POST /productos` | Crea un producto. |
| `PATCH /productos/{id}` | Actualiza parcialmente (campos no enviados no se tocan). |
| `POST /productos/{id}/comprar` | Compra `cantidad` unidades, con verificación concurrente y stock protegido contra condiciones de carrera. |
| `GET /comparacion/sincrono` | 3 verificaciones simuladas, una atrás de la otra (~300ms). |
| `GET /comparacion/asincrono` | Las mismas 3 verificaciones en paralelo (~100ms). |

### Formato de error de dominio (R9)

Los errores de negocio (producto inexistente, no habilitado, stock insuficiente)
devuelven:

```json
{ "error": "stock_insuficiente", "mensaje": "Stock insuficiente para el producto 1: ..." }
```

en vez del `{"detail": "..."}` por defecto de FastAPI.

## Evidencia de concurrencia real (R11/R12)

Con el servidor corriendo en otra terminal:

```bash
python test_concurrencia.py
```

El script crea un producto con stock=10 y dispara 6 compras de 2 unidades
**al mismo tiempo** con `asyncio.gather` (12 unidades pedidas contra 10 de
stock). Algunas compras van a fallar con `stock_insuficiente`, pero el stock
final del servidor siempre queda consistente (nunca negativo, nunca "pisado"
por una compra que leyó un valor viejo).

> Como ahora los datos persisten en PostgreSQL, **cada corrida del script deja
> un producto nuevo guardado** en la base ("Producto de prueba - concurrencia").
> La proteccion con `asyncio.Lock` vale para un solo proceso: correr uvicorn
> sin `--workers` (un unico worker).
