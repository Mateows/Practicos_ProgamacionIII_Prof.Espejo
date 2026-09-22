import asyncio
from typing import List, Optional
from Producto import Producto, ProductoCreate



class ProductoRepositorio:

    def __init__(self):
        self.productos: list[Producto] = []
        self._contador_id=0



    async def listar(self) -> List[Producto]:
        await asyncio.sleep(0.05)
        return self.productos


    async def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        await asyncio.sleep(0.05)
        for p in self.productos:
            if p.id == producto_id:
                return p
        return None

    
    async def crear(self, producto_in: ProductoCreate) -> Producto:
        await asyncio.sleep(0.05)
        self._contador_id += 1
        nuevo_producto = Producto(id=self._contador_id, **producto_in.model_dump())
        self.productos.append(nuevo_producto)
        return nuevo_producto