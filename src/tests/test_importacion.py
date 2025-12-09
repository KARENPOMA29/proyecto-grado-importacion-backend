from fastapi.testclient import TestClient
from src.main import app
import uuid
from datetime import date

client = TestClient(app)


def _crear_proveedor():
    nombre = f"Prov{uuid.uuid4().hex[:6]}"
    r = client.post("/proveedores/", json={"razonSocial": nombre, "telefono": "0", "encargado": "E", "direccion": "D", "ci": "111"})
    assert r.status_code in (200, 201)
    return r.json()


def test_importacion_crud():
    prov = _crear_proveedor()
    payload = {
        "codigo": f"IMP{uuid.uuid4().hex[:6]}",
        "proveedorId": prov["id"],
        "fechaLlegada": str(date.today()),
        "estado": "RECIBIDO",
        "observaciones": "none",
        "empleadoId": 1
    }
    r = client.post("/importaciones/", json=payload)
    assert r.status_code in (200, 201), r.text
    creado = r.json()
    iid = creado.get("id")

    r = client.get("/importaciones/")
    assert r.status_code == 200
    assert any(i.get("id") == iid for i in r.json())

    r = client.get(f"/importaciones/{iid}")
    assert r.status_code == 200

    r = client.put(f"/importaciones/{iid}", json={"estado": "PENDIENTE"})
    assert r.status_code in (200, 201)

    r = client.delete(f"/importaciones/{iid}")
    assert r.status_code in (200, 204)
