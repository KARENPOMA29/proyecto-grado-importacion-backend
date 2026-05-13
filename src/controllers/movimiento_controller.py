# src/controllers/movimiento_controller.py

from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, cast, String, Date
from datetime import datetime
from src.models.movimiento_inventario import MovimientoInventario
from src.models.producto import Producto
from src.models.modelo_producto import ModeloProducto
from src.models.almacen import Almacen
from src.models.categoria import Categoria
from src.models.importacion import Importacion
from src.models.sucursal import Sucursal
from src.models.seccion import Seccion
from src.models.empleado import Empleado
from src.models.ciudad import Ciudad

from src.schemas.movimiento import MovimientoCreate, MovimientoUpdate


# =========================================================
# 🔹 ADJUNTAR EXTRAS
# =========================================================

def _adjuntar_extras(db: Session, mov: MovimientoInventario):

    if mov.productoId:
        prod = (
            db.query(Producto)
            .filter(Producto.id == mov.productoId)
            .first()
        )

        mov.producto = prod

        if prod:
            mov.productoSerie = prod.numeroSerie
            mov.productoDescripcion = prod.descripcion
            mov.productoObservado = prod.observado
            mov.productoObsDescripcion = prod.obsDescripcion
            mov.productoEstado = prod.estado

            # MODELO
            if prod.modeloId:
                mov.modeloProducto = (
                    db.query(ModeloProducto)
                    .filter(ModeloProducto.id == prod.modeloId)
                    .first()
                )
            else:
                mov.modeloProducto = None

            # CATEGORIA
            if prod.categoriaId:
                mov.categoria = (
                    db.query(Categoria)
                    .filter(Categoria.id == prod.categoriaId)
                    .first()
                )
            else:
                mov.categoria = None

            # IMPORTACION
            if prod.importacionId:
                mov.importacion = (
                    db.query(Importacion)
                    .filter(Importacion.id == prod.importacionId)
                    .first()
                )
            else:
                mov.importacion = None

        else:
            mov.modeloProducto = None
            mov.categoria = None
            mov.importacion = None

    else:
        mov.producto = None
        mov.modeloProducto = None
        mov.categoria = None
        mov.importacion = None

    # ALMACEN
    if mov.almacenId:
        alm = (
            db.query(Almacen)
            .filter(Almacen.id == mov.almacenId)
            .first()
        )

        mov.almacen = alm
        mov.almacenNombre = alm.nombre if alm else None

    return mov


# =========================================================
# 🔹 LISTAR MOVIMIENTOS
# =========================================================

