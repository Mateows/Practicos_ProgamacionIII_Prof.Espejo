import asyncio
from typing import List, Optional
from Producto import Producto, ProductoCreate
from errores import ErrorDominio, ProductoNoEncontrado, ProductoNoHabilitado, StockInsuficiente



class ProductoRepositorio:

    def __init__(self):
        self.productos: list[Producto] = []
        self._contador_id=0
        self._locks: dict[int, asyncio.Lock] = {}



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


    def _lock_de(self, producto_id: int) -> asyncio.Lock:
        # No hay await entre el "in" y el guardado, asi que no hace falta proteger esto:
        # el event loop no puede intercalar otra corrutina en el medio.
        if producto_id not in self._locks:
            self._locks[producto_id] = asyncio.Lock()
        return self._locks[producto_id]


    async def actualizar(self, producto_id: int, cambios: dict) -> Producto:
        """R10: 'cambios' ya viene filtrado con exclude_unset=True desde main.py,
        asi que solo trae las claves que el cliente realmente envio (incluido None
        si lo envio explicito). Reconstruir el Producto completo con esos cambios
        vuelve a correr el @model_validator de stock sobre el estado final.

        Usa el mismo lock por producto que comprar(), para que un PATCH y una
        compra concurrentes sobre el mismo producto no se pisen entre si."""
        async with self._lock_de(producto_id):
            await asyncio.sleep(0.05)
            for i, p in enumerate(self.productos):
                if p.id == producto_id:
                    datos = p.model_dump()
                    datos.update(cambios)
                    actualizado = Producto(**datos)
                    self.productos[i] = actualizado
                    return actualizado
            raise ProductoNoEncontrado(producto_id)


    async def comprar(self, producto_id: int, cantidad: int) -> Producto:
        """R11: habilitado y stock se verifican concurrentemente con TaskGroup.
        R12: todo el ciclo verificar+descontar corre bajo un Lock por producto,
        para que dos compras del mismo producto no lean el mismo stock viejo
        y lo pisen (si el chequeo quedara afuera del lock, dos compras podrian
        pasar la verificacion antes de que cualquiera descuente, y sobrevenderiamos)."""
        lock = self._lock_de(producto_id)
        async with lock:
            await asyncio.sleep(0.05)

            indice = None
            producto = None
            for i, p in enumerate(self.productos):
                if p.id == producto_id:
                    indice = i
                    producto = p
                    break
            if producto is None:
                raise ProductoNoEncontrado(producto_id)

            async def verificar_habilitado():
                await asyncio.sleep(0.02)  # simula una consulta de verificacion
                if not producto.habilitado:
                    raise ProductoNoHabilitado(producto_id)

            async def verificar_stock():
                await asyncio.sleep(0.02)  # simula otra consulta de verificacion
                disponible = producto.stock - producto.stock_reservado
                if disponible < cantidad:
                    raise StockInsuficiente(producto_id, cantidad, disponible)

            try:
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(verificar_habilitado())
                    tg.create_task(verificar_stock())
            except* ErrorDominio as eg:
                raise eg.exceptions[0]

            datos = producto.model_dump()
            datos["stock"] = producto.stock - cantidad
            actualizado = Producto(**datos)
            self.productos[indice] = actualizado
            return actualizado