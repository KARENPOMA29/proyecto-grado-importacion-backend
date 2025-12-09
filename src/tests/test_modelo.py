from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_modelo():
    nombre = f"Mod {uuid.uuid4().hex[:6]}"
    payload = {
        "nombreModelo": nombre,
        "marca": "Marca",
        "capacidadOTamano": 10,
        "unidadMedida": "u",
        "stockMinimo": 1,
        "stockActual": 5
    }
    r = client.post("/modelos/", json=payload)
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_modelo_crud():
    creado = _crear_modelo()
    mid = creado["id"]

    r = client.get("/modelos/")
    assert r.status_code == 200
    assert any(m["id"] == mid for m in r.json())

    r = client.get(f"/modelos/{mid}")
    assert r.status_code == 200

    # usar la representación completa para evitar 422
    r_get = client.get(f"/modelos/{mid}")
    assert r_get.status_code == 200
    obj = r_get.json()
    obj["marca"] = "M2"
    r = client.put(f"/modelos/{mid}", json=obj)
    assert r.status_code in (200, 201), r.text

    r = client.delete(f"/modelos/{mid}")
    assert r.status_code in (200, 204)
