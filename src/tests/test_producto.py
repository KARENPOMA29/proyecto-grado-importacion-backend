from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_categoria():
    r = client.post("/categorias/", json={"nombre": f"C{uuid.uuid4().hex[:6]}"})
    assert r.status_code in (200, 201)
    return r.json()


def _crear_modelo():
    r = client.post("/modelos/", json={
        "nombreModelo": f"M{uuid.uuid4().hex[:6]}", "marca": "X", "capacidadOTamano": 1,
        "unidadMedida": "u", "stockMinimo": 0, "stockActual": 1
    })
    assert r.status_code in (200, 201)
    return r.json()


def test_producto_crud():
    cat = _crear_categoria()
    mod = _crear_modelo()

    payload = {
        "numeroSerie": f"S{uuid.uuid4().hex[:8]}",
        "descripcion": "Desc",
        "precio": "10.00",
        "color": "Rojo",
        "duracionGarantia": 12,
        "tipoGarantia": "M",
        "categoriaId": cat["id"],
        "modeloId": mod["id"],
        "importacionId": None
    }
    r = client.post("/productos/", json=payload)
    assert r.status_code in (200, 201), r.text
    creado = r.json()
    pid = creado["id"]

    r = client.get("/productos/")
    assert r.status_code == 200
    assert any(p["id"] == pid for p in r.json())

    r = client.get(f"/productos/{pid}")
    assert r.status_code == 200

    r = client.put(f"/productos/{pid}", json={"descripcion": "New"})
    assert r.status_code in (200, 201)

    r = client.delete(f"/productos/{pid}")
    assert r.status_code in (200, 204)
