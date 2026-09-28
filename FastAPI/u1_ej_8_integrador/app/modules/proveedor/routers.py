from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import List, Optional
from . import schemas
from .services import ProveedorService

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.post(
    "/",
    response_model=schemas.ProveedorRead,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo proveedor"
)
async def alta_proveedor(proveedor: schemas.ProveedorCreate):
    """
    Capa de Controlador (HTTP Endpoint) para dar de alta un proveedor.
    Delega la lógica de negocio y validación de unicidad al servicio.
    """
    return await ProveedorService.crear(proveedor)


@router.get(
    "/",
    response_model=List[schemas.ProveedorRead],
    status_code=status.HTTP_200_OK,
    summary="Listar proveedores con paginación y filtros"
)
async def listar_proveedores(
    skip: int = Query(0, ge=0, description="Cantidad de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad máxima de registros a retornar"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo/inactivo")
):
    """
    Lista todos los proveedores aplicando paginación y filtro opcional por estado.
    """
    return await ProveedorService.obtener_todos(skip=skip, limit=limit, activo=activo)


@router.get(
    "/{id}",
    response_model=schemas.ProveedorRead,
    status_code=status.HTTP_200_OK,
    summary="Consultar proveedor por ID"
)
async def detalle_proveedor(id: int = Path(..., gt=0, description="Identificador único del proveedor")):
    """
    Obtiene el detalle de un proveedor específico según su ID.
    """
    return await ProveedorService.obtener_por_id(id)


@router.put(
    "/{id}",
    response_model=schemas.ProveedorRead,
    status_code=status.HTTP_200_OK,
    summary="Actualización total de proveedor"
)
async def actualizar_proveedor(
    proveedor: schemas.ProveedorCreate,
    id: int = Path(..., gt=0, description="Identificador único del proveedor")
):
    """
    Reemplaza todos los datos de un proveedor existente.
    """
    return await ProveedorService.actualizar_total(id, proveedor)


@router.patch(
    "/{id}",
    response_model=schemas.ProveedorRead,
    status_code=status.HTTP_200_OK,
    summary="Actualización parcial de proveedor"
)
async def actualizar_parcial_proveedor(
    proveedor: schemas.ProveedorUpdate,
    id: int = Path(..., gt=0, description="Identificador único del proveedor")
):
    """
    Actualiza parcialmente los campos proporcionados de un proveedor.
    """
    return await ProveedorService.actualizar_parcial(id, proveedor)


@router.put(
    "/{id}/desactivar",
    response_model=schemas.ProveedorRead,
    status_code=status.HTTP_200_OK,
    summary="Borrado lógico de proveedor"
)
async def borrado_logico_proveedor(id: int = Path(..., gt=0, description="Identificador único del proveedor")):
    """
    Desactiva lógicamente un proveedor cambiando su estado a inactivo (activo = False).
    """
    return await ProveedorService.desactivar(id)
