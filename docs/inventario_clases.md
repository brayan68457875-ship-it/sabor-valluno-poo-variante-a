# Inventario de clases del código entregado

Este inventario se extrae de las definiciones reales. Complementa el diagrama, que omite constructores, propiedades rutinarias y auxiliares de serialización para conservar legibilidad. Los nombres de las 17 clases se mantienen. Las firmas muestran las anotaciones que contiene el código; los tipos de los contratos de dominio también se indican en la imagen UML.

## Cambios finales respecto al diagrama proporcionado

Se añadieron al dibujo el cobro centralizado y JSON en Restaurante, el diccionario de decisiones pendientes en ReglasVariante, la tarifa como argumento de calcular_envio, los contratos de conteo y compatibilidad necesarios, el cálculo por cantidad de Combo y la cotización histórica de DetalleProducto. La fecha de un pago admite None antes de procesarlo. No se sustituyó ninguna de las tres jerarquías.

La implementación agrega auxiliares de persistencia y validación, sin introducir nuevas clases de negocio. El diagrama original entregado antes de programar se conserva como diagrama_base_proporcionado.png.

## Restaurante

Archivo: `restaurante.py`. Base: object.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_clientes`, `_nombre`, `_pedidos`, `_productos`, `_reglas`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, nombre='Sabor Valluno', reglas=None)` | constructor |
| `nombre` | Propiedad; solo lectura |
| `reglas` | Propiedad; solo lectura |
| `productos` | Propiedad; solo lectura |
| `clientes` | Propiedad; solo lectura |
| `pedidos` | Propiedad; solo lectura |
| `seleccionar_variante(self, codigo: str)` | público |
| `registrar_producto(self, producto)` | público |
| `registrar_cliente(self, cliente: modelo.clientes.Cliente)` | público |
| `mesa_disponible(self, mesa: int) -> bool` | público |
| `crear_pedido(self, pedido)` | público |
| `listar_menu(self, dia: str)` | público |
| `siguiente_id_producto(self)` | público |
| `siguiente_id_cliente(self)` | público |
| `siguiente_id_pedido(self)` | público |
| `siguiente_id_pago(self)` | público |
| `cobrar_pedido(self, id_pedido, metodo)` | público |
| `_ventas_del_dia(self, fecha)` | protegido |
| `productos_mas_vendidos(self, fecha: datetime.date)` | público |
| `reporte_ventas(self, fecha: datetime.date) -> dict` | público |
| `guardar_json(self, ruta)` | público |
| `cargar_json(ruta)` | público |
| `_desde_datos(datos)` | protegido |

## Cliente

Archivo: `modelo/clientes.py`. Base: object.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_direccion`, `_id_cliente`, `_nombre`, `_telefono`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_cliente: int, nombre: str, telefono: str, direccion: str = '')` | constructor |
| `id_cliente` | Propiedad; solo lectura |
| `nombre` | Propiedad; lectura y setter |
| `telefono` | Propiedad; lectura y setter |
| `direccion` | Propiedad; lectura y setter |
| `validar_telefono(valor: str) -> bool` | público |
| `actualizar_datos(self, nombre: str, telefono: str, direccion: str)` | público |
| `a_dict(self)` | público |

## Producto

Archivo: `modelo/productos.py`. Base: ABC.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_id_producto`, `_nombre`, `_reglas`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_producto: int, nombre: str, reglas)` | constructor |
| `id_producto` | Propiedad; solo lectura |
| `nombre` | Propiedad; solo lectura |
| `reglas` | Propiedad; solo lectura |
| `calcular_precio(self) -> decimal.Decimal` | público · abstracto |
| `esta_disponible(self, dia: str) -> bool` | público · abstracto |
| `contar_platos(self) -> int` | público · abstracto |
| `contar_productos(self) -> int` | público |
| `calcular_importe(self, cantidad: int, dia: str) -> decimal.Decimal` | público |
| `validar_precio(precio: decimal.Decimal)` | público |
| `contiene(self, producto)` | público |
| `desglosar_ventas(self, cantidad)` | público |
| `a_dict(self)` | público |

