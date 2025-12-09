from fastapi.testclient import TestClient
from src.main import app
import uuid
from random import randint

client = TestClient(app)


def _crear_cliente():
    nombre = f"Cli{uuid.uuid4().hex[:6]}"
    payload = {
        "nombre": nombre,
        "apellido": "Ap",
        "segundoApellido": "SA",
        "correo": f"{nombre}@test.com",
        "ci": str(randint(1000000, 9999999))
    }
    r = client.post("/clientes/", json=payload)
    assert r.status_code in (200, 201), r.text
    return r.json()


def test_cliente_crud():
    creado = _crear_cliente()
    cid = creado["id"]

    r = client.get("/clientes/")
    assert r.status_code == 200
    assert any(c["id"] == cid for c in r.json())

    r = client.get(f"/clientes/{cid}")
    assert r.status_code == 200

    # obtener el recurso completo y usar su representación como base para update
    r_get = client.get(f"/clientes/{cid}")
    assert r_get.status_code == 200
    obj = r_get.json()
    obj["apellido"] = "Nuevo"
    r = client.put(f"/clientes/{cid}", json=obj)
    assert r.status_code in (200, 201), r.text

    r = client.delete(f"/clientes/{cid}")
    assert r.status_code in (200, 204)
