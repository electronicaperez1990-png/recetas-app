"""Controlador: rutas Flask que conectan las plantillas (vista) con el modelo."""

from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from models.recipe import Recipe

recetas_bp = Blueprint("recetas", __name__)


def _repository():
    return current_app.config["RECIPE_REPOSITORY"]


def _datos_formulario() -> dict:
    ingredientes = [
        linea.strip()
        for linea in request.form.get("ingredientes", "").splitlines()
        if linea.strip()
    ]
    pasos = [
        linea.strip()
        for linea in request.form.get("pasos", "").splitlines()
        if linea.strip()
    ]
    return {
        "nombre": request.form.get("nombre", "").strip(),
        "categoria": request.form.get("categoria", "").strip(),
        "ingredientes": ingredientes,
        "pasos": pasos,
        "tiempo_preparacion": int(request.form.get("tiempo_preparacion") or 0),
        "porciones": int(request.form.get("porciones") or 0),
    }


@recetas_bp.route("/")
def index():
    repo = _repository()
    return render_template(
        "index.html",
        recetas=repo.list_all(),
        categorias=repo.list_categories(),
    )


@recetas_bp.route("/recetas/<receta_id>")
def detalle(receta_id: str):
    receta = _repository().get_by_id(receta_id)
    if receta is None:
        flash("Receta no encontrada.", "error")
        return redirect(url_for("recetas.index"))
    return render_template("detalle.html", receta=receta)


@recetas_bp.route("/recetas/nueva", methods=["GET", "POST"])
def nueva_receta():
    if request.method == "POST":
        datos = _datos_formulario()
        if not datos["nombre"] or not datos["categoria"]:
            flash("Nombre y categoría son obligatorios.", "error")
            return render_template("formulario.html", titulo="Nueva receta", receta=None)
        receta = _repository().add(Recipe(**datos))
        flash(f"Receta '{receta.nombre}' guardada.", "ok")
        return redirect(url_for("recetas.detalle", receta_id=receta.id))
    return render_template("formulario.html", titulo="Nueva receta", receta=None)


@recetas_bp.route("/recetas/<receta_id>/editar", methods=["GET", "POST"])
def editar_receta(receta_id: str):
    repo = _repository()
    receta = repo.get_by_id(receta_id)
    if receta is None:
        flash("Receta no encontrada.", "error")
        return redirect(url_for("recetas.index"))

    if request.method == "POST":
        datos = _datos_formulario()
        if not datos["nombre"] or not datos["categoria"]:
            flash("Nombre y categoría son obligatorios.", "error")
            return render_template("formulario.html", titulo="Editar receta", receta=receta)
        repo.update(receta_id, **datos)
        flash(f"Receta '{datos['nombre']}' actualizada.", "ok")
        return redirect(url_for("recetas.detalle", receta_id=receta_id))

    return render_template("formulario.html", titulo="Editar receta", receta=receta)


@recetas_bp.route("/recetas/<receta_id>/eliminar", methods=["POST"])
def eliminar_receta(receta_id: str):
    repo = _repository()
    receta = repo.get_by_id(receta_id)
    if receta and repo.delete(receta_id):
        flash(f"Receta '{receta.nombre}' eliminada.", "ok")
    else:
        flash("Receta no encontrada.", "error")
    return redirect(url_for("recetas.index"))


@recetas_bp.route("/buscar")
def buscar():
    repo = _repository()
    query = request.args.get("q", "").strip()
    recetas = repo.search(query) if query else []
    return render_template(
        "index.html",
        recetas=recetas,
        categorias=repo.list_categories(),
        query=query,
        titulo_seccion=f"Resultados para \"{query}\"" if query else None,
    )


@recetas_bp.route("/categoria/<nombre>")
def por_categoria(nombre: str):
    repo = _repository()
    return render_template(
        "index.html",
        recetas=repo.filter_by_category(nombre),
        categorias=repo.list_categories(),
        titulo_seccion=f"Categoría: {nombre}",
    )
