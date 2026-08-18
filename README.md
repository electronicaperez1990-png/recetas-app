# recetas-app

Aplicación de recetas de cocina en consola, construida con arquitectura MVC
(Modelo-Vista-Controlador) en Python, usando `uv` como gestor de entorno y
dependencias.

## Estructura

```
recetas-app/
├── main.py                   # punto de entrada
├── models/recipe.py          # Recipe + RecipeRepository (persistencia JSON, CRUD, búsqueda/filtro)
├── views/console_view.py     # entrada/salida por consola
├── controllers/recipe_controller.py  # bucle del menú, conecta vista y modelo
├── data/recetas.json         # datos persistidos
└── tests/test_recipe_model.py  # tests unitarios del modelo
```

## Instalación

```bash
uv sync
```

## Ejecución

```bash
uv run main.py
```

## Tests

```bash
uv run pytest
```

## Funcionalidades

- Ver todas las recetas
- Ver el detalle de una receta
- Agregar una receta nueva
- Editar una receta existente
- Eliminar una receta
- Buscar recetas por nombre o ingrediente
- Filtrar recetas por categoría
