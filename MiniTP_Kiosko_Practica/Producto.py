from pydantic import BaseModel, Field, model_validator
from typing import Optional
from decimal import Decimal



class ProductoCreate(BaseModel):
    nombre: str= Field(..., min_length=1, max_length=120)
    precio: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    stock_reservado: int = Field(ge=0)
    ##Validador de que el stock de serva no supere al stock actual


    @model_validator(mode="after")
    def validar_stock(self):
        if self.stock_reservado > self.stock:
            raise ValueError("El stock reservado no puede ser superar al stock")
        return self
    producto : bool = True
    categoria: Optional[str] = None


class Producto(BaseModel):
    id: int
    nombre: str= Field(..., min_length=1, max_length=120)
    precio: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    stock_reservado: int = Field(ge=0)
    ##Validador de que el stock de serva no supere al stock actual


    @model_validator(mode="after")
    def validar_stock(self):
        if self.stock_reservado > self.stock:
            raise ValueError("El stock reservado no puede ser superar al stock")
        return self
    producto : bool = True
    categoria: Optional[str] = None



