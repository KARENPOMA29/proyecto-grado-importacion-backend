from pydantic import BaseModel

class LoginRequest(BaseModel):
    usuario: str
    contrasena: str