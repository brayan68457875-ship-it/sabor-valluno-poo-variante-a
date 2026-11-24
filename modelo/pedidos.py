from abc import ABC, abstractmethod
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from .utilidades import dinero, entero, dia_fecha, texto_obligatorio

class EstadoPedido(Enum):
    REGISTRADO = 'REGISTRADO'
    EN_PREPARACION = 'EN_PREPARACION'
    LISTO = 'LISTO'
    ENTREGADO = 'ENTREGADO'
    CANCELADO = 'CANCELADO'

class DetalleProducto:

    def __init__(self, id_detalle: int, producto, cantidad: int, fecha_precio: date, validar_edicion=None):
        self._id_detalle = entero(id_detalle)
        self._producto = producto
        self._fecha_precio = fecha_precio
        self._precio_unitario = producto.calcular_precio()
        self._validar_edicion = validar_edicion or (lambda: None)
        self._importes = tuple((producto.calcular_importe(n, dia_fecha(fecha_precio)) for n in range(1, 21)))
        self._platos = producto.contar_platos()
        self._productos = producto.contar_productos()
        self._hojas_venta = producto.desglosar_ventas(1)
        self.cambiar_cantidad(cantidad)

    @property
    def id_detalle(self):
        return self._id_detalle

    @property
    def producto(self):
        return self._producto

    @property
    def cantidad(self):
        return self._cantidad

    @property
    def precio_unitario(self):
        return self._precio_unitario

    @property
    def fecha_precio(self):
        return self._fecha_precio

    def calcular_subtotal(self) -> Decimal:
        return self._importes[self.cantidad - 1]

    def calcular_descuento_promocion(self) -> Decimal:
        return dinero(self.precio_unitario * self.cantidad - self.calcular_subtotal())

    def cambiar_cantidad(self, cantidad: int):
        self._validar_edicion()
        self._cantidad = entero(cantidad, 1, 20)

    def contar_platos(self):
        return self._platos * self.cantidad

    def contar_productos(self):
        return self._productos * self.cantidad

    def ventas(self, criterio):
        if criterio == 'lineas':
            return {self.producto.id_producto: {'nombre': self.producto.nombre, 'cantidad': self.cantidad}}
        return {codigo: {'nombre': dato['nombre'], 'cantidad': dato['cantidad'] * self.cantidad} for codigo, dato in self._hojas_venta.items()}

    def a_dict(self):
        return {'id_detalle': self.id_detalle, 'id_producto': self.producto.id_producto, 'cantidad': self.cantidad, 'precio_unitario': str(self.precio_unitario), 'fecha_precio': self.fecha_precio.isoformat(), 'importes': [str(v) for v in self._importes], 'platos': self._platos, 'productos': self._productos, 'hojas_venta': self._hojas_venta}

    def restaurar_cotizacion(self, datos):
        self._precio_unitario = dinero(datos['precio_unitario'])
        importes = tuple((dinero(n) for n in datos['importes']))
        if self._precio_unitario <= 0 or len(importes) != 20 or any((n <= 0 for n in importes)):
            raise ValueError('Cotización de detalle inválida.')
        self._importes = importes
        self._platos = entero(datos['platos'], 0)
        self._productos = entero(datos['productos'], 1)
        self._hojas_venta = {int(k): v for k, v in datos['hojas_venta'].items()}

