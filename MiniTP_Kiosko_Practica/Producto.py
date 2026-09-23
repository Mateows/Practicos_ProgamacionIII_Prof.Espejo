from pydantic import BaseModel, Field, model_validator
from typing import Optional
from decimal import Decimal


class ProductoBase(BaseModel):
    """Campos y validaciones comunes a ProductoCreate y Producto (R7: evita duplicar el validador)."""

    nombre: str = Field(..., min_length=1, max_length=120)
    precio: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    stock_reservado: int = Field(ge=0)
    habilitado: bool = True
    categoria: Optional[str] = None

    ##Validador de que el stock reservado no supere al stock actual
    @model_validator(mode="after")
    def validar_stock(self):
        if self.stock_reservado > self.stock:
            raise ValueError("El stock reservado no puede ser superar al stock")
        return self


class ProductoCreate(ProductoBase):
    """Modelo de entrada para crear un producto (R5)."""
    pass


class Producto(ProductoBase):
    """Modelo de lectura: lo que devuelve la API, incluye el id asignado por el servidor (R5)."""
    id: int


class ProductoActualizar(BaseModel):
    """Modelo de entrada para PATCH: todos los campos opcionales (R5, R10).

    La validación de stock_reservado <= stock para el estado final no se hace acá
    (no siempre llegan los dos campos juntos en un PATCH parcial): se revalida en el
    repositorio reconstruyendo el Producto completo con los cambios ya aplicados,
    lo que dispara el validador de ProductoBase sobre el estado resultante real.
    """

    nombre: Optional[str] = Field(default=None, min_length=1, max_length=120)
    precio: Optional[Decimal] = Field(default=None, gt=0)
    stock: Optional[int] = Field(default=None, ge=0)
    stock_reservado: Optional[int] = Field(default=None, ge=0)
    habilitado: Optional[bool] = None
    categoria: Optional[str] = None


class CompraCrear(BaseModel):
    """Body de POST /productos/{id}/comprar."""

    cantidad: int = Field(gt=0)
