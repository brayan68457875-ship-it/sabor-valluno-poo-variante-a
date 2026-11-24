"""Gestor, reportes y persistencia JSON del sistema."""
import json
import os
from datetime import date, datetime
from pathlib import Path
from types import MappingProxyType
from modelo.utilidades import dinero, texto_obligatorio
from modelo.reglas import ReglasVariante
from modelo.clientes import Cliente
from modelo.productos import Plato, Bebida, Combo
from modelo.pedidos import Local, Llevar, Delivery, EstadoPedido
from modelo.pagos import Efectivo, QR, Tarjeta

class Restaurante:
    def __init__(self, nombre='Sabor Valluno', reglas=None):
        self._nombre = texto_obligatorio(nombre)
        self._reglas = reglas or ReglasVariante.desde_codigo('A')
        self._productos, self._clientes, self._pedidos = {}, {}, {}

    @property
    def nombre(self): return self._nombre
    @property
    def reglas(self): return self._reglas
    @property
    def productos(self): return MappingProxyType(self._productos)
    @property
    def clientes(self): return MappingProxyType(self._clientes)
    @property
    def pedidos(self): return MappingProxyType(self._pedidos)

    def seleccionar_variante(self, codigo: str):
        if self._productos or self._pedidos:
            raise ValueError('Seleccione la variante antes de registrar productos y pedidos; use un contexto nuevo para otra variante.')
        self._reglas = ReglasVariante.desde_codigo(codigo, dict(self.reglas.decisiones))

    def registrar_producto(self, producto):
        if producto.id_producto in self._productos:
            raise ValueError('Ya existe ese identificador de producto.')
        if producto.reglas is not self.reglas:
            raise ValueError('El producto utiliza una configuración distinta.')
        producto.calcular_precio()
        self._productos[producto.id_producto] = producto

    def registrar_cliente(self, cliente: Cliente):
        if cliente.id_cliente in self._clientes:
            raise ValueError('Ya existe ese identificador de cliente.')
        self._clientes[cliente.id_cliente] = cliente

    def mesa_disponible(self, mesa: int) -> bool:
        return all(p.mesa_ocupada() != mesa for p in self._pedidos.values())

    def crear_pedido(self, pedido):
        if pedido.id_pedido in self._pedidos:
            raise ValueError('Ya existe ese identificador de pedido.')
        if pedido.reglas is not self.reglas:
            raise ValueError('El pedido utiliza una configuración distinta.')
        if self._clientes.get(pedido.cliente.id_cliente) is not pedido.cliente:
            raise ValueError('Registre primero el cliente en este restaurante.')
        mesa = pedido.mesa_ocupada()
        if mesa is not None and not self.mesa_disponible(mesa):
            raise ValueError('La mesa ya tiene un pedido abierto.')
        self._pedidos[pedido.id_pedido] = pedido

    def listar_menu(self, dia: str):
        return tuple(p for p in self._productos.values() if p.esta_disponible(dia))

    def siguiente_id_producto(self): return max(self._productos, default=0) + 1
    def siguiente_id_cliente(self): return max(self._clientes, default=0) + 1
    def siguiente_id_pedido(self): return max(self._pedidos, default=0) + 1
    def siguiente_id_pago(self):
        return max((p.pago.id_pago for p in self._pedidos.values() if p.pago), default=0) + 1

    def cobrar_pedido(self, id_pedido, metodo):
        for pedido in self._pedidos.values():
            if pedido.pago is not None:
                if pedido.pago.id_pago == metodo.id_pago:
                    raise ValueError('El identificador de pago ya se utilizó.')
                if getattr(pedido.pago, 'codigo_transaccion', None) == getattr(metodo, 'codigo_transaccion', ''):
                    raise ValueError('El código de transacción QR ya se utilizó.')
        return self._pedidos[id_pedido].cobrar(metodo)

    def _ventas_del_dia(self, fecha):
        # Venta = pedido cobrado en esa fecha, no pedido solo registrado.
        return tuple(p for p in self._pedidos.values()
                     if p.pago is not None and p.pago.fecha.date() == fecha
                     and p.estado != EstadoPedido.CANCELADO)

    def productos_mas_vendidos(self, fecha: date):
        acumulado = {}
        for pedido in self._ventas_del_dia(fecha):
            for detalle in pedido.items:
                for codigo, dato in detalle.ventas(self.reglas.decisiones['top_productos']).items():
                    acumulado.setdefault(codigo, {'id_producto': codigo, 'nombre': dato['nombre'], 'cantidad': 0})
                    acumulado[codigo]['cantidad'] += dato['cantidad']
        return sorted(acumulado.values(), key=lambda dato: (-dato['cantidad'], dato['id_producto']))[:3]

    def reporte_ventas(self, fecha: date) -> dict:
        resumen = {modalidad: {'pedidos': 0, 'total_pedidos': dinero(0), 'cobrado': dinero(0)} for modalidad in ('local', 'llevar', 'delivery')}
        for pedido in self._ventas_del_dia(fecha):
            dato = resumen[pedido.modalidad]
            dato['pedidos'] += 1
            dato['total_pedidos'] += pedido.calcular_total()
            dato['cobrado'] += pedido.pago.monto_cobrado
        return {'fecha': fecha.isoformat(), 'por_modalidad': resumen,
                'top_3': self.productos_mas_vendidos(fecha),
                'criterio_top': self.reglas.decisiones['top_productos'],
                'cobrado_total': sum((d['cobrado'] for d in resumen.values()), dinero(0))}

    def guardar_json(self, ruta):
        datos = {'version': 1, 'nombre': self.nombre, 'reglas': self.reglas.a_dict(),
                 'productos': [p.a_dict() for p in self._productos.values()],
                 'clientes': [c.a_dict() for c in self._clientes.values()],
                 'pedidos': [p.a_dict() for p in self._pedidos.values()]}
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = ruta.with_suffix(ruta.suffix + '.tmp')
        temporal.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding='utf-8')
        os.replace(temporal, ruta)

    @staticmethod
    def cargar_json(ruta):
        try:
            datos = json.loads(Path(ruta).read_text(encoding='utf-8'))
            return Restaurante._desde_datos(datos)
        except (KeyError, TypeError, ArithmeticError, RecursionError) as error:
            raise ValueError(f'Estructura de archivo inválida: {error}') from error

    @staticmethod
    def _desde_datos(datos):
        if datos['version'] != 1:
            raise ValueError('Versión de JSON no compatible.')
        reglas = ReglasVariante.desde_codigo(datos['reglas']['codigo'], datos['reglas']['decisiones'])
        restaurante = Restaurante(datos['nombre'], reglas)
        pendientes = list(datos['productos'])
        # Fábricas de entrada/salida: el dominio no decide por tipos de objeto.
        fabricas_productos = {
            'Plato': lambda r: Plato(r['id_producto'], r['nombre'], r['precio_base'], reglas, r['dias_venta']),
            'Bebida': lambda r: Bebida(r['id_producto'], r['nombre'], r['precio_vaso'], reglas, r['presentacion'], r['es_natural']),
            'Combo': lambda r: Combo(r['id_producto'], r['nombre'], [restaurante.productos[i] for i in r['componentes']], reglas),
        }
        while pendientes:
            sin_resolver = []
            for registro in pendientes:
                referencias = registro.get('componentes', [])
                if not all(codigo in restaurante.productos for codigo in referencias):
                    sin_resolver.append(registro)
                    continue
                producto = fabricas_productos[registro['clase']](registro)
                restaurante.registrar_producto(producto)
            if len(sin_resolver) == len(pendientes):
                raise ValueError('Productos inexistentes o ciclo entre combos en el JSON.')
            pendientes = sin_resolver
        for registro in datos['clientes']:
            restaurante.registrar_cliente(Cliente(**registro))
        for registro in datos['pedidos']:
            argumentos = (registro['id_pedido'], restaurante.clientes[registro['id_cliente']], reglas)
            fecha = datetime.fromisoformat(registro['fecha_registro'])
            fabricas_pedidos = {
                'Local': lambda: Local(*argumentos, registro['mesa'], fecha),
                'Llevar': lambda: Llevar(*argumentos, fecha),
                'Delivery': lambda: Delivery(*argumentos, registro['zona'], registro['direccion_entrega'], fecha,
                                              registro['tarifas']),
            }
            pedido = fabricas_pedidos[registro['clase']]()
            pedido.restaurar_historial(registro, restaurante.productos)
            pago_guardado = registro['pago']
            if pago_guardado is not None:
                id_pago = pago_guardado['id_pago']
                fabricas_pagos = {
                    'Efectivo': lambda: Efectivo(id_pago, pago_guardado['monto_recibido'], reglas),
                    'QR': lambda: QR(id_pago, pago_guardado['codigo_transaccion'], reglas),
                    'Tarjeta': lambda: Tarjeta(id_pago, reglas),
                }
                pago = fabricas_pagos[pago_guardado['clase']]()
                pedido.validar_pago(pago)
                esperado = pago.procesar_pago(pedido.calcular_total())
                if esperado != dinero(pago_guardado['monto_cobrado']):
                    raise ValueError('El pago almacenado no coincide con el total del pedido.')
                pago.restaurar_cobro(pago_guardado)
                for anterior in restaurante.pedidos.values():
                    if anterior.pago and anterior.pago.id_pago == pago.id_pago:
                        raise ValueError('Identificador de pago duplicado en el archivo.')
                    if anterior.pago and getattr(anterior.pago, 'codigo_transaccion', None) == getattr(pago, 'codigo_transaccion', ''):
                        raise ValueError('Código QR duplicado en el archivo.')
                pedido.restaurar_historial(registro, restaurante.productos, pago)
            restaurante.crear_pedido(pedido)
        return restaurante
