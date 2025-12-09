from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_sucursal(nombre=None):
    if nombre is None:
        nombre = f"Suc {uuid.uuid4().hex[:8]}"
    r = client.post("/sucursales/", json={"nombre": nombre, "telefono": "000-000"})
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_sucursal_crud():
    creado = _crear_sucursal()
    sid = creado["id"]

    r = client.get("/sucursales/")
    assert r.status_code == 200
    assert any(s["id"] == sid for s in r.json())

    r = client.get(f"/sucursales/{sid}")
    assert r.status_code == 200

    r = client.put(f"/sucursales/{sid}", json={"nombre": "Suc Act", "telefono": "111"})
    assert r.status_code in (200, 201)

    r = client.delete(f"/sucursales/{sid}")
    assert r.status_code in (200, 204)
