from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_categoria(nombre=None):
    if nombre is None:
        nombre = f"Cat {uuid.uuid4().hex[:8]}"
    r = client.post("/categorias/", json={"nombre": nombre})
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_categoria_crud():
    creado = _crear_categoria()
    cid = creado["id"]

    # listar
    r = client.get("/categorias/")
    assert r.status_code == 200
    assert any(c["id"] == cid for c in r.json())

    # obtener
    r = client.get(f"/categorias/{cid}")
    assert r.status_code == 200

    # actualizar
    r = client.put(f"/categorias/{cid}", json={"nombre": "Actualizada"})
    assert r.status_code in (200, 201)

    # eliminar
    r = client.delete(f"/categorias/{cid}")
    assert r.status_code in (200, 204)
