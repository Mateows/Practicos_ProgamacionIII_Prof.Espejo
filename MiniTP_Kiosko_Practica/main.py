import asyncio
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from typing_extensions import Annotated
from Producto import Producto, ProductoCreate
from Repo import ProductoRepositorio



@asynccontextmanager
async def lifespan(app: FastAPI):
    global repositorio_global

    repositorio_global = ProductoRepositorio() #Inicio
    yield
    repositorio_global = None #Cierro






app = FastAPI(lifespan=lifespan)

def get_repo() -> ProductoRepositorio:
    if repositorio_global is None:
        raise HTTPException(status_code=500, detail="Repositorio no inicializado")
    return repositorio_global



@app.get("/productos", response_model=list[Producto])
async def listar_producto(
    repo: Annotated[ProductoRepositorio, Depends(get_repo)]
):
    return await repo.listar()



@app.post("productos", response_model=Producto, status_code=201)
async def crear_producto(
    producto_in: ProductoCreate,
    repo: Annotated[ProductoRepositorio, Depends(get_repo)],
):
    return await repo.crear(producto_in)




