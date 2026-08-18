import pytest

from models.recipe import Recipe, RecipeRepository


@pytest.fixture
def repo(tmp_path):
    return RecipeRepository(data_path=tmp_path / "recetas.json")


def _receta(nombre="Pasta", categoria="plato fuerte", ingrediente="tomate"):
    return Recipe(
        nombre=nombre,
        categoria=categoria,
        ingredientes=[ingrediente, "sal"],
        pasos=["Cocinar la pasta.", "Agregar la salsa."],
        tiempo_preparacion=20,
        porciones=2,
    )


def test_repositorio_vacio_crea_archivo(tmp_path):
    data_path = tmp_path / "recetas.json"
    RecipeRepository(data_path=data_path)
    assert data_path.exists()
    assert data_path.read_text(encoding="utf-8").strip() == "[]"


def test_agregar_y_listar(repo):
    receta = _receta()
    repo.add(receta)
    todas = repo.list_all()
    assert len(todas) == 1
    assert todas[0].nombre == "Pasta"


def test_persistencia_entre_instancias(tmp_path):
    data_path = tmp_path / "recetas.json"
    repo1 = RecipeRepository(data_path=data_path)
    repo1.add(_receta())

    repo2 = RecipeRepository(data_path=data_path)
    assert len(repo2.list_all()) == 1
    assert repo2.list_all()[0].nombre == "Pasta"


def test_get_by_id(repo):
    receta = repo.add(_receta())
    encontrada = repo.get_by_id(receta.id)
    assert encontrada is not None
    assert encontrada.id == receta.id
    assert repo.get_by_id("id-inexistente") is None


def test_actualizar_receta(repo):
    receta = repo.add(_receta())
    actualizada = repo.update(receta.id, nombre="Pasta al pesto", porciones=4)
    assert actualizada.nombre == "Pasta al pesto"
    assert actualizada.porciones == 4
    assert actualizada.categoria == "plato fuerte"  # no cambiado, se conserva


def test_actualizar_receta_inexistente(repo):
    assert repo.update("id-inexistente", nombre="X") is None


def test_eliminar_receta(repo):
    receta = repo.add(_receta())
    assert repo.delete(receta.id) is True
    assert repo.list_all() == []
    assert repo.delete(receta.id) is False


def test_buscar_por_nombre_e_ingrediente(repo):
    repo.add(_receta(nombre="Pasta al tomate", ingrediente="tomate"))
    repo.add(_receta(nombre="Ensalada", ingrediente="lechuga"))

    assert len(repo.search("pasta")) == 1
    assert len(repo.search("tomate")) == 1
    assert len(repo.search("lechuga")) == 1
    assert len(repo.search("inexistente")) == 0


def test_filtrar_por_categoria(repo):
    repo.add(_receta(categoria="postre"))
    repo.add(_receta(categoria="plato fuerte"))

    resultado = repo.filter_by_category("postre")
    assert len(resultado) == 1
    assert resultado[0].categoria == "postre"


def test_list_categories(repo):
    repo.add(_receta(categoria="postre"))
    repo.add(_receta(categoria="plato fuerte"))
    repo.add(_receta(categoria="postre"))

    assert repo.list_categories() == ["plato fuerte", "postre"]
