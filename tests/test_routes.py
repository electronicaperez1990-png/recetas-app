import pytest

from app import create_app
from models.recipe import Recipe


@pytest.fixture
def client(tmp_path):
    app = create_app(data_path=tmp_path / "recetas.json")
    app.testing = True
    repo = app.config["RECIPE_REPOSITORY"]
    repo.add(
        Recipe(
            nombre="Pasta al tomate",
            categoria="plato fuerte",
            ingredientes=["pasta", "tomate", "ajo"],
            pasos=["Cocinar la pasta.", "Preparar la salsa.", "Mezclar."],
            tiempo_preparacion=25,
            porciones=2,
        )
    )
    with app.test_client() as test_client:
        yield test_client, repo


def test_index_muestra_recetas(client):
    test_client, _ = client
    resp = test_client.get("/")
    assert resp.status_code == 200
    assert b"Pasta al tomate" in resp.data


def test_detalle_receta(client):
    test_client, repo = client
    receta_id = repo.list_all()[0].id
    resp = test_client.get(f"/recetas/{receta_id}")
    assert resp.status_code == 200
    assert b"Cocinar la pasta." in resp.data


def test_detalle_receta_inexistente_redirige(client):
    test_client, _ = client
    resp = test_client.get("/recetas/no-existe", follow_redirects=True)
    assert resp.status_code == 200
    assert "no encontrada".encode() in resp.data.lower() or b"Receta no encontrada" in resp.data


def test_agregar_receta(client):
    test_client, repo = client
    resp = test_client.post(
        "/recetas/nueva",
        data={
            "nombre": "Ensalada verde",
            "categoria": "entrada",
            "ingredientes": "lechuga\npepino",
            "pasos": "Lavar y cortar.\nMezclar.",
            "tiempo_preparacion": "10",
            "porciones": "2",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert any(r.nombre == "Ensalada verde" for r in repo.list_all())


def test_editar_receta(client):
    test_client, repo = client
    receta_id = repo.list_all()[0].id
    resp = test_client.post(
        f"/recetas/{receta_id}/editar",
        data={
            "nombre": "Pasta al pesto",
            "categoria": "plato fuerte",
            "ingredientes": "pasta\npesto",
            "pasos": "Cocinar.\nMezclar con pesto.",
            "tiempo_preparacion": "20",
            "porciones": "2",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert repo.get_by_id(receta_id).nombre == "Pasta al pesto"


def test_eliminar_receta(client):
    test_client, repo = client
    receta_id = repo.list_all()[0].id
    resp = test_client.post(f"/recetas/{receta_id}/eliminar", follow_redirects=True)
    assert resp.status_code == 200
    assert repo.get_by_id(receta_id) is None


def test_buscar(client):
    test_client, _ = client
    resp = test_client.get("/buscar?q=tomate")
    assert resp.status_code == 200
    assert b"Pasta al tomate" in resp.data


def test_filtrar_por_categoria(client):
    test_client, _ = client
    resp = test_client.get("/categoria/plato fuerte")
    assert resp.status_code == 200
    assert b"Pasta al tomate" in resp.data
