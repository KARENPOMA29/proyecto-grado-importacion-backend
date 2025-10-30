from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routers import empleado_router, cliente_router, proveedor_router, categoria_router, modelo_producto_router, sucursal_router, almacen_router, seccion_router, auth_router, importacion_router, movimiento_router, producto_router
from src.config.db import Base, engine

# 🗄️ Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API - Gestión de Empleados",
    description="API REST para gestionar empleados del sistema",
    version="1.0.0"
)

# 🌐 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📍 Registrar rutas
app.include_router(empleado_router.router)
app.include_router(cliente_router.router)
app.include_router(proveedor_router.router)
app.include_router(categoria_router.router)
app.include_router(modelo_producto_router.router)
app.include_router(sucursal_router.router)
app.include_router(almacen_router.router)
app.include_router(seccion_router.router)
app.include_router(importacion_router.router)
app.include_router(movimiento_router.router)
app.include_router(producto_router.router)
app.include_router(auth_router.router, prefix="/auth", tags=["Autenticación"])
# 📍 Ruta raíz
@app.get("/")
def home():
    return {"mensaje": "🚀 API de Empleados funcionando correctamente"}
