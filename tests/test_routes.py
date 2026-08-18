import io

import pytest

from app import create_app
from models.recipe import Recipe


@pytest.fixture
def client(tmp_path):
    app = create_app(
        data_path=tmp_path / "recetas.json",
        upload_folder=tmp_path / "uploads",
    )
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


def test_agregar_receta_con_imagen(client):
    test_client, repo = client
    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    resp = test_client.post(
        "/recetas/nueva",
        data={
            "nombre": "Tarta de manzana",
            "categoria": "postre",
            "ingredientes": "manzana\nharina",
            "pasos": "Cortar.\nHornear.",
            "tiempo_preparacion": "50",
            "porciones": "6",
            "imagen": (io.BytesIO(b"contenido falso de imagen"), "tarta.jpg"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    receta = next(r for r in repo.list_all() if r.nombre == "Tarta de manzana")
    assert receta.imagen is not None
    assert (upload_folder / receta.imagen).exists()


def test_agregar_receta_con_extension_invalida(client):
    test_client, repo = client
    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    resp = test_client.post(
        "/recetas/nueva",
        data={
            "nombre": "Receta con archivo raro",
            "categoria": "postre",
            "ingredientes": "algo",
            "pasos": "hacer algo",
            "tiempo_preparacion": "5",
            "porciones": "1",
            "imagen": (io.BytesIO(b"no es una imagen"), "notas.txt"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    assert resp.status_code == 200
    receta = next(r for r in repo.list_all() if r.nombre == "Receta con archivo raro")
    assert receta.imagen is None
    assert list(upload_folder.glob("*")) == []


def test_editar_receta_reemplaza_imagen(client):
    test_client, repo = client
    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    receta_id = repo.list_all()[0].id

    test_client.post(
        f"/recetas/{receta_id}/editar",
        data={
            "nombre": "Pasta al tomate",
            "categoria": "plato fuerte",
            "ingredientes": "pasta\ntomate",
            "pasos": "Cocinar.",
            "tiempo_preparacion": "25",
            "porciones": "2",
            "imagen": (io.BytesIO(b"foto original"), "original.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    imagen_original = repo.get_by_id(receta_id).imagen
    assert (upload_folder / imagen_original).exists()

    test_client.post(
        f"/recetas/{receta_id}/editar",
        data={
            "nombre": "Pasta al tomate",
            "categoria": "plato fuerte",
            "ingredientes": "pasta\ntomate",
            "pasos": "Cocinar.",
            "tiempo_preparacion": "25",
            "porciones": "2",
            "imagen": (io.BytesIO(b"foto nueva"), "nueva.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    imagen_nueva = repo.get_by_id(receta_id).imagen
    assert imagen_nueva != imagen_original
    assert (upload_folder / imagen_nueva).exists()
    assert not (upload_folder / imagen_original).exists()


def test_eliminar_receta_borra_imagen(client):
    test_client, repo = client
    upload_folder = test_client.application.config["UPLOAD_FOLDER"]
    receta_id = repo.list_all()[0].id

    test_client.post(
        f"/recetas/{receta_id}/editar",
        data={
            "nombre": "Pasta al tomate",
            "categoria": "plato fuerte",
            "ingredientes": "pasta\ntomate",
            "pasos": "Cocinar.",
            "tiempo_preparacion": "25",
            "porciones": "2",
            "imagen": (io.BytesIO(b"foto"), "foto.png"),
        },
        content_type="multipart/form-data",
        follow_redirects=True,
    )
    imagen = repo.get_by_id(receta_id).imagen
    assert (upload_folder / imagen).exists()

    test_client.post(f"/recetas/{receta_id}/eliminar", follow_redirects=True)
    assert not (upload_folder / imagen).exists()