## Plato

Archivo: `modelo/productos.py`. Base: Producto.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_dias_venta`, `_precio_base`, `_restriccion_variante`, `precio_base`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_producto: int, nombre: str, precio_base, reglas, dias_venta=None)` | constructor |
| `precio_base` | Propiedad; lectura y setter |
| `dias_venta` | Propiedad; solo lectura |
| `actualizar_dias(self, dias)` | público |
| `calcular_precio(self) -> decimal.Decimal` | público |
| `esta_disponible(self, dia: str) -> bool` | público |
| `contar_platos(self) -> int` | público |
| `a_dict(self)` | público |

## Bebida

Archivo: `modelo/productos.py`. Base: Producto.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_es_natural`, `_precio_vaso`, `_presentacion`, `precio_vaso`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_producto: int, nombre: str, precio_vaso, reglas, presentacion='vaso', es_natural=False)` | constructor |
| `precio_vaso` | Propiedad; lectura y setter |
| `presentacion` | Propiedad; solo lectura |
| `es_natural` | Propiedad; solo lectura |
| `calcular_precio(self) -> decimal.Decimal` | público |
| `esta_disponible(self, dia: str) -> bool` | público |
| `contar_platos(self) -> int` | público |
| `calcular_importe(self, cantidad: int, dia: str) -> decimal.Decimal` | público |
| `a_dict(self)` | público |

## Combo

Archivo: `modelo/productos.py`. Base: Producto.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_componentes`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_producto: int, nombre: str, componentes, reglas)` | constructor |
| `componentes` | Propiedad; solo lectura |
| `calcular_precio(self) -> decimal.Decimal` | público |
| `esta_disponible(self, dia: str) -> bool` | público |
| `contar_platos(self) -> int` | público |
| `contar_productos(self) -> int` | público |
| `calcular_importe(self, cantidad: int, dia: str) -> decimal.Decimal` | público |
| `contiene(self, p: modelo.productos.Producto) -> bool` | público |
| `validar_sin_ciclos(self, p: modelo.productos.Producto)` | público |
| `agregar_componente(self, p: modelo.productos.Producto)` | público |
| `quitar_componente(self, p: modelo.productos.Producto)` | público |
| `desglosar_ventas(self, cantidad)` | público |
| `a_dict(self)` | público |

## Pedido

Archivo: `modelo/pedidos.py`. Base: ABC.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_cliente`, `_estado`, `_fecha_registro`, `_id_pedido`, `_items`, `_modalidad`, `_pago`, `_reglas`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_pedido: int, cliente, reglas, fecha_registro=None)` | constructor |
| `id_pedido` | Propiedad; solo lectura |
| `cliente` | Propiedad; solo lectura |
| `reglas` | Propiedad; solo lectura |
| `fecha_registro` | Propiedad; solo lectura |
| `estado` | Propiedad; solo lectura |
| `pago` | Propiedad; solo lectura |
| `modalidad` | Propiedad; solo lectura |
| `items` | Propiedad; solo lectura |
| `items_lectura(self)` | público |
| `_validar_edicion(self)` | protegido |
| `agregar_producto(self, producto, cantidad: int)` | público |
| `quitar_producto(self, id_producto: int)` | público |
| `calcular_subtotal(self) -> decimal.Decimal` | público |
| `calcular_descuento(self) -> decimal.Decimal` | público |
| `calcular_cargos(self) -> decimal.Decimal` | público · abstracto |
| `contar_platos(self) -> int` | público |
| `contar_productos(self) -> int` | público |
| `validar_minimo(self)` | público |
| `calcular_total(self) -> decimal.Decimal` | público |
| `_validar_confirmacion(self)` | protegido |
| `_transicionar(self, nuevo)` | protegido |
| `siguientes_estados(self)` | público |
| `cambiar_estado(self, nuevo: modelo.pedidos.EstadoPedido)` | público |
| `cancelar(self)` | público |
| `registrar_entrega(self, fecha: datetime.datetime)` | público |
| `validar_pago(self, pago)` | público |
| `cobrar(self, metodo) -> decimal.Decimal` | público |
| `calcular_compensacion(self) -> decimal.Decimal` | público |
| `mesa_ocupada(self)` | público |
| `generar_comprobante(self) -> str` | público |
| `a_dict(self)` | público |
| `restaurar_historial(self, datos, productos, pago=None)` | público |

