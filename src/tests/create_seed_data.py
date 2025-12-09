from fastapi.testclient import TestClient
from src.main import app
from datetime import date
import uuid

client = TestClient(app)


def create_basic_seed():
    out = {}

    # crear sucursal
    r = client.post("/sucursales/", json={"nombre": f"SeedSuc {uuid.uuid4().hex[:6]}", "telefono": "000"})
    if r.status_code in (200, 201):
        out['sucursal'] = r.json()

    # crear categoria
    r = client.post("/categorias/", json={"nombre": f"SeedCat {uuid.uuid4().hex[:6]}"})
    if r.status_code in (200, 201):
        out['categoria'] = r.json()

    # crear modelo
    r = client.post("/modelos/", json={
        "nombreModelo": f"SeedMod {uuid.uuid4().hex[:6]}",
        "marca": "Seed",
        "capacidadOTamano": 1,
        "unidadMedida": "u",
        "stockMinimo": 0,
        "stockActual": 10
    })
    if r.status_code in (200, 201):
        out['modelo'] = r.json()

    # crear proveedor
    r = client.post("/proveedores/", json={"razonSocial": f"SeedProv {uuid.uuid4().hex[:6]}", "telefono": "0", "encargado": "E", "direccion": "D", "ci": "111"})
    if r.status_code in (200, 201):
        out['proveedor'] = r.json()

    # crear empleado (no enviará correo en TESTING)
    nombre = f"SeedEmp{uuid.uuid4().hex[:6]}"
    r = client.post("/empleados/", json={
        "nombre": nombre,
        "apellido": "Ap",
        "segundoApellido": "SA",
        "ci": "9999999",
        "telefono": "000",
        "rol": "admin",
        "usuario": nombre,
        "correo": f"{nombre}@test.com",
        "urlImagen": None,
        "contrasena": "seedpass123"
    })
    if r.status_code in (200, 201):
        out['empleado'] = r.json()

    print("Seed creado:")
    for k, v in out.items():
        print(k, v.get('id'))

    return out


if __name__ == "__main__":
    create_basic_seed()
