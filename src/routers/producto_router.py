# src/routers/producto_router.py
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.config.db import SessionLocal
from src.schemas.producto import ProductoCreate, ProductoUpdate, ProductoOut
from src.controllers import producto_controller as controller

router = APIRouter(
    prefix="/productos",
    tags=["Productos"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/disponibles/sucursal/{sucursal_id}")
def productos_disponibles_por_sucursal(
    sucursal_id: int,
    db: Session = Depends(get_db),
):
    sql = text("""
        SELECT
            productoId AS id,
            numeroSerie,
            descripcion,
            precio,
            precioOrigen,
            modeloId,
            nombreModelo,
            color,
            capacidadOTamano,
            urlImagen,
            almacenId,
            almacenNombre,
            sucursalId,
            sucursalNombre
        FROM vw_productos_disponibles_por_sucursal
        WHERE sucursalId = :sucursal_id
        ORDER BY nombreModelo, numeroSerie
    """)

    result = db.execute(sql, {"sucursal_id": sucursal_id}).mappings().all()

    return [dict(row) for row in result]

# -------------------------------------------------------------------
# POST /productos/  -> crear
# -------------------------------------------------------------------
@router.post("/", response_model=ProductoOut)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    return controller.crear_producto(db, producto)


# -------------------------------------------------------------------
# GET /productos/  -> listar (con filtro de estado opcional)
#   ?estado=1  -> disponibles (por defecto)
#   ?estado=2  -> vendidos
#   ?estado=0  -> inactivos
#   sin estado -> por defecto 1 (disponibles)
# -------------------------------------------------------------------
@router.get("/", response_model=List[ProductoOut])
def listar_productos(
    estado: Optional[int] = Query(
        1,
        description="Estado del producto (0, 1, 2). Por defecto 1 = disponible",
    ),
    observado: Optional[int] = Query(
        None,
        description="1 = normal, 2 = observado",
    ),
    categoriaId: Optional[int] = Query(
        None,
        description="ID de categoría",
    ),
    modeloId: Optional[int] = Query(
        None,
        description="ID de modelo",
    ),
    importacionId: Optional[int] = Query(
        None,
        description="ID de importación",
    ),
    numeroSerie: Optional[str] = Query(
        None,
        description="Búsqueda parcial por número de serie",
    ),
    db: Session = Depends(get_db),
):
    return controller.listar_productos(
        db,
        estado=estado,
        observado=observado,
        categoriaId=categoriaId,
        modeloId=modeloId,
        importacionId=importacionId,
        numeroSerie=numeroSerie,
    )




@router.get("/buscador")
def buscar_productos(
    search: Optional[str] = Query(None),

    estado: Optional[int] = Query(
        1,
        description="1=Disponible, 2=Vendido, 0=Inactivo"
    ),

    categoriaId: Optional[int] = Query(None),
    modeloId: Optional[int] = Query(None),
    ciudadId: Optional[int] = Query(None),
    sucursalId: Optional[int] = Query(None),
    almacenId: Optional[int] = Query(None),
    seccionId: Optional[int] = Query(None),

    observado: Optional[int] = Query(None),

    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),

    db: Session = Depends(get_db),
):
    offset = (page - 1) * pageSize

    where = ["1 = 1"]

    params = {
        "offset": offset,
        "pageSize": pageSize,
    }

    # ---------------------------------------------------------
    # FILTROS
    # ---------------------------------------------------------

    if estado is not None:
        where.append("productoEstado = :estado")
        params["estado"] = estado

    if categoriaId is not None:
        where.append("categoriaId = :categoriaId")
        params["categoriaId"] = categoriaId

    if modeloId is not None:
        where.append("modeloId = :modeloId")
        params["modeloId"] = modeloId

    if ciudadId is not None:
        where.append("ciudadId = :ciudadId")
        params["ciudadId"] = ciudadId

    if sucursalId is not None:
        where.append("sucursalId = :sucursalId")
        params["sucursalId"] = sucursalId

    if almacenId is not None:
        where.append("almacenId = :almacenId")
        params["almacenId"] = almacenId

    if seccionId is not None:
        where.append("seccionId = :seccionId")
        params["seccionId"] = seccionId

    if observado is not None:
        where.append("observado = :observado")
        params["observado"] = observado

    # ---------------------------------------------------------
    # BÚSQUEDA GENERAL
    # ---------------------------------------------------------

    if search and search.strip():
        where.append("""
        (
            numeroSerie LIKE :search OR
            descripcion LIKE :search OR
            categoriaNombre LIKE :search OR
            nombreModelo LIKE :search OR
            ciudadNombre LIKE :search OR
            sucursalNombre LIKE :search OR
            almacenNombre LIKE :search OR
            seccionNombre LIKE :search OR
            importacionCodigo LIKE :search
        )
        """)

        params["search"] = f"%{search.strip()}%"

    where_sql = " AND ".join(where)

    # ---------------------------------------------------------
    # TOTAL
    # ---------------------------------------------------------

    total_sql = text(f"""
        SELECT COUNT(*) AS total
        FROM vw_productos_buscador
        WHERE {where_sql}
    """)

    total = db.execute(total_sql, params).scalar() or 0

    # ---------------------------------------------------------
    # DATA
    # ---------------------------------------------------------

    data_sql = text(f"""
        SELECT *
        FROM vw_productos_buscador
        WHERE {where_sql}
        ORDER BY fechaRegistro DESC
        OFFSET :offset ROWS
        FETCH NEXT :pageSize ROWS ONLY
    """)

    rows = db.execute(data_sql, params).mappings().all()

    return {
        "items": [dict(row) for row in rows],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }

# -------------------------------------------------------------------
# GET /productos/{id} -> obtener por ID (solo activos)
# -------------------------------------------------------------------
@router.get("/{producto_id}", response_model=ProductoOut)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    return controller.obtener_producto(db, producto_id)


# -------------------------------------------------------------------
# GET /productos/by-serie/{numero_serie} -> obtener por número de serie
#   Devuelve null si no existe o está inactivo
# -------------------------------------------------------------------
@router.get("/by-serie/{numero_serie}", response_model=Optional[ProductoOut])
def obtener_producto_por_serie(numero_serie: str, db: Session = Depends(get_db)):
    producto = controller.obtener_producto_por_serie(db, numero_serie)
    # No lanzamos 404; dejamos que el frontend reciba null si no hay
    return producto


# -------------------------------------------------------------------
# PUT /productos/{id} -> actualizar
# -------------------------------------------------------------------
@router.put("/{producto_id}", response_model=ProductoOut)
def actualizar_producto(
    producto_id: int,
    datos: ProductoUpdate,
    db: Session = Depends(get_db),
):
    return controller.actualizar_producto(db, producto_id, datos)


# -------------------------------------------------------------------
# DELETE /productos/{id} -> borrado lógico
# -------------------------------------------------------------------
@router.delete("/{producto_id}")
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    return controller.eliminar_producto(db, producto_id)
