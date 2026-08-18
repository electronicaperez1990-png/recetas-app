"""Punto de entrada de la aplicación web de recetas (Flask)."""

from pathlib import Path

from flask import Flask

from controllers.recipe_controller import recetas_bp
from models.recipe import RecipeRepository

DEFAULT_UPLOAD_FOLDER = Path(__file__).resolve().parent / "views" / "static" / "uploads"


def create_app(data_path=None, upload_folder=None) -> Flask:
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static",
    )
    app.config["SECRET_KEY"] = "recetas-app-dev-key"
    app.config["RECIPE_REPOSITORY"] = (
        RecipeRepository(data_path=data_path) if data_path else RecipeRepository()
    )
    app.config["UPLOAD_FOLDER"] = Path(upload_folder or DEFAULT_UPLOAD_FOLDER)
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.config["UPLOAD_FOLDER"].mkdir(parents=True, exist_ok=True)
    app.register_blueprint(recetas_bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
