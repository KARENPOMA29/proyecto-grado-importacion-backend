from fastapi.testclient import TestClient
from src.main import app
import uuid

client = TestClient(app)


def test_recuperar_password_and_login():
    # crear empleado para probar login/recuperar
    nombre = f"EmpAuth{uuid.uuid4().hex[:6]}"
    payload = {
        "nombre": nombre,
        "apellido": "Ap",
        "segundoApellido": "SA",
        "ci": "9876543",
        "telefono": "000",
        "rol": "user",
        "usuario": nombre,
        "correo": f"{nombre}@test.com",
        "urlImagen": None,
        "contrasena": "mypass123"
    }
    r = client.post("/empleados/", json=payload)
    assert r.status_code in (200, 201)

    # login (ruta registrada en main.py con prefix /auth)
    r = client.post("/auth/login", json={"usuario": payload["usuario"], "contrasena": payload["contrasena"]})
    assert r.status_code == 200, r.text

    # recuperar (solo comprobamos que la ruta responde)
    r = client.post("/auth/recuperar", json={"correo": payload["correo"], "ci": payload["ci"]})
    assert r.status_code in (200, 201), r.text
