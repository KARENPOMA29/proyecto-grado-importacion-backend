from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException


def _row_to_dict(row):
    return dict(row._mapping) if row else None


def obtener_empleado(db: Session, empleado_id: int):
    sql = text("""
        SELECT id, nombre, apellido, segundoApellido, rol
        FROM Empleado
        WHERE id = :empleado_id AND estado = 1
    """)

    row = db.execute(sql, {"empleado_id": empleado_id}).first()

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Empleado no encontrado o inactivo."
        )

    return _row_to_dict(row)


def obtener_dashboard_ventas(db: Session, empleado_id: int):
    sql = text("""
        SELECT *
        FROM vw_dashboard_empleado_ventas
        WHERE empleadoId = :empleado_id
    """)

    row = db.execute(sql, {"empleado_id": empleado_id}).first()
    data = _row_to_dict(row)

    return data or {
        "empleadoId": empleado_id,
        "totalVentas": 0,
        "montoTotalVendido": 0,
        "productosVendidos": 0,
        "promedioVenta": 0,
        "mejorVenta": 0,
        "modeloMasVendido": None,
        "mejorDiaVentas": None,
    }


def obtener_dashboard_almacen(db: Session, empleado_id: int):
    sql = text("""
        SELECT *
        FROM vw_dashboard_empleado_almacen
        WHERE empleadoId = :empleado_id
    """)

    row = db.execute(sql, {"empleado_id": empleado_id}).first()
    data = _row_to_dict(row)

    return data or {
        "empleadoId": empleado_id,
        "totalMovimientos": 0,
        "productosGestionados": 0,
        "almacenesAfectados": 0,
        "entradas": 0,
        "salidas": 0,
        "productosObservados": 0,
        "ultimoMovimiento": None,
        "diaConMasMovimientos": None,
        "almacenMasUsado": None,
    }


def obtener_dashboard_pilotero(db: Session, empleado_id: int):
    sql = text("""
        SELECT *
        FROM vw_dashboard_empleado_pilotero
        WHERE empleadoId = :empleado_id
    """)

    row = db.execute(sql, {"empleado_id": empleado_id}).first()
    data = _row_to_dict(row)

    return data or {
        "empleadoId": empleado_id,
        "totalImportaciones": 0,
        "enProceso": 0,
        "concluidas": 0,
        "retrasadas": 0,
        "productosGestionados": 0,
        "inversionGestionada": 0,
        "valorVentaGestionado": 0,
        "gananciaGestionada": 0,
        "importacionAntesDeFecha": None,
        "mayorImportacionGestionada": None,
    }


def obtener_dashboard_por_empleado(db: Session, empleado_id: int):
    empleado = obtener_empleado(db, empleado_id)

    rol = empleado["rol"]

    if rol == "Ventas":
        dashboard = obtener_dashboard_ventas(db, empleado_id)

    elif rol == "Almacen":
        dashboard = obtener_dashboard_almacen(db, empleado_id)

    elif rol == "Pilotero":
        dashboard = obtener_dashboard_pilotero(db, empleado_id)

    else:
        raise HTTPException(
            status_code=400,
            detail=f"El rol '{rol}' no tiene dashboard configurado."
        )

    return {
        "empleado": empleado,
        "rol": rol,
        "dashboard": dashboard,
    }