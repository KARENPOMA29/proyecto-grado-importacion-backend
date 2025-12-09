# Documentación del Flujo del Sistema

## 1. Autenticación y Seguridad
### Flujo de Autenticación (`auth_controller.py` y `auth_router.py`)
1. El usuario ingresa credenciales (usuario y contraseña)
2. El sistema verifica las credenciales contra la base de datos
3. Si son válidas, genera un token JWT
4. El token se usa para todas las operaciones posteriores

### Seguridad (`utils/security.py`)
- Encriptación de contraseñas usando MD5
- Validación de tokens JWT
- Protección de rutas mediante decoradores

## 2. Gestión de Empleados
### Flujo de Empleados (`empleado_controller.py`)
1. **Crear Empleado**
   - Validación de duplicados (nombre, correo, CI)
   - Encriptación de contraseña
   - Registro en base de datos
   - Envío de credenciales por correo

2. **Actualizar Empleado**
   - Verificación de existencia
   - Validación de duplicados
   - Actualización de datos
   - Encriptación de nueva contraseña si se modifica

3. **Eliminar Empleado**
   - Marcado lógico (estado = 0)
   - No eliminación física de registros

## 3. Gestión de Inventario

### 3.1 Almacenes (`almacen_controller.py`)
1. **Creación de Almacén**
   - Registro de nuevo almacén
   - Asociación con sucursal
   - Validación de nombres únicos

2. **Gestión de Almacén**
   - Actualización de información
   - Listado de almacenes activos
   - Eliminación lógica

### 3.2 Productos (`producto_controller.py`)
1. **Registro de Productos**
   - Creación con datos básicos
   - Asociación con categoría y modelo
   - Asignación de código único

2. **Control de Stock**
   - Actualización de existencias
   - Verificación de disponibilidad
   - Alertas de stock bajo

### 3.3 Movimientos de Inventario (`movimiento_controller.py`)
1. **Registro de Movimientos**
   - Entradas de productos
   - Salidas de productos
   - Transferencias entre almacenes

2. **Control de Movimientos**
   - Validación de stock disponible
   - Registro de fecha y responsable
   - Histórico de movimientos

## 4. Gestión de Ventas

### 4.1 Proceso de Venta (`venta_controller.py`)
1. **Creación de Venta**
   - Registro de cliente
   - Selección de productos
   - Cálculo de totales
   - Verificación de stock

2. **Detalle de Venta**
   - Registro de productos vendidos
   - Cantidades y precios
   - Descuentos aplicados

3. **Finalización de Venta**
   - Actualización de inventario
   - Generación de comprobante
   - Registro de pago

## 5. Gestión de Clientes y Proveedores

### 5.1 Clientes (`cliente_controller.py`)
1. **Registro de Clientes**
   - Datos personales
   - Historial de compras
   - Estado de cuenta

### 5.2 Proveedores (`proveedor_controller.py`)
1. **Gestión de Proveedores**
   - Registro de información
   - Productos suministrados
   - Historial de importaciones

## 6. Importaciones

### 6.1 Proceso de Importación (`importacion_controller.py`)
1. **Registro de Importación**
   - Datos del proveedor
   - Productos importados
   - Costos y cantidades

2. **Control de Importación**
   - Seguimiento de estado
   - Actualización de inventario
   - Registro de documentos

## 7. Categorías y Secciones

### 7.1 Categorías (`categoria_controller.py`)
- Gestión de categorías de productos
- Organización jerárquica
- Asociación con productos

### 7.2 Secciones (`seccion_controller.py`)
- Organización física de almacenes
- Asignación de productos
- Control de ubicaciones

## 8. Sucursales

### 8.1 Gestión de Sucursales (`sucursal_controller.py`)
1. **Administración de Sucursales**
   - Registro de ubicaciones
   - Asignación de almacenes
   - Control de personal

2. **Operaciones por Sucursal**
   - Gestión independiente de inventario
   - Control de ventas por sucursal
   - Reportes específicos

## 9. Utilitarios del Sistema

### 9.1 Mailer (`utils/mailer.py`)
- Envío de credenciales
- Notificaciones automáticas
- Alertas del sistema

## 10. Flujo de Datos General

1. **Entrada de Datos**
   - Interfaces de usuario (Frontend)
   - Validaciones (Schemas)
   - Autorización (JWT)

2. **Procesamiento**
   - Controladores (Lógica de negocio)
   - Modelos (Estructura de datos)
   - Servicios (Funciones auxiliares)

3. **Almacenamiento**
   - Base de datos (SQLAlchemy)
   - Registro de transacciones
   - Auditoría de cambios

4. **Salida**
   - Respuestas API (FastAPI)
   - Reportes y consultas
   - Notificaciones

## 11. Integración Frontend-Backend

1. **Comunicación**
   - API REST
   - Autenticación JWT
   - Manejo de estados

2. **Interfaz de Usuario**
   - Componentes React
   - Servicios de API
   - Gestión de contexto

3. **Seguridad**
   - Validación de tokens
   - Protección de rutas
   - Control de acceso