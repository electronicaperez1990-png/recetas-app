# recetas-app

Aplicación web de recetas de cocina, construida con arquitectura MVC
(Modelo-Vista-Controlador) en Python usando Flask, con `uv` como gestor de
entorno y dependencias.

## Estructura

```
recetas-app/
├── app.py                             # punto de entrada (Flask)
├── models/recipe.py                   # Recipe + RecipeRepository (persistencia JSON, CRUD, búsqueda/filtro)
├── controllers/recipe_controller.py   # Blueprint con las rutas, conecta vistas y modelo
├── views/
│   ├── templates/                     # plantillas Jinja2 (vista)
│   └── static/style.css               # estilos
├── data/recetas.json                  # datos persistidos
└── tests/
    ├── test_recipe_model.py           # tests unitarios del modelo
    └── test_routes.py                 # tests de integración de las rutas
```

## Instalación

```bash
uv sync
```

## Ejecución

```bash
uv run app.py
```

Abre **http://127.0.0.1:5000** en el navegador.

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
