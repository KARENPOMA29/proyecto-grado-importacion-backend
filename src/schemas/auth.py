from pydantic import BaseModel

class LoginRequest(BaseModel):
    usuario: str
    contrasena: str
    
class RecuperarRequest(BaseModel):
    correo: str
    ci: str
