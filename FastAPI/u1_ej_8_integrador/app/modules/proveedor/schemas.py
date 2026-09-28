from pydantic import BaseModel, Field
from typing import Optional


class ProveedorBase(BaseModel):
    codigo: str = Field(..., min_length=3, max_length=20, pattern=r"^[A-Z]{3}-\d{3}$", example="PRV-001")
    razon_social: str = Field(..., min_length=3, max_length=100, example="Distribuidora Mayorista S.A.")
    cuit: str = Field(..., pattern=r"^\d{2}-\d{8}-\d{1}$", example="30-12345678-9")
    email: Optional[str] = Field(None, example="contacto@proveedor.com")
    telefono: Optional[str] = Field(None, min_length=6, max_length=20, example="+54911223344")
    activo: bool = True


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    codigo: Optional[str] = Field(None, min_length=3, max_length=20, pattern=r"^[A-Z]{3}-\d{3}$")
    razon_social: Optional[str] = Field(None, min_length=3, max_length=100)
    cuit: Optional[str] = Field(None, pattern=r"^\d{2}-\d{8}-\d{1}$")
    email: Optional[str] = None
    telefono: Optional[str] = Field(None, min_length=6, max_length=20)
    activo: Optional[bool] = None


class ProveedorRead(ProveedorBase):
    id: int
