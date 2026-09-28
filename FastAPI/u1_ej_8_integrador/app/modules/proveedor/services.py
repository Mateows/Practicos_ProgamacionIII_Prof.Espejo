from typing import List, Optional
from fastapi import HTTPException, status
from .schemas import ProveedorCreate, ProveedorRead, ProveedorUpdate

# Simulación de Repositorio en memoria con persistencia compartida
db_proveedores: List[ProveedorRead] = [
    ProveedorRead(
        id=1,
        codigo="PRV-001",
        razon_social="Proveedor Global S.R.L.",
        cuit="30-71234567-8",
        email="ventas@global.com",
        telefono="+541144556677",
        activo=True
    ),
    ProveedorRead(
        id=2,
        codigo="PRV-002",
        razon_social="Insumos del Sur S.A.",
        cuit="30-65432109-4",
        email="contacto@insumossur.com",
        telefono="+541188990011",
        activo=True
    )
]
id_counter = 3


class ProveedorService:
    """
    Capa de Servicios (Domain Logic / Repository Pattern simulation).
    Encapsula las reglas de negocio, validaciones de integridad transaccional
    y excepciones de dominio de forma asíncrona.
    """

    @staticmethod
    async def crear(data: ProveedorCreate) -> ProveedorRead:
        global id_counter
        # Validación de reglas de negocio: unicidad de código y CUIT
        for p in db_proveedores:
            if p.codigo == data.codigo:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un proveedor con el código '{data.codigo}'."
                )
            if p.cuit == data.cuit:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un proveedor registrado con el CUIT '{data.cuit}'."
                )

        nuevo_proveedor = ProveedorRead(id=id_counter, **data.model_dump())
        db_proveedores.append(nuevo_proveedor)
        id_counter += 1
        return nuevo_proveedor

    @staticmethod
    async def obtener_todos(skip: int = 0, limit: int = 10, activo: Optional[bool] = None) -> List[ProveedorRead]:
        resultado = db_proveedores
        if activo is not None:
            resultado = [p for p in resultado if p.activo == activo]
        return resultado[skip : skip + limit]

    @staticmethod
    async def obtener_por_id(id: int) -> ProveedorRead:
        for p in db_proveedores:
            if p.id == id:
                return p
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {id} no encontrado."
        )

    @staticmethod
    async def actualizar_total(id: int, data: ProveedorCreate) -> ProveedorRead:
        # Verificar existencia
        await ProveedorService.obtener_por_id(id)

        # Validar unicidad si cambian código o CUIT
        for p in db_proveedores:
            if p.id != id:
                if p.codigo == data.codigo:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El código '{data.codigo}' ya está en uso por otro proveedor."
                    )
                if p.cuit == data.cuit:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El CUIT '{data.cuit}' ya está registrado por otro proveedor."
                    )

        for index, p in enumerate(db_proveedores):
            if p.id == id:
                proveedor_actualizado = ProveedorRead(id=id, **data.model_dump())
                db_proveedores[index] = proveedor_actualizado
                return proveedor_actualizado
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {id} no encontrado."
        )

    @staticmethod
    async def actualizar_parcial(id: int, data: ProveedorUpdate) -> ProveedorRead:
        proveedor_actual = await ProveedorService.obtener_por_id(id)
        
        update_data = data.model_dump(exclude_unset=True)
        
        # Validar unicidad si se actualizan código o CUIT
        if "codigo" in update_data and update_data["codigo"] != proveedor_actual.codigo:
            for p in db_proveedores:
                if p.id != id and p.codigo == update_data["codigo"]:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El código '{update_data['codigo']}' ya está en uso."
                    )
                    
        if "cuit" in update_data and update_data["cuit"] != proveedor_actual.cuit:
            for p in db_proveedores:
                if p.id != id and p.cuit == update_data["cuit"]:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El CUIT '{update_data['cuit']}' ya está registrado."
                    )

        for index, p in enumerate(db_proveedores):
            if p.id == id:
                p_dict = p.model_dump()
                p_dict.update(update_data)
                proveedor_actualizado = ProveedorRead(**p_dict)
                db_proveedores[index] = proveedor_actualizado
                return proveedor_actualizado

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {id} no encontrado."
        )

    @staticmethod
    async def desactivar(id: int) -> ProveedorRead:
        proveedor = await ProveedorService.obtener_por_id(id)
        
        if not proveedor.activo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El proveedor con ID {id} ya se encuentra inactivo."
            )

        for index, p in enumerate(db_proveedores):
            if p.id == id:
                p_dict = p.model_dump()
                p_dict["activo"] = False
                proveedor_desactivado = ProveedorRead(**p_dict)
                db_proveedores[index] = proveedor_desactivado
                return proveedor_desactivado

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Proveedor con ID {id} no encontrado."
        )