class Pedido(ABC):

    def __init__(self, id_pedido: int, cliente, reglas, fecha_registro=None):
        self._id_pedido = entero(id_pedido)
        self._cliente = cliente
        self._reglas = reglas
        self._fecha_registro = fecha_registro or datetime.now()
        self._estado = EstadoPedido.REGISTRADO
        self._items = []
        self._pago = None
        self._modalidad = ''

    @property
    def id_pedido(self):
        return self._id_pedido

    @property
    def cliente(self):
        return self._cliente

    @property
    def reglas(self):
        return self._reglas

    @property
    def fecha_registro(self):
        return self._fecha_registro

    @property
    def estado(self):
        return self._estado

    @property
    def pago(self):
        return self._pago

    @property
    def modalidad(self):
        return self._modalidad

    @property
    def items(self):
        return tuple(self._items)

    def items_lectura(self):
        return self.items

    def _validar_edicion(self):
        if self.estado != EstadoPedido.REGISTRADO or self.pago is not None:
            raise ValueError('Solo se edita un pedido REGISTRADO y sin cobrar.')

    def agregar_producto(self, producto, cantidad: int):
        self._validar_edicion()
        cantidad = entero(cantidad, 1, 20)
        if producto.reglas is not self.reglas:
            raise ValueError('Producto y pedido deben compartir las mismas reglas.')
        if not producto.esta_disponible(dia_fecha(self.fecha_registro)):
            raise ValueError('Producto no disponible el día del pedido.')
        for detalle in self._items:
            if detalle.producto.id_producto == producto.id_producto:
                detalle.cambiar_cantidad(detalle.cantidad + cantidad)
                return
        numero = max((d.id_detalle for d in self._items), default=0) + 1
        self._items.append(DetalleProducto(numero, producto, cantidad, self.fecha_registro.date(), self._validar_edicion))

    def quitar_producto(self, id_producto: int):
        self._validar_edicion()
        for indice, detalle in enumerate(self._items):
            if detalle.producto.id_producto == id_producto:
                self._items.pop(indice)
                return
        raise ValueError('El producto no está en el pedido.')

    def calcular_subtotal(self) -> Decimal:
        return dinero(sum((d.calcular_subtotal() for d in self._items), dinero(0)))

    def calcular_descuento(self) -> Decimal:
        return dinero(0)

    @abstractmethod
    def calcular_cargos(self) -> Decimal:
        pass

    def contar_platos(self) -> int:
        return sum((d.contar_platos() for d in self._items))

    def contar_productos(self) -> int:
        return sum((d.contar_productos() for d in self._items))

    def validar_minimo(self):
        pass

    def calcular_total(self) -> Decimal:
        return dinero(self.calcular_subtotal() - self.calcular_descuento() + self.calcular_cargos())

    def _validar_confirmacion(self):
        if not self._items:
            raise ValueError('El pedido debe contener al menos un producto.')
        self.validar_minimo()

    def _transicionar(self, nuevo):
        if nuevo not in self.siguientes_estados():
            raise ValueError(f'Transición inválida: {self.estado.value} -> {nuevo.value}.')
        if nuevo == EstadoPedido.CANCELADO:
            self._validar_edicion()
        else:
            self._validar_confirmacion()
        self._estado = nuevo

    def siguientes_estados(self):
        return {EstadoPedido.REGISTRADO: (EstadoPedido.EN_PREPARACION, EstadoPedido.CANCELADO), EstadoPedido.EN_PREPARACION: (EstadoPedido.LISTO,), EstadoPedido.LISTO: (EstadoPedido.ENTREGADO,), EstadoPedido.ENTREGADO: (), EstadoPedido.CANCELADO: ()}[self.estado]

    def cambiar_estado(self, nuevo: EstadoPedido):
        if nuevo == EstadoPedido.ENTREGADO:
            self.registrar_entrega(datetime.now())
        else:
            self._transicionar(nuevo)

    def cancelar(self):
        self.cambiar_estado(EstadoPedido.CANCELADO)

    def registrar_entrega(self, fecha: datetime):
        self._transicionar(EstadoPedido.ENTREGADO)

    def validar_pago(self, pago):
        if pago.reglas is not self.reglas:
            raise ValueError('El pago debe utilizar las reglas del pedido.')

    def cobrar(self, metodo) -> Decimal:
        if self.estado == EstadoPedido.CANCELADO or self.pago is not None:
            raise ValueError('El pedido está cancelado o ya fue cobrado.')
        self._validar_confirmacion()
        self.validar_pago(metodo)
        monto = metodo.procesar_pago(self.calcular_total())
        self._pago = metodo
        return monto

    def mesa_ocupada(self):
        return None

    def generar_comprobante(self) -> str:
        lineas = [f'SABOR VALLUNO | Pedido #{self.id_pedido} | {self.modalidad}', f'Cliente: {self.cliente.nombre} | Tel.: {self.cliente.telefono}', f"Registro: {self.fecha_registro.isoformat(sep=' ', timespec='minutes')}", f'Estado: {self.estado.value} | Variante: {self.reglas.codigo}', 'En la variante A, los precios de combos ya incluyen el 10 % de descuento.']
        for detalle in self.items:
            lineas.append(f'{detalle.cantidad} x {detalle.producto.nombre} @ Bs {detalle.precio_unitario:.2f} | promoción -{detalle.calcular_descuento_promocion():.2f} | Bs {detalle.calcular_subtotal():.2f}')
        lineas += [f'Subtotal: Bs {self.calcular_subtotal():.2f}', f'Descuento adicional del pedido: Bs {self.calcular_descuento():.2f}', f'Cargos: Bs {self.calcular_cargos():.2f}', f'Total: Bs {self.calcular_total():.2f}']
        if self.pago:
            lineas += [self.pago.generar_comprobante(), f'Ajuste de cobro: Bs {self.pago.monto_cobrado - self.calcular_total():.2f}']
        elif self.estado == EstadoPedido.CANCELADO:
            lineas.append('PEDIDO CANCELADO. No corresponde cobrar.')
        else:
            lineas.append('PENDIENTE DE PAGO. Simulación académica; no es factura fiscal.')
        return '\n'.join(lineas)

    def a_dict(self):
        return {'id_pedido': self.id_pedido, 'id_cliente': self.cliente.id_cliente, 'fecha_registro': self.fecha_registro.isoformat(), 'estado': self.estado.value, 'items': [d.a_dict() for d in self.items], 'pago': None if self.pago is None else self.pago.a_dict()}

    def restaurar_historial(self, datos, productos, pago=None):
        detalles = []
        vistos = set()
        for registro in datos['items']:
            if registro['id_producto'] in vistos:
                raise ValueError('Detalle duplicado en el archivo.')
            vistos.add(registro['id_producto'])
            detalle = DetalleProducto(registro['id_detalle'], productos[registro['id_producto']], registro['cantidad'], date.fromisoformat(registro['fecha_precio']))
            detalle.restaurar_cotizacion(registro)
            detalle._validar_edicion = self._validar_edicion
            detalles.append(detalle)
        self._items = detalles
        estado = EstadoPedido(datos['estado'])
        if estado not in (EstadoPedido.REGISTRADO, EstadoPedido.CANCELADO) or pago is not None:
            self._validar_confirmacion()
        if estado == EstadoPedido.CANCELADO and pago is not None:
            raise ValueError('Un pedido cancelado no puede tener un pago.')
        self._estado, self._pago = (estado, pago)

