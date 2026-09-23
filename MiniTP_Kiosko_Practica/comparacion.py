"""R14: endpoints que muestran, con tiempos reales, la diferencia entre hacer
varias verificaciones una atras de la otra vs. concurrentemente.

Las "verificaciones" son simuladas (asyncio.sleep) a proposito, como si fueran
consultas a servicios externos (ej: verificar stock en un deposito, verificar un
medio de pago, etc.). Cada una tarda 0.1s, y son 3: secuencial da ~0.3s totales,
concurrente da ~0.1s.
"""

import asyncio
import time

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/comparacion", tags=["comparacion"])

DEMORA_POR_VERIFICACION = 0.1
CANTIDAD_VERIFICACIONES = 3


class ResultadoComparacion(BaseModel):
    resultados: list[str]
    duracion_ms: float


async def _verificacion_simulada(nombre: str) -> str:
    await asyncio.sleep(DEMORA_POR_VERIFICACION)
    return f"{nombre}: ok"


@router.get("/sincrono", response_model=ResultadoComparacion)
async def comparacion_sincrona():
    inicio = time.perf_counter()
    resultados = []
    for i in range(1, CANTIDAD_VERIFICACIONES + 1):
        resultado = await _verificacion_simulada(f"verificacion_{i}")
        resultados.append(resultado)
    duracion_ms = (time.perf_counter() - inicio) * 1000
    return ResultadoComparacion(resultados=resultados, duracion_ms=round(duracion_ms, 2))


@router.get("/asincrono", response_model=ResultadoComparacion)
async def comparacion_asincrona():
    inicio = time.perf_counter()
    async with asyncio.TaskGroup() as tg:
        tareas = [
            tg.create_task(_verificacion_simulada(f"verificacion_{i}"))
            for i in range(1, CANTIDAD_VERIFICACIONES + 1)
        ]
    resultados = [tarea.result() for tarea in tareas]
    duracion_ms = (time.perf_counter() - inicio) * 1000
    return ResultadoComparacion(resultados=resultados, duracion_ms=round(duracion_ms, 2))
