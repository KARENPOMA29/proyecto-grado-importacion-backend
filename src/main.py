from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.routers import empleado_router, cliente_router, proveedor_router, categoria_router, modelo_producto_router, sucursal_router, almacen_router, seccion_router, auth_router, importacion_router, movimiento_router, producto_router, venta_router, movimiento_importacion_router ,ciudad_router, marca_router, alerta_router, reporte_ventas_router, reporte_entradas_router, reporte_importaciones_router
from src.config.db import Base, engine
from src.config.paths import EMPLEADOS_DIR
from fastapi.staticfiles import StaticFiles
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
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/archivos",
    StaticFiles(directory=str(EMPLEADOS_DIR.parent)),  # "Archivos" es el padre
    name="archivos",
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
app.include_router(venta_router.router)
app.include_router(movimiento_importacion_router.router)
app.include_router(ciudad_router.router)
app.include_router(marca_router.router)
app.include_router(alerta_router.router)
app.include_router(reporte_ventas_router.router)
app.include_router(reporte_entradas_router.router)
app.include_router(reporte_importaciones_router.router)
app.include_router(auth_router.router, prefix="/auth", tags=["Autenticación"])
# 📍 Ruta raíz
@app.get("/")
def home():
    return {"mensaje": "🚀 API de Empleados funcionando correctamente"}
