"""Controlador: conecta la vista con el modelo y maneja el flujo del menú."""

from __future__ import annotations

from models.recipe import Recipe, RecipeRepository
from views import console_view as view


class RecipeController:
    def __init__(self, repository: RecipeRepository):
        self.repository = repository

    def run(self) -> None:
        acciones = {
            "1": self.ver_todas,
            "2": self.ver_detalle,
            "3": self.agregar,
            "4": self.editar,
            "5": self.eliminar,
            "6": self.buscar,
            "7": self.filtrar_por_categoria,
        }
        while True:
            opcion = view.mostrar_menu()
            if opcion == "0":
                print("¡Hasta luego!")
                break
            accion = acciones.get(opcion)
            if accion is None:
                view.mostrar_mensaje("Opción inválida.", ok=False)
                continue
            accion()

    def _elegir_receta(self, recetas: list[Recipe]) -> Recipe | None:
        view.mostrar_lista(recetas)
        if not recetas:
            return None
        indice = view.elegir_indice(len(recetas))
        if indice is None:
            view.mostrar_mensaje("Selección inválida.", ok=False)
            return None
        return recetas[indice]

    def ver_todas(self) -> None:
        view.mostrar_lista(self.repository.list_all())

    def ver_detalle(self) -> None:
        receta = self._elegir_receta(self.repository.list_all())
        if receta:
            view.mostrar_detalle(receta)

    def agregar(self) -> None:
        datos = view.pedir_datos_receta()
        if not datos["nombre"]:
            view.mostrar_mensaje("El nombre es obligatorio. Se canceló.", ok=False)
            return
        receta = Recipe(**datos)
        self.repository.add(receta)
        view.mostrar_mensaje(f"Receta '{receta.nombre}' guardada.")

    def editar(self) -> None:
        receta = self._elegir_receta(self.repository.list_all())
        if not receta:
            return
        cambios = view.pedir_datos_edicion(receta)
        self.repository.update(receta.id, **cambios)
        view.mostrar_mensaje(f"Receta '{receta.nombre}' actualizada.")

    def eliminar(self) -> None:
        receta = self._elegir_receta(self.repository.list_all())
        if not receta:
            return
        if view.pedir_confirmacion(f"¿Eliminar '{receta.nombre}'?"):
            self.repository.delete(receta.id)
            view.mostrar_mensaje(f"Receta '{receta.nombre}' eliminada.")
        else:
            view.mostrar_mensaje("Eliminación cancelada.")

    def buscar(self) -> None:
        texto = view.pedir_texto("Buscar por nombre o ingrediente: ")
        resultados = self.repository.search(texto)
        view.mostrar_lista(resultados)

    def filtrar_por_categoria(self) -> None:
        categorias = self.repository.list_categories()
        if not categorias:
            view.mostrar_mensaje("No hay categorías registradas.", ok=False)
            return
        print("\nCategorías disponibles:")
        for i, cat in enumerate(categorias, start=1):
            print(f"  {i}. {cat}")
        indice = view.elegir_indice(len(categorias))
        if indice is None:
            view.mostrar_mensaje("Selección inválida.", ok=False)
            return
        resultados = self.repository.filter_by_category(categorias[indice])
        view.mostrar_lista(resultados)
