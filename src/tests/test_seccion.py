from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_seccion(almacen_id, modelo_id):
    payload = {"almacenId": almacen_id, "modeloId": modelo_id, "descripcion": f"Sec {uuid.uuid4().hex[:6]}"}
    r = client.post("/secciones/", json=payload)
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_seccion_crud():
    # crear dependencias mínimas: almacen y modelo
    r_a = client.post("/almacenes/", json={"nombre": f"Alm {uuid.uuid4().hex[:6]}", "sucursalId": 1})
    assert r_a.status_code in (200, 201)
    almacen = r_a.json()

    r_m = client.post("/modelos/", json={
        "nombreModelo": f"M{uuid.uuid4().hex[:6]}", "marca": "X", "capacidadOTamano": 1,
        "unidadMedida": "u", "stockMinimo": 0, "stockActual": 1
    })
    assert r_m.status_code in (200, 201)
    modelo = r_m.json()

    creado = _crear_seccion(almacen["id"], modelo["id"])
    sid = creado["id"]

    r = client.get("/secciones/")
    assert r.status_code == 200
    assert any(s["id"] == sid for s in r.json())

    r = client.get(f"/secciones/{sid}")
    assert r.status_code == 200

    # usar representación completa para evitar 422
    r_get = client.get(f"/secciones/{sid}")
    assert r_get.status_code == 200
    obj = r_get.json()
    obj["descripcion"] = "Nueva"
    r = client.put(f"/secciones/{sid}", json=obj)
    assert r.status_code in (200, 201), r.text

    r = client.delete(f"/secciones/{sid}")
    assert r.status_code in (200, 204)
