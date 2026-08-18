"""Punto de entrada de la aplicación web de recetas (Flask)."""

from flask import Flask

from controllers.recipe_controller import recetas_bp
from models.recipe import RecipeRepository


def create_app(data_path=None) -> Flask:
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )
    app.config["SECRET_KEY"] = "recetas-app-dev-key"
    app.config["RECIPE_REPOSITORY"] = (
        RecipeRepository(data_path=data_path) if data_path else RecipeRepository()
    )
    app.register_blueprint(recetas_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