class Local(Pedido):

    def __init__(self, id_pedido: int, cliente, reglas, mesa: int, fecha_registro=None):
        super().__init__(id_pedido, cliente, reglas, fecha_registro)
        self._modalidad = 'local'
        self._mesa = entero(mesa, 1, 15)
        self.validar_mesa()

    @property
    def mesa(self):
        return self._mesa

    def validar_mesa(self):
        entero(self.mesa, 1, 15)

    def calcular_cargos(self) -> Decimal:
        return dinero(0)

    def calcular_descuento(self) -> Decimal:
        return self.reglas.descontar_local(self.calcular_subtotal(), self.contar_platos())

    def mesa_ocupada(self):
        return None if self.estado in (EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO) else self.mesa

    def a_dict(self):
        return dict(super().a_dict(), clase='Local', mesa=self.mesa)

class Llevar(Pedido):

    def __init__(self, id_pedido: int, cliente, reglas, fecha_registro=None):
        super().__init__(id_pedido, cliente, reglas, fecha_registro)
        self._modalidad = 'llevar'

    @property
    def cantidad_envases(self):
        return self.calcular_envases()

    def calcular_envases(self) -> int:
        return self.contar_platos()

    def calcular_cargos(self) -> Decimal:
        return self.reglas.calcular_envases(self.contar_platos(), self.contar_productos())

    def a_dict(self):
        return dict(super().a_dict(), clase='Llevar')

class Delivery(Pedido):
    TARIFAS = {'Cercado': '8', 'Quillacollo': '15', 'Sacaba': '15', 'Vinto': '20'}

    def __init__(self, id_pedido: int, cliente, reglas, zona: str, direccion_entrega: str, fecha_registro=None, tarifas=None):
        super().__init__(id_pedido, cliente, reglas, fecha_registro)
        self._modalidad = 'delivery'
        self._tarifas = {z: dinero(v) for z, v in (tarifas or self.TARIFAS).items()}
        if any((v < 0 for v in self._tarifas.values())) or zona not in self._tarifas:
            raise ValueError('Zona desconocida o tarifa inválida.')
        self._zona = zona
        self._direccion_entrega = texto_obligatorio(direccion_entrega)
        self._fecha_entrega = None

    @property
    def zona(self):
        return self._zona

    @property
    def direccion_entrega(self):
        return self._direccion_entrega

    @property
    def fecha_entrega(self):
        return self._fecha_entrega

    @property
    def tarifas(self):
        return MappingProxyType(self._tarifas)

    def calcular_cargos(self) -> Decimal:
        return self.reglas.calcular_envio(self.zona, self.calcular_subtotal(), self.tarifas[self.zona])

    def validar_minimo(self):
        if self.calcular_subtotal() < self.reglas.minimo_delivery:
            raise ValueError(f'El subtotal mínimo de delivery es Bs {self.reglas.minimo_delivery:.2f}.')

    def validar_pago(self, pago):
        super().validar_pago(pago)
        if not pago.permite_delivery():
            raise ValueError('Delivery solo admite métodos habilitados: Efectivo o QR.')

    def registrar_entrega(self, fecha: datetime):
        if fecha < self.fecha_registro:
            raise ValueError('La entrega no puede ser anterior al registro.')
        self._transicionar(EstadoPedido.ENTREGADO)
        self._fecha_entrega = fecha

    def a_dict(self):
        return dict(super().a_dict(), clase='Delivery', zona=self.zona, direccion_entrega=self.direccion_entrega, fecha_entrega=None if self.fecha_entrega is None else self.fecha_entrega.isoformat(), tarifas={z: str(v) for z, v in self.tarifas.items()})

    def restaurar_historial(self, datos, productos, pago=None):
        super().restaurar_historial(datos, productos, pago)
        self._fecha_entrega = None if datos['fecha_entrega'] is None else datetime.fromisoformat(datos['fecha_entrega'])
        if (self.estado == EstadoPedido.ENTREGADO) != (self.fecha_entrega is not None):
            raise ValueError('Estado y fecha de entrega inconsistentes.')
        if self.fecha_entrega is not None and self.fecha_entrega < self.fecha_registro:
            raise ValueError('Fecha de entrega anterior al registro.')
        if pago is not None:
            self.validar_pago(pago)
