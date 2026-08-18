"""Modelo: entidad Recipe y repositorio con persistencia en JSON."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "recetas.json"


@dataclass
class Recipe:
    nombre: str
    categoria: str
    ingredientes: list[str]
    pasos: list[str]
    tiempo_preparacion: int
    porciones: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    fecha_creacion: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Recipe:
        return cls(
            id=data["id"],
            nombre=data["nombre"],
            categoria=data["categoria"],
            ingredientes=list(data["ingredientes"]),
            pasos=list(data["pasos"]),
            tiempo_preparacion=data["tiempo_preparacion"],
            porciones=data["porciones"],
            fecha_creacion=data["fecha_creacion"],
        )


class RecipeRepository:
    """Maneja la carga/guardado en JSON y las operaciones CRUD sobre recetas."""

    def __init__(self, data_path: Path | str = DEFAULT_DATA_PATH):
        self.data_path = Path(data_path)
        self._recipes: list[Recipe] = self._load()

    def _load(self) -> list[Recipe]:
        if not self.data_path.exists():
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            self.data_path.write_text("[]", encoding="utf-8")
            return []
        raw = self.data_path.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        return [Recipe.from_dict(item) for item in json.loads(raw)]

    def _save(self) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [recipe.to_dict() for recipe in self._recipes]
        self.data_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def list_all(self) -> list[Recipe]:
        return list(self._recipes)

    def get_by_id(self, recipe_id: str) -> Recipe | None:
        return next((r for r in self._recipes if r.id == recipe_id), None)

    def add(self, recipe: Recipe) -> Recipe:
        self._recipes.append(recipe)
        self._save()
        return recipe

    def update(self, recipe_id: str, **campos) -> Recipe | None:
        recipe = self.get_by_id(recipe_id)
        if recipe is None:
            return None
        for clave, valor in campos.items():
            if valor is not None and hasattr(recipe, clave):
                setattr(recipe, clave, valor)
        self._save()
        return recipe

    def delete(self, recipe_id: str) -> bool:
        recipe = self.get_by_id(recipe_id)
        if recipe is None:
            return False
        self._recipes.remove(recipe)
        self._save()
        return True

    def search(self, texto: str) -> list[Recipe]:
        texto = texto.strip().lower()
        if not texto:
            return []
        resultado = []
        for r in self._recipes:
            if texto in r.nombre.lower() or any(
                texto in ing.lower() for ing in r.ingredientes
            ):
                resultado.append(r)
        return resultado

    def filter_by_category(self, categoria: str) -> list[Recipe]:
        categoria = categoria.strip().lower()
        return [r for r in self._recipes if r.categoria.lower() == categoria]

    def list_categories(self) -> list[str]:
        return sorted({r.categoria for r in self._recipes})
