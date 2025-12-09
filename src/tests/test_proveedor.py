from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_proveedor():
    nombre = f"Prov {uuid.uuid4().hex[:6]}"
    payload = {
        "razonSocial": nombre,
        "telefono": "000",
        "encargado": "Enc",
        "direccion": "Dir",
        "ci": "123456"
    }
    r = client.post("/proveedores/", json=payload)
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_proveedor_crud():
    creado = _crear_proveedor()
    pid = creado["id"]

    r = client.get("/proveedores/")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json())

    r = client.get(f"/proveedores/{pid}")
    assert r.status_code == 200

    # obtener recurso completo y usarlo para update (evitar 422)
    r_get = client.get(f"/proveedores/{pid}")
    assert r_get.status_code == 200
    obj = r_get.json()
    obj["telefono"] = "111"
    r = client.put(f"/proveedores/{pid}", json=obj)
    assert r.status_code in (200, 201), r.text

    r = client.delete(f"/proveedores/{pid}")
    assert r.status_code in (200, 204)
