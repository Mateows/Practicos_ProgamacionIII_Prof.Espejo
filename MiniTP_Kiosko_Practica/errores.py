"""Excepciones de dominio del kiosco (R9).

En vez de usar HTTPException con un detail suelto, cada error del dominio es una
excepcion propia con un codigo estable y un status_code fijo. main.py registra un
exception_handler para ErrorDominio que las traduce a un JSON con formato propio,
en lugar del {"detail": "..."} por default de FastAPI.
"""


class ErrorDominio(Exception):
    codigo: str = "error_dominio"
    status_code: int = 400

    def __init__(self, mensaje: str):
        self.mensaje = mensaje
        super().__init__(mensaje)


class ProductoNoEncontrado(ErrorDominio):
    codigo = "producto_no_encontrado"
    status_code = 404

    def __init__(self, producto_id: int):
        super().__init__(f"No existe un producto con id {producto_id}")


class ProductoNoHabilitado(ErrorDominio):
    codigo = "producto_no_habilitado"
    status_code = 409

    def __init__(self, producto_id: int):
        super().__init__(f"El producto {producto_id} no esta habilitado para la venta")


class StockInsuficiente(ErrorDominio):
    codigo = "stock_insuficiente"
    status_code = 409

    def __init__(self, producto_id: int, solicitado: int, disponible: int):
        super().__init__(
            f"Stock insuficiente para el producto {producto_id}: "
            f"se pidieron {solicitado}, hay {disponible} disponibles"
        )
        self.solicitado = solicitado
        self.disponible = disponible
