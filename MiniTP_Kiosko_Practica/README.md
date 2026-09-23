# Mini TP — Kiosco (FastAPI)
Catálogo de productos con paginación, contratos con Pydantic, errores de dominio
propios y compra concurrente segura. Requiere **Python 3.11+** (se usa
`asyncio.TaskGroup` y `except*`).

## Instalación

```bash
cd MiniTP_Kiosko_Practica
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

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
