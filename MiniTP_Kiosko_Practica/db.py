import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


# La URL (con la contraseña) se lee de la variable de entorno DATABASE_URL, asi no
# queda ninguna credencial real en el codigo. El valor por defecto es solo un
# placeholder: sin la variable seteada, el server no va a poder conectarse.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://USUARIO:PASSWORD@localhost:5432/kiosco_db",
)

engine = create_async_engine(DATABASE_URL, echo=False)

# expire_on_commit=False: despues del commit los objetos siguen teniendo sus
# atributos cargados, asi FastAPI puede serializarlos sin volver a la base.
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def crear_tablas() -> None:
    # Importar Producto registra la tabla en SQLModel.metadata antes del create_all.
    import Producto  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