## Local

Archivo: `modelo/pedidos.py`. Base: Pedido.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_mesa`, `_modalidad`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_pedido: int, cliente, reglas, mesa: int, fecha_registro=None)` | constructor |
| `mesa` | Propiedad; solo lectura |
| `validar_mesa(self)` | público |
| `calcular_cargos(self) -> decimal.Decimal` | público |
| `calcular_descuento(self) -> decimal.Decimal` | público |
| `mesa_ocupada(self)` | público |
| `a_dict(self)` | público |

## Llevar

Archivo: `modelo/pedidos.py`. Base: Pedido.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_modalidad`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_pedido: int, cliente, reglas, fecha_registro=None)` | constructor |
| `cantidad_envases` | Propiedad; solo lectura |
| `calcular_envases(self) -> int` | público |
| `calcular_cargos(self) -> decimal.Decimal` | público |
| `a_dict(self)` | público |

## Delivery

Archivo: `modelo/pedidos.py`. Base: Pedido.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_direccion_entrega`, `_fecha_entrega`, `_limite_retraso_min`, `_modalidad`, `_tarifas`, `_zona`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_pedido: int, cliente, reglas, zona: str, direccion_entrega: str, fecha_registro=None, limite_retraso_min=60, tarifas=None)` | constructor |
| `zona` | Propiedad; solo lectura |
| `direccion_entrega` | Propiedad; solo lectura |
| `fecha_entrega` | Propiedad; solo lectura |
| `limite_retraso_min` | Propiedad; solo lectura |
| `tarifas` | Propiedad; solo lectura |
| `calcular_cargos(self) -> decimal.Decimal` | público |
| `validar_minimo(self)` | público |
| `validar_pago(self, pago)` | público |
| `registrar_entrega(self, fecha: datetime.datetime)` | público |
| `calcular_retraso(self) -> float` | público |
| `calcular_compensacion(self) -> decimal.Decimal` | público |
| `a_dict(self)` | público |
| `restaurar_historial(self, datos, productos, pago=None)` | público |

## DetalleProducto

Archivo: `modelo/pedidos.py`. Base: object.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_cantidad`, `_fecha_precio`, `_hojas_venta`, `_id_detalle`, `_importes`, `_platos`, `_precio_unitario`, `_producto`, `_productos`, `_validar_edicion`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_detalle: int, producto, cantidad: int, fecha_precio: datetime.date, validar_edicion=None)` | constructor |
| `id_detalle` | Propiedad; solo lectura |
| `producto` | Propiedad; solo lectura |
| `cantidad` | Propiedad; solo lectura |
| `precio_unitario` | Propiedad; solo lectura |
| `fecha_precio` | Propiedad; solo lectura |
| `calcular_subtotal(self) -> decimal.Decimal` | público |
| `calcular_descuento_promocion(self) -> decimal.Decimal` | público |
| `cambiar_cantidad(self, cantidad: int)` | público |
| `contar_platos(self)` | público |
| `contar_productos(self)` | público |
| `ventas(self, criterio)` | público |
| `a_dict(self)` | público |
| `restaurar_cotizacion(self, datos)` | público |

## MetodoPago

