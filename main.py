"""Punto de entrada de la aplicación de recetas."""

from controllers.recipe_controller import RecipeController
from models.recipe import RecipeRepository


def main() -> None:
    repository = RecipeRepository()
    controller = RecipeController(repository)
    controller.run()


if __name__ == "__main__":
    main()
