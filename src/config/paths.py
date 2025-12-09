# src/config/paths.py
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]

DIR_ARCHIVOS = os.getenv("DIR_ARCHIVOS", "Archivos")
DIR_EMPLEADOS = os.getenv("DIR_EMPLEADOS", f"{DIR_ARCHIVOS}/empleados")
DIR_MODELOS_PRODUCTOS = os.getenv("DIR_MODELOS_PRODUCTOS", f"{DIR_ARCHIVOS}/modelos_productos")
# 👇 NUEVO
DIR_MOVIMIENTOS_IMPORTACION = os.getenv(
    "DIR_MOVIMIENTOS_IMPORTACION",
    f"{DIR_ARCHIVOS}/movimientosimportacion",
)

ARCHIVOS_DIR = (BASE_DIR / DIR_ARCHIVOS).resolve()
EMPLEADOS_DIR = (BASE_DIR / DIR_EMPLEADOS).resolve()
MODELOS_PRODUCTOS_DIR = (BASE_DIR / DIR_MODELOS_PRODUCTOS).resolve()
# 👇 NUEVO
MOVIMIENTOS_IMPORTACION_DIR = (BASE_DIR / DIR_MOVIMIENTOS_IMPORTACION).resolve()

for d in [ARCHIVOS_DIR, EMPLEADOS_DIR, MODELOS_PRODUCTOS_DIR, MOVIMIENTOS_IMPORTACION_DIR]:
    d.mkdir(parents=True, exist_ok=True)

__all__ = [
    "BASE_DIR",
    "ARCHIVOS_DIR",
    "EMPLEADOS_DIR",
    "MODELOS_PRODUCTOS_DIR",
    "MOVIMIENTOS_IMPORTACION_DIR",  # 👈 NUEVO
]
