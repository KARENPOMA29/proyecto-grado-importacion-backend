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
        "rol": "vendedor",
        "usuario": nombre,
        "correo": f"{nombre}@test.com",
        "urlImagen": None,
        "contrasena": "secret123"
    }
    r = client.post("/empleados/", json=payload)
    assert r.status_code in (200, 201)
    return r.json()


def _crear_cliente():
    import random
    nombre = f"Cli{uuid.uuid4().hex[:6]}"
    payload = {"nombre": nombre, "apellido": "A", "segundoApellido": "B", "correo": f"{nombre}@t.com", "ci": str(random.randint(1000000,9999999))}
    r = client.post("/clientes/", json=payload)
    assert r.status_code in (200, 201)
    return r.json()


def _crear_sucursal():
    r = client.post("/sucursales/", json={"nombre": f"S{uuid.uuid4().hex[:6]}", "telefono": "0"})
    assert r.status_code in (200, 201)
    return r.json()


def _crear_categoria_modelo_producto():
    r1 = client.post("/categorias/", json={"nombre": f"C{uuid.uuid4().hex[:6]}"})
    assert r1.status_code in (200, 201)
    cat = r1.json()
    r2 = client.post("/modelos/", json={"nombreModelo": f"M{uuid.uuid4().hex[:6]}", "marca": "X", "capacidadOTamano": 1, "unidadMedida": "u", "stockMinimo": 0, "stockActual": 1})
    assert r2.status_code in (200, 201)
    mod = r2.json()
    r3 = client.post("/productos/", json={"numeroSerie": f"S{uuid.uuid4().hex[:8]}", "descripcion": "d", "precio": "1.00", "color": "C", "duracionGarantia": 0, "tipoGarantia": "N", "categoriaId": cat["id"], "modeloId": mod["id"], "importacionId": None})
    assert r3.status_code in (200, 201)
    prod = r3.json()
    return cat, mod, prod


def test_venta_crud():
    emp = _crear_empleado()
    cli = _crear_cliente()
    suc = _crear_sucursal()
    cat, mod, prod = _crear_categoria_modelo_producto()

    payload = {
        "empleadoId": emp["id"],
        "clienteId": cli["id"],
        "sucursalId": suc["id"],
        "codigoVenta": None,
        "detalles": [{"productoId": prod["id"], "subtotal": 1.0}]
    }
    r = client.post("/ventas/", json=payload)
    assert r.status_code in (200, 201), r.text
    creado = r.json()
    vid = creado.get("id")

    r = client.get("/ventas/")
    assert r.status_code == 200
    # buscar por id si el endpoint lo devuelve
    assert any(v.get("id") == vid for v in r.json())

    r = client.get(f"/ventas/{vid}")
    assert r.status_code == 200

    r = client.put(f"/ventas/{vid}/cancelar")
    assert r.status_code in (200, 201)
