from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_modelo():
    r = client.post("/modelos/", json={
        "nombreModelo": f"M{uuid.uuid4().hex[:6]}", "marca": "X", "capacidadOTamano": 1,
        "unidadMedida": "u", "stockMinimo": 0, "stockActual": 1
    })
    assert r.status_code in (200, 201)
    return r.json()


def _crear_categoria():
    r = client.post("/categorias/", json={"nombre": f"C{uuid.uuid4().hex[:6]}"})
    assert r.status_code in (200, 201)
    return r.json()


def _crear_producto(cat_id, mod_id):
    payload = {
        "numeroSerie": f"S{uuid.uuid4().hex[:8]}",
        "descripcion": "Desc",
        "precio": "5.00",
        "color": "N",
        "duracionGarantia": 6,
        "tipoGarantia": "M",
        "categoriaId": cat_id,
        "modeloId": mod_id,
        "importacionId": None
    }
    r = client.post("/productos/", json=payload)
    assert r.status_code in (200, 201)
    return r.json()


def test_movimiento_crud():
    mod = _crear_modelo()
    cat = _crear_categoria()
    prod = _crear_producto(cat["id"], mod["id"])

    # crear almacen mínimo
    r = client.post("/almacenes/", json={"nombre": f"Alm{uuid.uuid4().hex[:6]}", "sucursalId": 1})
    assert r.status_code in (200, 201)
    almacen = r.json()

    payload = {"productoId": prod["id"], "almacenId": almacen["id"], "tipoMovimiento": "INGRESO"}
    r = client.post("/movimientos/", json=payload)
    assert r.status_code in (200, 201), r.text
    creado = r.json()
    mid = creado["id"]

    r = client.get("/movimientos/")
    assert r.status_code == 200
    assert any(m["id"] == mid for m in r.json())

    r = client.get(f"/movimientos/{mid}")
    assert r.status_code == 200

    r = client.put(f"/movimientos/{mid}", json={"tipoMovimiento": "SALIDA"})
    assert r.status_code in (200, 201)

    r = client.delete(f"/movimientos/{mid}")
    assert r.status_code in (200, 204)
