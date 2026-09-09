"""Tests del dominio Figura/Poligono/Lado (figuras.py).

Cubren los puntos centrales de las Partes 3 y 4 del TP: falla temprana de
la ABC, classmethod de lados_esperados, crear_regular, copia defensiva,
agregacion del Taller y duck typing via Protocol.
"""

import pytest

from figuras import (
    Cuadrado,
    Etiqueta,
    Hexagono,
    Lado,
    Pentagono,
    Poligono,
    Taller,
    Triangulo,
    crear_regular,
    exportar_todo,
)
from libreria_externa import PlanoCAD


def test_poligono_abstracto_no_se_puede_instanciar():
    """Falla temprana: Poligono es ABC, no se puede construir directamente."""
    with pytest.raises(TypeError):
        Poligono("x", "y")


def test_lados_esperados_es_classmethod():
    """lados_esperados() se puede consultar sobre la clase, sin instanciar."""
    assert Triangulo.lados_esperados() == 3
    assert Cuadrado.lados_esperados() == 4
    assert Pentagono.lados_esperados() == 5
    assert Hexagono.lados_esperados() == 6


def test_crear_regular_arma_poligono_con_lados_iguales():
    """crear_regular reemplaza a PoligonoRegular: usa la clase existente."""
    pentagono = crear_regular(Pentagono, medida=4, nombre="P", color="verde")
    assert isinstance(pentagono, Pentagono)
    assert len(pentagono.lados) == 5
    assert pentagono.perimetro() == 20


def test_lados_devuelve_copia_defensiva():
    """Modificar la tupla devuelta por .lados no debe afectar al Poligono."""
    triangulo = Triangulo("T", "rojo", [Lado(3), Lado(4), Lado(5)])
    copia = triangulo.lados
    assert copia == tuple(triangulo.lados)
    assert copia is not triangulo._lados


def test_taller_agregacion_poligono_sobrevive():
    """Agregacion: el Poligono sigue existiendo si el Taller desaparece."""
    cuadrado = Cuadrado("C", "azul", [Lado(2)] * 4)
    taller = Taller()
    taller.recibir(cuadrado)
    del taller
    assert cuadrado.perimetro() == 8


def test_exportar_todo_duck_typing_con_planocad():
    """exportar_todo funciona con Poligono y PlanoCAD en la misma lista."""
    triangulo = Triangulo("T", "rojo", [Lado(3), Lado(4), Lado(5)])
    plano = PlanoCAD("PLANO-01")
    resultado = exportar_todo([triangulo, plano])
    assert len(resultado) == 2
    assert "Triangulo" in resultado[0]
    assert "PlanoCAD" in resultado[1]


def test_etiqueta_es_inmutable():
    """Etiqueta es un @dataclass(frozen=True): no se puede modificar."""
    etiqueta = Etiqueta("borde norte")
    with pytest.raises(Exception):
        etiqueta.texto = "otro texto"