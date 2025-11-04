# src/routers/auth_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.config.db import get_db
from src.controllers.auth_controller import login_empleado, recuperar_contrasena_empleado
from src.schemas.auth import LoginRequest, RecuperarRequest
from pydantic import BaseModel

router = APIRouter()   # 👈 SIN prefix aquí

@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    return login_empleado(db, credentials)

@router.post("/recuperar")
def recuperar_password(payload: RecuperarRequest, db: Session = Depends(get_db)):
    return recuperar_contrasena_empleado(db, payload.correo, payload.ci)
