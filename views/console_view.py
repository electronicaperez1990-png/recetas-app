"""Vista: entrada/salida por consola. No contiene lógica de negocio."""

from __future__ import annotations

from models.recipe import Recipe

MENU = """
=== App de Recetas ===
1. Ver todas las recetas
2. Ver detalle de una receta
3. Agregar nueva receta
4. Editar receta
5. Eliminar receta
6. Buscar recetas (nombre/ingrediente)
7. Filtrar por categoría
0. Salir
"""


def mostrar_menu() -> str:
    print(MENU)
    return input("Elige una opción: ").strip()


def mostrar_mensaje(texto: str, ok: bool = True) -> None:
    simbolo = "✔" if ok else "✖"
    print(f"{simbolo} {texto}")


def mostrar_lista(recetas: list[Recipe]) -> None:
    if not recetas:
        print("No hay recetas para mostrar.")
        return
    print(f"\n{'#':<4}{'Nombre':<30}{'Categoría':<20}{'Tiempo':<10}{'Porciones':<10}")
    print("-" * 74)
    for i, r in enumerate(recetas, start=1):
        print(
            f"{i:<4}{r.nombre:<30}{r.categoria:<20}"
            f"{str(r.tiempo_preparacion) + ' min':<10}{r.porciones:<10}"
        )


def mostrar_detalle(receta: Recipe) -> None:
    print(f"\n--- {receta.nombre} ---")
    print(f"Categoría: {receta.categoria}")
    print(f"Tiempo de preparación: {receta.tiempo_preparacion} min")
    print(f"Porciones: {receta.porciones}")
    print(f"Creada: {receta.fecha_creacion}")
    print("\nIngredientes:")
    for ing in receta.ingredientes:
        print(f"  - {ing}")
    print("\nPasos:")
    for i, paso in enumerate(receta.pasos, start=1):
        print(f"  {i}. {paso}")


def pedir_lineas(etiqueta: str) -> list[str]:
    print(f"Ingresa {etiqueta} (una por línea, línea vacía para terminar):")
    lineas = []
    while True:
        linea = input("  > ").strip()
        if not linea:
            break
        lineas.append(linea)
    return lineas


def pedir_datos_receta() -> dict:
    nombre = input("Nombre de la receta: ").strip()
    categoria = input("Categoría (ej. postre, plato fuerte, bebida): ").strip()
    ingredientes = pedir_lineas("los ingredientes")
    pasos = pedir_lineas("los pasos de preparación")
    tiempo_preparacion = _pedir_entero("Tiempo de preparación (minutos): ")
    porciones = _pedir_entero("Porciones: ")
    return {
        "nombre": nombre,
        "categoria": categoria,
        "ingredientes": ingredientes,
        "pasos": pasos,
        "tiempo_preparacion": tiempo_preparacion,
        "porciones": porciones,
    }


def pedir_datos_edicion(receta: Recipe) -> dict:
    print("Deja en blanco un campo para conservar el valor actual.")
    nombre = input(f"Nombre [{receta.nombre}]: ").strip()
    categoria = input(f"Categoría [{receta.categoria}]: ").strip()

    print("Ingredientes actuales:")
    for ing in receta.ingredientes:
        print(f"  - {ing}")
    if input("¿Reemplazar ingredientes? (s/n): ").strip().lower() == "s":
        ingredientes = pedir_lineas("los nuevos ingredientes")
    else:
        ingredientes = None

    print("Pasos actuales:")
    for paso in receta.pasos:
        print(f"  - {paso}")
    if input("¿Reemplazar pasos? (s/n): ").strip().lower() == "s":
        pasos = pedir_lineas("los nuevos pasos")
    else:
        pasos = None

    tiempo_raw = input(
        f"Tiempo de preparación [{receta.tiempo_preparacion}]: "
    ).strip()
    porciones_raw = input(f"Porciones [{receta.porciones}]: ").strip()

    return {
        "nombre": nombre or None,
        "categoria": categoria or None,
        "ingredientes": ingredientes,
        "pasos": pasos,
        "tiempo_preparacion": int(tiempo_raw) if tiempo_raw.isdigit() else None,
        "porciones": int(porciones_raw) if porciones_raw.isdigit() else None,
    }


def pedir_texto(mensaje: str) -> str:
    return input(mensaje).strip()


def pedir_confirmacion(mensaje: str) -> bool:
    return input(f"{mensaje} (s/n): ").strip().lower() == "s"


def elegir_indice(cantidad: int, mensaje: str = "Elige un número: ") -> int | None:
    valor = input(mensaje).strip()
    if not valor.isdigit():
        return None
    indice = int(valor) - 1
    if 0 <= indice < cantidad:
        return indice
    return None


def _pedir_entero(mensaje: str) -> int:
    while True:
        valor = input(mensaje).strip()
        if valor.isdigit():
            return int(valor)
        print("Por favor ingresa un número entero válido.")
