# src/tests/test_almacen.py (versión sincrónica)
from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_almacen(nombre=None, sucursal_id=1):
    # usar un nombre único por defecto para evitar colisiones con datos existentes
    if nombre is None:
        nombre = f"Depósito TEMP {uuid.uuid4().hex[:8]}"
    r = client.post("/almacenes/", json={"nombre": nombre, "sucursalId": sucursal_id})
    # aceptar 200 o 201 (el API a veces responde 200 con el recurso creado)
    assert r.status_code in (200, 201), r.text
    return r.json()  # dict con id, nombre, etc.

def test_actualizar_almacen_put():
    # 1) Crear
    # no usar un nombre fijo para evitar colisiones con datos existentes
    creado = _crear_almacen()
    almacen_id = creado["id"]

    # 2) Actualizar (PUT) – ajusta el body según tu esquema Update
    # usar nombre único para evitar colisiones
    new_name = f"Depósito ACTUALIZADO {uuid.uuid4().hex[:6]}"
    payload_update = {
        "nombre": new_name,
        "sucursalId": 1,
        "estado": 1
    }
    r_upd = client.put(f"/almacenes/{almacen_id}", json=payload_update)
    assert r_upd.status_code in (200, 204), r_upd.text

    # 3) Obtener y verificar cambios
    r_get = client.get("/almacenes/")
    assert r_get.status_code == 200
    data = r_get.json()
    # comprobar que el almacén actualizado tiene el nombre nuevo
    assert any(a["id"] == almacen_id and a["nombre"] == new_name for a in data)

def test_actualizar_almacen_inexistente_retorna_404():
    payload_update = {
        "nombre": "No existe",
        "sucursalId": 1,
        "estado": 1
    }
    r = client.put("/almacenes/999999", json=payload_update)
    assert r.status_code == 404

def test_listar_almacenes():
    # crear un almacén conocido y verificar que aparece en el listado
    creado = _crear_almacen(nombre=f"Deposito HOME {uuid.uuid4().hex[:6]}")
    r = client.get("/almacenes/")
    assert r.status_code == 200
    assert any(a["id"] == creado["id"] for a in r.json())

def test_eliminar_almacen():
    # crear y luego eliminar ese almacén
    creado = _crear_almacen()
    almacen_id = creado["id"]
    r = client.delete(f"/almacenes/{almacen_id}")
    assert r.status_code in [200, 204], r.text
    # verificar que ya no aparece en el listado
    r_get = client.get("/almacenes/")
    assert r_get.status_code == 200
    assert all(a["id"] != almacen_id for a in r_get.json())