Archivo: `modelo/pagos.py`. Base: ABC.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_fecha`, `_id_pago`, `_monto_cobrado`, `_nombre`, `_reglas`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_pago: int, reglas)` | constructor |
| `id_pago` | Propiedad; solo lectura |
| `fecha` | Propiedad; solo lectura |
| `monto_cobrado` | Propiedad; solo lectura |
| `reglas` | Propiedad; solo lectura |
| `procesar_pago(self, total: decimal.Decimal) -> decimal.Decimal` | público · abstracto |
| `permite_delivery(self) -> bool` | público |
| `_validar_cobro(self, total)` | protegido |
| `_registrar_cobro(self, monto)` | protegido |
| `generar_comprobante(self) -> str` | público |
| `a_dict(self)` | público |
| `restaurar_cobro(self, datos)` | público |

## Efectivo

Archivo: `modelo/pagos.py`. Base: MetodoPago.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_cambio`, `_monto_recibido`, `_nombre`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_pago: int, monto_recibido, reglas)` | constructor |
| `monto_recibido` | Propiedad; solo lectura |
| `cambio` | Propiedad; solo lectura |
| `procesar_pago(self, total: decimal.Decimal) -> decimal.Decimal` | público |
| `calcular_cambio(self) -> decimal.Decimal` | público |
| `generar_comprobante(self) -> str` | público |
| `a_dict(self)` | público |
| `restaurar_cobro(self, datos)` | público |

## QR

Archivo: `modelo/pagos.py`. Base: MetodoPago.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_codigo_transaccion`, `_nombre`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_pago: int, codigo_transaccion: str, reglas)` | constructor |
| `codigo_transaccion` | Propiedad; solo lectura |
| `validar_codigo(codigo: str) -> bool` | público |
| `procesar_pago(self, total: decimal.Decimal) -> decimal.Decimal` | público |
| `generar_comprobante(self) -> str` | público |
| `a_dict(self)` | público |

## Tarjeta

Archivo: `modelo/pagos.py`. Base: MetodoPago.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_comision`, `_nombre`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, id_pago: int, reglas)` | constructor |
| `comision` | Propiedad; solo lectura |
| `calcular_comision(self, total: decimal.Decimal) -> decimal.Decimal` | público |
| `procesar_pago(self, total: decimal.Decimal) -> decimal.Decimal` | público |
| `permite_delivery(self) -> bool` | público |
| `a_dict(self)` | público |

## EstadoPedido

Archivo: `modelo/pedidos.py`. Base: Enum.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): .

| Miembro declarado | Contrato |
|---|---|
| `_generate_next_value_(name, start, count, last_values)` | protegido |
| `__new__(cls, value)` | protegido |

## ReglasVariante

Archivo: `modelo/reglas.py`. Base: object.

**Campos asignados por esta clase** (incluye inicialización de campos heredados): `_base_envase`, `_codigo`, `_costo_envase`, `_decisiones`, `_descuento_fijo`, `_descuento_local`, `_dias_venta`, `_maximo_componentes`, `_minimo_componentes_descuento`, `_minimo_delivery`, `_minimo_platos_local`, `_paso_redondeo_efectivo`, `_porcentaje_combo`, `_promo_natural_martes`, `_umbral_envio_gratis`, `_zonas_gratis`.

| Miembro declarado | Contrato |
|---|---|
| `__init__(self, codigo, decisiones=None)` | constructor |
| `desde_codigo(codigo, decisiones=None)` | público |
| `codigo` | Propiedad; solo lectura |
| `decisiones` | Propiedad; solo lectura |
| `minimo_delivery` | Propiedad; solo lectura |
| `dias_venta` | Propiedad; solo lectura |
| `base_envase` | Propiedad; solo lectura |
| `descontar_combo(self, suma, cantidad)` | público |
| `validar_componentes(self, cantidad)` | público |
| `calcular_envases(self, platos, productos)` | público |
| `calcular_envio(self, zona, subtotal, tarifa)` | público |
| `descontar_local(self, subtotal, platos)` | público |
| `calcular_promocion(self, importe, cantidad, dia, es_natural, es_vaso)` | público |
| `ajustar_efectivo(self, total)` | público |
| `a_dict(self)` | público |