def listar_movimientos(
    db: Session,
    usuario_id: Optional[int] = None,
    almacen_id: Optional[int] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    estado_producto: Optional[int] = None,
    fecha: Optional[str] = None,
):
    # Último movimiento activo por producto
    ultimos = (
        db.query(
            MovimientoInventario.productoId.label("productoId"),
            func.max(MovimientoInventario.id).label("ultimoMovimientoId"),
        )
        .filter(MovimientoInventario.estado == 1)
        .group_by(MovimientoInventario.productoId)
        .subquery()
    )

    query = (
        db.query(MovimientoInventario)
        .join(ultimos, MovimientoInventario.id == ultimos.c.ultimoMovimientoId)
        .outerjoin(Producto, Producto.id == MovimientoInventario.productoId)
        .outerjoin(Almacen, Almacen.id == MovimientoInventario.almacenId)
        .outerjoin(ModeloProducto, ModeloProducto.id == Producto.modeloId)
        .outerjoin(Categoria, Categoria.id == Producto.categoriaId)
        .outerjoin(Importacion, Importacion.id == Producto.importacionId)
        .filter(MovimientoInventario.estado == 1)
    )

    if usuario_id is not None:
        query = query.filter(MovimientoInventario.usuarioId == usuario_id)

    if almacen_id is not None:
        query = query.filter(MovimientoInventario.almacenId == almacen_id)

    if estado_producto is not None:
        query = query.filter(Producto.estado == estado_producto)

    if fecha:
        query = query.filter(cast(MovimientoInventario.fecha, Date) == fecha)

    if search:
        search_clean = search.strip().lower()
        term = f"%{search_clean}%"

        condiciones = [
            func.lower(func.coalesce(Producto.numeroSerie, "")).like(term),
            func.lower(func.coalesce(Producto.descripcion, "")).like(term),
            func.lower(func.coalesce(MovimientoInventario.tipoMovimiento, "")).like(term),
            func.lower(func.coalesce(Almacen.nombre, "")).like(term),
            func.lower(func.coalesce(ModeloProducto.nombreModelo, "")).like(term),
            func.lower(func.coalesce(Categoria.nombre, "")).like(term),
            func.lower(func.coalesce(Importacion.codigo, "")).like(term),
        ]

        query = query.filter(or_(*condiciones))

    total = query.count()

    movs = (
        query.order_by(MovimientoInventario.fecha.desc(), MovimientoInventario.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    for m in movs:
        _adjuntar_extras(db, m)

    return {
        "items": movs,
        "total": total,
    }
# =========================================================
# 🔹 OBTENER MOVIMIENTO
# =========================================================

def obtener_movimiento(db: Session, movimiento_id: int):

    mov = (
        db.query(MovimientoInventario)
        .filter(
            MovimientoInventario.id == movimiento_id,
            MovimientoInventario.estado == 1,
        )
        .first()
    )

    if not mov:
        raise HTTPException(
            status_code=404,
            detail="Movimiento no encontrado"
        )

    _adjuntar_extras(db, mov)

    return mov


# =========================================================
# 🔹 DETALLE COMPLETO MOVIMIENTO
# =========================================================

def obtener_movimiento_detalle(db: Session, movimiento_id: int):

    mov = (
        db.query(MovimientoInventario)
        .filter(
            MovimientoInventario.id == movimiento_id,
            MovimientoInventario.estado == 1,
        )
        .first()
    )

    if not mov:
        raise HTTPException(
            status_code=404,
            detail="Movimiento no encontrado"
        )

    producto = None
    modelo = None
    categoria = None
    importacion = None
    seccion = None
    almacen = None
    sucursal = None
    ciudad = None
    empleado = None

    # PRODUCTO
    if mov.productoId:
        producto = (
            db.query(Producto)
            .filter(Producto.id == mov.productoId)
            .first()
        )

    # ALMACEN
    if mov.almacenId:
        almacen = (
            db.query(Almacen)
            .filter(Almacen.id == mov.almacenId)
            .first()
        )

    # MODELO / CATEGORIA / IMPORTACION
    if producto:

        if producto.modeloId:
            modelo = (
                db.query(ModeloProducto)
                .filter(ModeloProducto.id == producto.modeloId)
                .first()
            )

        if producto.categoriaId:
            categoria = (
                db.query(Categoria)
                .filter(Categoria.id == producto.categoriaId)
                .first()
            )

        if producto.importacionId:
            importacion = (
                db.query(Importacion)
                .filter(Importacion.id == producto.importacionId)
                .first()
            )

        # ✅ SECCION
        # según tu BDD:
        # Seccion.almacenId + Seccion.modeloId

        if mov.almacenId and producto.modeloId:

            seccion = (
                db.query(Seccion)
                .filter(
                    Seccion.almacenId == mov.almacenId,
                    Seccion.modeloId == producto.modeloId,
                    Seccion.estado == 1,
                )
                .first()
            )

    # SUCURSAL
    if almacen and almacen.sucursalId:

        sucursal = (
            db.query(Sucursal)
            .filter(Sucursal.id == almacen.sucursalId)
            .first()
        )

    # CIUDAD
    if sucursal and sucursal.idCiudad:

        ciudad = (
            db.query(Ciudad)
            .filter(Ciudad.id == sucursal.idCiudad)
            .first()
        )

    # EMPLEADO
    if mov.usuarioId:

        empleado = (
            db.query(Empleado)
            .filter(Empleado.id == mov.usuarioId)
            .first()
        )

    return {

        "id": mov.id,
        "tipoMovimiento": mov.tipoMovimiento,
        "fecha": mov.fecha,
        "estado": mov.estado,

        "empleado": {
            "id": empleado.id,
            "nombre": getattr(empleado, "nombre", None),
            "apellido": getattr(empleado, "apellido", None),
            "ci": getattr(empleado, "ci", None),
            "correo": getattr(empleado, "correo", None),
            "telefono": getattr(empleado, "telefono", None),
            "rol": getattr(empleado, "rol", None),
        } if empleado else None,

        "sucursal": {
            "id": sucursal.id,
            "nombre": sucursal.nombre,
            "telefono": sucursal.telefono,
            "direccion": sucursal.direccion,
            "ciudad": ciudad.nombre if ciudad else None,
        } if sucursal else None,

        "almacen": {
            "id": almacen.id,
            "nombre": almacen.nombre,
            "direccion": almacen.direccion,
        } if almacen else None,

        "seccion": {
            "id": seccion.id,
            "nombre": seccion.nombre,
        } if seccion else None,

        "producto": {
            "id": producto.id,
            "numeroSerie": getattr(producto, "numeroSerie", None),
            "descripcion": getattr(producto, "descripcion", None),
            "precio": getattr(producto, "precio", None),
            "precioOrigen": getattr(producto, "precioOrigen", None),
            "estado": getattr(producto, "estado", None),
            "observado": getattr(producto, "observado", None),
            "obsDescripcion": getattr(producto, "obsDescripcion", None),
            "fechaRegistro": getattr(producto, "fechaRegistro", None),
        } if producto else None,

        "modelo": {
            "id": modelo.id,
            "nombreModelo": getattr(modelo, "nombreModelo", None),
        } if modelo else None,

        "categoria": {
            "id": categoria.id,
            "nombre": categoria.nombre,
        } if categoria else None,

        "importacion": {
            "id": importacion.id,
            "codigo": getattr(importacion, "codigo", None),
            "fechaLlegada": getattr(importacion, "fechaLlegada", None),
        } if importacion else None,
    }


# =========================================================
# 🔹 CREAR MOVIMIENTO
# =========================================================

def crear_movimiento(
    db: Session,
    payload: MovimientoCreate,
    usuario_id: int | None = None,
):

    prod = (
        db.query(Producto)
        .filter(Producto.id == payload.productoId)
        .first()
    )

    if not prod:
        raise HTTPException(
            status_code=404,
            detail="Producto no existe"
        )

    mov = MovimientoInventario(
        productoId=payload.productoId,
        almacenId=payload.almacenId,
        tipoMovimiento=payload.tipoMovimiento,
        usuarioId=usuario_id,
        estado=1,
    )

    db.add(mov)

    db.commit()
    db.refresh(mov)

    _adjuntar_extras(db, mov)

    return mov


# =========================================================
# 🔹 ACTUALIZAR MOVIMIENTO
# =========================================================

def actualizar_movimiento_detalle(db: Session, movimiento_id: int, payload):
    try:
        mov = (
            db.query(MovimientoInventario)
            .filter(
                MovimientoInventario.id == movimiento_id,
                MovimientoInventario.estado == 1,
            )
            .first()
        )

        if not mov:
            raise HTTPException(status_code=404, detail="Movimiento no encontrado")

        producto = (
            db.query(Producto)
            .filter(Producto.id == mov.productoId)
            .first()
        )

        if not producto:
            raise HTTPException(status_code=404, detail="Producto asociado no encontrado")

        if producto.estado == 2:
            raise HTTPException(
                status_code=400,
                detail="No se puede editar este movimiento porque el producto ya fue vendido."
            )

        almacen_actual_id = mov.almacenId
        modelo_actual_id = producto.modeloId

        nuevo_almacen_id = (
            payload.almacenId
            if payload.almacenId is not None
            else almacen_actual_id
        )
        nuevo_modelo_id = modelo_actual_id

        almacen = (
            db.query(Almacen)
            .filter(Almacen.id == nuevo_almacen_id)
            .first()
        )

        if not almacen:
            raise HTTPException(status_code=404, detail="Almacén no encontrado")

        if payload.seccionId is not None:
            seccion = (
                db.query(Seccion)
                .filter(
                    Seccion.id == payload.seccionId,
                    Seccion.estado == 1,
                )
                .first()
            )

            if not seccion:
                raise HTTPException(status_code=404, detail="Sección no encontrada")

            if int(seccion.almacenId) != int(nuevo_almacen_id):
                raise HTTPException(
                    status_code=400,
                    detail="La sección no pertenece al almacén seleccionado",
                )

            if not seccion.modeloId:
                raise HTTPException(
                    status_code=400,
                    detail="La sección seleccionada no tiene un modelo asignado",
                )

            nuevo_modelo_id = seccion.modeloId

        if payload.categoriaId is not None:
            categoria = (
                db.query(Categoria)
                .filter(Categoria.id == payload.categoriaId)
                .first()
            )

            if not categoria:
                raise HTTPException(status_code=404, detail="Categoría no encontrada")

            producto.categoriaId = payload.categoriaId

        if payload.importacionId is not None:
            importacion = (
                db.query(Importacion)
                .filter(Importacion.id == payload.importacionId)
                .first()
            )

            if not importacion:
                raise HTTPException(status_code=404, detail="Importación no encontrada")

            producto.importacionId = payload.importacionId

        if payload.productoDescripcion is not None:
            producto.descripcion = payload.productoDescripcion

        if payload.productoPrecioOrigen is not None:
            producto.precioOrigen = payload.productoPrecioOrigen

        if payload.productoPrecio is not None:
            producto.precio = payload.productoPrecio

        if payload.productoObservado is not None:
            producto.observado = payload.productoObservado

        producto.obsDescripcion = payload.productoObsDescripcion
        producto.modeloId = nuevo_modelo_id

        cambio_ubicacion = int(nuevo_almacen_id) != int(almacen_actual_id)
        cambio_modelo = int(nuevo_modelo_id) != int(modelo_actual_id or 0)

        if cambio_ubicacion or cambio_modelo:
            nuevo_mov = MovimientoInventario(
                productoId=producto.id,
                almacenId=nuevo_almacen_id,
                tipoMovimiento=payload.tipoMovimiento or "ENTRADA",
                usuarioId=mov.usuarioId,
                estado=1,
                fecha=datetime.utcnow(),
            )

            db.add(nuevo_mov)
            db.commit()
            db.refresh(nuevo_mov)

            return obtener_movimiento_detalle(db, nuevo_mov.id)

        if payload.tipoMovimiento is not None:
            if payload.tipoMovimiento not in ["ENTRADA", "SALIDA"]:
                raise HTTPException(
                    status_code=400,
                    detail="Tipo de movimiento inválido",
                )

            mov.tipoMovimiento = payload.tipoMovimiento

        db.commit()
        db.refresh(mov)

        return obtener_movimiento_detalle(db, mov.id)

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar movimiento: {str(e)}"
        )
# =========================================================
# 🔹 ELIMINAR MOVIMIENTO
# =========================================================

def eliminar_movimiento(db: Session, movimiento_id: int):
    mov = (
        db.query(MovimientoInventario)
        .filter(
            MovimientoInventario.id == movimiento_id,
            MovimientoInventario.estado == 1,
        )
        .first()
    )

    if not mov:
        raise HTTPException(
            status_code=404,
            detail="Movimiento no encontrado"
        )

    producto = (
        db.query(Producto)
        .filter(Producto.id == mov.productoId)
        .first()
    )

    if not producto:
        raise HTTPException(
            status_code=404,
            detail="Producto asociado no encontrado"
        )

    if producto.estado == 2:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar este movimiento porque el producto ya fue vendido."
        )

    mov.estado = 0
    producto.estado = 0
    db.commit()

    return {
        "detail": "Movimiento eliminado correctamente"
    }