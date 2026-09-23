"""Evidencia de R11/R12: dispara varias compras del MISMO producto al mismo
tiempo con asyncio.gather (no un for secuencial, que las desincroniza) y muestra
que el stock final queda consistente, sin condiciones de carrera.

Requiere el servidor corriendo:  uvicorn main:app --reload
"""

import asyncio

import httpx

BASE_URL = "http://127.0.0.1:8000"

STOCK_INICIAL = 10
CANTIDAD_POR_COMPRA = 2
COMPRAS_SIMULTANEAS = 6  # 6 x 2 = 12 unidades pedidas contra 10 de stock


async def crear_producto_de_prueba(client: httpx.AsyncClient) -> int:
    resp = await client.post(
        "/productos",
        json={
            "nombre": "Producto de prueba - concurrencia",
            "precio": "100.00",
            "stock": STOCK_INICIAL,
            "stock_reservado": 0,
            "habilitado": True,
            "categoria": "test",
        },
    )
    resp.raise_for_status()
    return resp.json()["id"]


async def comprar(client: httpx.AsyncClient, producto_id: int, etiqueta: str) -> None:
    resp = await client.post(
        f"/productos/{producto_id}/comprar",
        json={"cantidad": CANTIDAD_POR_COMPRA},
    )
    if resp.status_code == 200:
        print(f"[{etiqueta}] OK   -> stock restante: {resp.json()['stock']}")
    else:
        cuerpo = resp.json()
        print(f"[{etiqueta}] {resp.status_code} -> {cuerpo.get('error')}: {cuerpo.get('mensaje')}")


async def main() -> None:
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10) as client:
        producto_id = await crear_producto_de_prueba(client)
        print(f"Producto creado: id={producto_id}, stock inicial={STOCK_INICIAL}\n")

        tareas = [
            comprar(client, producto_id, f"compra-{i}")
            for i in range(1, COMPRAS_SIMULTANEAS + 1)
        ]
        await asyncio.gather(*tareas)

        resp = await client.get(f"/productos/{producto_id}")
        stock_final = resp.json()["stock"]
        print(f"\nStock final segun el servidor: {stock_final}")
        print(
            "Si no hubiera proteccion contra condiciones de carrera, dos compras "
            "podrian haber leido el mismo stock viejo y el resultado final no "
            "coincidiria con: stock_inicial - (compras exitosas x cantidad)."
        )


if __name__ == "__main__":
    asyncio.run(main())
