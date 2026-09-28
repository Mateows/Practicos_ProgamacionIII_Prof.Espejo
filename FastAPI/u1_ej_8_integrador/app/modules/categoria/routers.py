from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import List
from . import schemas, services

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.post(
    "/", response_model=schemas.CategoriaRead, status_code=status.HTTP_201_CREATED
)
async def alta_categoria(categoria: schemas.CategoriaCreate):
    return await services.crear(categoria)


@router.get(
    "/", response_model=List[schemas.CategoriaRead], status_code=status.HTTP_200_OK
)
async def listar_categorias(skip: int = Query(0, ge=0), limit: int = Query(10, le=50)):
    return await services.obtener_todas(skip, limit)


@router.get(
    "/{id}", response_model=schemas.CategoriaRead, status_code=status.HTTP_200_OK
)
async def detalle_categoria(id: int = Path(..., gt=0)):
    categoria = await services.obtener_por_id(id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return categoria


@router.put(
    "/{id}", response_model=schemas.CategoriaRead, status_code=status.HTTP_200_OK
)
async def actualizar_categoria(categoria: schemas.CategoriaCreate, id: int = Path(..., gt=0)):
    actualizada = await services.actualizar_total(id, categoria)
    if not actualizada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return actualizada


@router.put(
    "/{id}/desactivar",
    response_model=schemas.CategoriaRead,
    status_code=status.HTTP_200_OK,
)
async def borrado_logico(id: int = Path(..., gt=0)):
    desactivada = await services.desactivar(id)
    if not desactivada:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return desactivada
