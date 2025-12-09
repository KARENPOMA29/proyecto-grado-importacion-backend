from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def _crear_empleado():
    nombre = f"Emp{uuid.uuid4().hex[:6]}"
    payload = {
        "nombre": nombre,
        "apellido": "Ap",
        "segundoApellido": "SA",
        "ci": "1234567",
        "telefono": "000",
        "rol": "admin",
        "usuario": nombre,
        "correo": f"{nombre}@test.com",
        "urlImagen": None,
        "contrasena": "secret123"
    }
    r = client.post("/empleados/", json=payload)
    assert r.status_code in (200, 201), r.text
    return r.json(), payload


def test_empleado_crud_and_login():
    creado, payload = _crear_empleado()
    eid = creado["id"]

    r = client.get("/empleados/")
    assert r.status_code == 200
    assert any(e["id"] == eid for e in r.json())

    r = client.get(f"/empleados/{eid}")
    assert r.status_code == 200

    # Para evitar 422, obtener la representación completa y modificarla
    r_get = client.get(f"/empleados/{eid}")
    assert r_get.status_code == 200
    obj = r_get.json()
    obj["telefono"] = "111"
    r = client.put(f"/empleados/{eid}", json=obj)
    assert r.status_code in (200, 201), r.text

    # login via auth endpoint (ruta con prefijo /auth)
    r = client.post("/auth/login", json={"usuario": payload["usuario"], "contrasena": payload["contrasena"]})
    assert r.status_code == 200, r.text

    r = client.delete(f"/empleados/{eid}")
    # delete may return message
    assert r.status_code in (200, 204)
