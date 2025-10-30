from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.config.db import get_db
from src.controllers.auth_controller import login_empleado
from src.schemas.auth import LoginRequest

router = APIRouter()

@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint para autenticar empleados
    """
    return login_empleado(db, credentials)