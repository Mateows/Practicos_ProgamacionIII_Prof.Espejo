import asyncio
from typing import List, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from Producto import Producto, ProductoBase, ProductoCreate
from errores import ErrorDominio, ProductoNoEncontrado, ProductoNoHabilitado, StockInsuficiente



class ProductoRepositorio:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        # R4: el repositorio se crea una sola vez (en el lifespan) y recibe la
        # fabrica de sesiones, no una sesion: cada operacion abre la suya.
        self._session_factory = session_factory
        self._locks: dict[int, asyncio.Lock] = {}



    async def listar(self, offset: int, limit: int) -> Tuple[List[Producto], int]:
        """Devuelve (pagina de productos, total de registros en la tabla) (R8)."""
        await asyncio.sleep(0.05)
        async with self._session_factory() as session:
            total = (await session.exec(select(func.count()).select_from(Producto))).one()
            consulta = select(Producto).order_by(Producto.id).offset(offset).limit(limit)
            productos = (await session.exec(consulta)).all()
            return list(productos), total


    async def obtener_por_id(self, producto_id: int) -> Optional[Producto]:
        await asyncio.sleep(0.05)
        async with self._session_factory() as session:
            return await session.get(Producto, producto_id)


    async def crear(self, producto_in: ProductoCreate) -> Producto:
        await asyncio.sleep(0.05)
        async with self._session_factory() as session:
            nuevo_producto = Producto.model_validate(producto_in)
            session.add(nuevo_producto)
            await session.commit()
            await session.refresh(nuevo_producto)
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
        si lo envio explicito). Validar el estado completo con esos cambios contra
        ProductoBase vuelve a correr el @model_validator de stock sobre el estado final
        (Producto es table=True y SQLModel no valida al instanciarlo).

        Usa el mismo lock por producto que comprar(), para que un PATCH y una
        compra concurrentes sobre el mismo producto no se pisen entre si."""
        async with self._lock_de(producto_id):
            await asyncio.sleep(0.05)
            async with self._session_factory() as session:
                producto = await session.get(Producto, producto_id)
                if producto is None:
                    raise ProductoNoEncontrado(producto_id)

                datos = producto.model_dump(exclude={"id"})
                datos.update(cambios)
                validado = ProductoBase.model_validate(datos)  # lanza ValidationError si queda invalido

                for campo, valor in validado.model_dump().items():
                    setattr(producto, campo, valor)
                session.add(producto)
                await session.commit()
                await session.refresh(producto)
                return producto


    async def comprar(self, producto_id: int, cantidad: int) -> Producto:
        """R11: habilitado y stock se verifican concurrentemente con TaskGroup.
        R12: todo el ciclo verificar+descontar corre bajo un Lock por producto,
        para que dos compras del mismo producto no lean el mismo stock viejo
        y lo pisen (si el chequeo quedara afuera del lock, dos compras podrian
        pasar la verificacion antes de que cualquiera descuente, y sobrevenderiamos)."""
        lock = self._lock_de(producto_id)
        async with lock:
            await asyncio.sleep(0.05)
            async with self._session_factory() as session:
                producto = await session.get(Producto, producto_id)
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

                producto.stock = producto.stock - cantidad
                session.add(producto)
                await session.commit()
                await session.refresh(producto)
                return producto
