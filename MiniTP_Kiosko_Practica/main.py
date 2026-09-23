import asyncio
from contextlib import asynccontextmanager
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from typing_extensions import Annotated
from Producto import Producto, ProductoActualizar, ProductoCreate, CompraCrear
from Repo import ProductoRepositorio
from errores import ErrorDominio, ProductoNoEncontrado
from comparacion import router as comparacion_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    global repositorio_global

    repositorio_global = ProductoRepositorio() #Inicio
    yield
    repositorio_global = None #Cierro






app = FastAPI(lifespan=lifespan)


@app.exception_handler(ErrorDominio)
async def manejar_error_dominio(request: Request, exc: ErrorDominio):
    # R9: formato propio y estable para errores de dominio, en vez del
    # {"detail": "..."} default de FastAPI.
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.codigo, "mensaje": exc.mensaje},
    )


def notificar_compra(producto_id: int, cantidad: int) -> None:
    # R13: se ejecuta en segundo plano via BackgroundTasks, despues de responder al cliente.
    print(f"[notificacion] compra confirmada: producto={producto_id} cantidad={cantidad}")


def get_repo() -> ProductoRepositorio:
    if repositorio_global is None:
        raise HTTPException(status_code=500, detail="Repositorio no inicializado")
    return repositorio_global



@app.get("/productos", response_model=list[Producto])
async def listar_producto(
    response: Response,
    repo: Annotated[ProductoRepositorio, Depends(get_repo)],
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    productos = await repo.listar()
    response.headers["X-Total-Count"] = str(len(productos))  # R8: total en un header, no en el body
    return productos[offset: offset + limit]



@app.post("/productos", response_model=Producto, status_code=201)
async def crear_producto(
    producto_in: ProductoCreate,
    repo: Annotated[ProductoRepositorio, Depends(get_repo)],
):
    return await repo.crear(producto_in)



@app.get("/productos/{producto_id}", response_model=Producto)
async def obtener_producto(
    producto_id: int,
    repo: Annotated[ProductoRepositorio, Depends(get_repo)],
):
    producto = await repo.obtener_por_id(producto_id)
    if producto is None:
        raise ProductoNoEncontrado(producto_id)
    return producto



@app.patch("/productos/{producto_id}", response_model=Producto)
async def actualizar_producto(
    producto_id: int,
    cambios: ProductoActualizar,
    repo: Annotated[ProductoRepositorio, Depends(get_repo)],
):
    # R10: exclude_unset=True deja afuera los campos que el cliente no mando;
    # si mando un campo explicitamente en null, ese None SI queda en el dict.
    datos = cambios.model_dump(exclude_unset=True)
    return await repo.actualizar(producto_id, datos)



@app.post("/productos/{producto_id}/comprar", response_model=Producto)
async def comprar_producto(
    producto_id: int,
    compra: CompraCrear,
    background_tasks: BackgroundTasks,
    repo: Annotated[ProductoRepositorio, Depends(get_repo)],
):
    producto_actualizado = await repo.comprar(producto_id, compra.cantidad)
    background_tasks.add_task(notificar_compra, producto_id, compra.cantidad)
    return producto_actualizado


app.include_router(comparacion_router)




