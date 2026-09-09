from figuras import (
    Cuadrado,
    Etiqueta,
    Exportable,
    Hexagono,
    Lado,
    Pentagono,
    Poligono,
    Taller,
    Triangulo,
    exportar_todo,
)
from libreria_externa import PlanoCAD

print("=" * 60)
print("1. Armando el taller con 4 polígonos")
print("=" * 60)

taller = Taller()

triangulo = Triangulo("Triangulo", "rojo", [Lado(3), Lado(4), Lado(5)])
cuadrado = Cuadrado("Cuadrado", "azul", [Lado(2), Lado(2), Lado(2), Lado(2)])
pentagono = Pentagono("Pentagono", "verde", [Lado(4)] * 5)
hexagono = Hexagono("Hexagono", "amarillo", [Lado(3)] * 6)

for figura in (triangulo, cuadrado, pentagono, hexagono):
    taller.recibir(figura)
    print(f"Recibido: {figura.exportar()}")

print()
print("=" * 60)
print("2. Etiquetando lados")
print("=" * 60)

primer_lado_triangulo = triangulo.lados[0]
primer_lado_cuadrado = cuadrado.lados[0]

etiqueta_triangulo = Etiqueta("hipotenusa aproximada")
etiqueta_cuadrado = Etiqueta("borde norte")
primer_lado_triangulo.etiqueta = etiqueta_triangulo
primer_lado_cuadrado.etiqueta = etiqueta_cuadrado

print(f"Lado del triángulo etiquetado como: {etiqueta_triangulo.texto}")
print(f"Lado del cuadrado etiquetado como: {etiqueta_cuadrado.texto}")

print()
print("=" * 60)
print("3. Exportando todo junto con un PlanoCAD (duck typing)")
print("=" * 60)

plano = PlanoCAD("PLANO-TALLER-01")
items_a_exportar: list[Exportable] = list(taller.inventario()) + [plano]

for linea in exportar_todo(items_a_exportar):
    print(linea)

print()
print("=" * 60)
print("4. Inventario del taller")
print("=" * 60)

for poligono in taller.inventario():
    print(f"- {poligono.nombre} ({poligono.lados_esperados()} lados)")

print()
print("=" * 60)
print("5. Demostrando las decisiones de diseño")
print("*" * 100)

# --- Agregación: Taller -- Poligono ---
# El Poligono sigue existiendo aunque el Taller desaparezca.
poligono_de_prueba = Cuadrado("Testigo", "gris", [Lado(1), Lado(1), Lado(1), Lado(1)])
taller_temporal = Taller()
taller_temporal.recibir(poligono_de_prueba)
del taller_temporal
print(f"Agregación: el Taller se borró, pero el Poligono sigue vivo -> {poligono_de_prueba.exportar()}")
print("*" * 100)

# --- Composición: Poligono -- Lado ---
# Los Lado no existen fuera de su Poligono: no hay forma de "sacarlos"
# y conservarlos independientemente, porque Poligono los crea y los guarda
# como parte de sí mismo (copia defensiva en .lados, no la lista real).
copia_lados = poligono_de_prueba.lados
del poligono_de_prueba
print(f"Composición: aunque tengamos una copia de los Lado ({len(copia_lados)} de ellos), "
      f"ya no hay Poligono que los sostenga como conjunto propio; nacieron y viven atados a él.")
print("*" * 100)

# --- Falla temprana: Poligono es ABC ---
print("Falla temprana: instanciar Poligono directamente sin lados_esperados()...")
print("*" * 100)
try:
    Poligono("x", "y")  # type: ignore[abstract]  # intencional: demuestra la falla temprana
except TypeError as error:
    print(f"  -> TypeError esperado: {error}")
print("*" * 100)