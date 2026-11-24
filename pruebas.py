"""Casos verificables con assert, sin dependencias externas.

Ejecutar sin -O: python pruebas.py
Las fechas comerciales de los casos son fijas; el reporte usa la fecha del cobro.
"""
import ast
import json
import tempfile
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path
from modelo.reglas import ReglasVariante
from modelo.productos import Producto, Plato, Bebida, Combo
from modelo.clientes import Cliente
from modelo.pedidos import Pedido, Local, Llevar, Delivery, EstadoPedido
from modelo.pagos import MetodoPago, Efectivo, QR, Tarjeta
from modelo.utilidades import dinero
from restaurante import Restaurante
from datos_demo import cargar_demostracion
LUNES = datetime(2026, 11, 23, 12, 0)
MARTES = datetime(2026, 11, 24, 12, 0)
CLIENTE = Cliente(1, 'Cliente de prueba', '71234567', 'Calle de prueba')

def debe_fallar(operacion, excepcion=ValueError):
    try:
        operacion()
    except excepcion:
        return
    raise AssertionError(f'Se esperaba {excepcion.__name__}.')

def productos(codigo='A', decisiones=None):
    reglas = ReglasVariante.desde_codigo(codigo, decisiones)
    plato = Plato(1, 'Silpancho', '35', reglas)
    bebida = Bebida(2, 'Mocochinchi', '6', reglas, es_natural=True)
    combo = Combo(3, 'Combo referencia', [plato, bebida], reglas)
    return (reglas, plato, bebida, combo)

def referencia(codigo, precio_combo, total):
    reglas, plato, bebida, combo = productos(codigo)
    pedido = Delivery(1, CLIENTE, reglas, 'Quillacollo', 'Dirección de prueba', LUNES)
    pedido.agregar_producto(combo, 2)
    assert combo.calcular_precio() == dinero(precio_combo)
    assert pedido.calcular_total() == dinero(total)
    assert pedido.contar_platos() == 2

def prueba_referencia_a():
    referencia('A', '36.90', '88.80')

def prueba_combo_anidado_y_envases():
    reglas, plato, bebida, combo = productos()
    anidado = Combo(4, 'Anidado', [combo, plato], reglas)
    pedido = Llevar(1, CLIENTE, reglas, LUNES)
    pedido.agregar_producto(anidado, 2)
    assert anidado.calcular_precio() == dinero('64.71')
    assert anidado.contar_platos() == 2
    assert pedido.calcular_envases() == 4
    assert pedido.calcular_cargos() == dinero(8)
    assert pedido.calcular_total() == dinero('137.42')

def prueba_ciclo_directo_e_indirecto():
    reglas, plato, bebida, combo = productos()
    otro = Combo(4, 'Otro', [combo, bebida], reglas)
    debe_fallar(lambda: combo.agregar_componente(combo))
    debe_fallar(lambda: combo.agregar_componente(otro))
    assert len(combo.componentes) == 2

def prueba_disponibilidad_a_y_combo():
    reglas = ReglasVariante('A')
    plato = Plato(1, 'Chicharrón', '40', reglas)
    bebida = Bebida(2, 'Agua', '5', reglas)
    combo = Combo(3, 'Dominguero', [plato, bebida], reglas)
    assert combo.esta_disponible('domingo')
    assert not combo.esta_disponible('lunes')
    pedido = Local(1, CLIENTE, reglas, 1, LUNES)
    debe_fallar(lambda: pedido.agregar_producto(combo, 1))
    debe_fallar(lambda: plato.actualizar_dias(['lunes']))

def prueba_transiciones_y_edicion():
    reglas, plato, bebida, combo = productos()
    pedido = Local(1, CLIENTE, reglas, 1, LUNES)
    debe_fallar(lambda: pedido.cambiar_estado(EstadoPedido.EN_PREPARACION))
    pedido.agregar_producto(plato, 1)
    debe_fallar(lambda: pedido.cambiar_estado(EstadoPedido.LISTO))
    pedido.cambiar_estado(EstadoPedido.EN_PREPARACION)
    debe_fallar(lambda: pedido.agregar_producto(bebida, 1))
    debe_fallar(lambda: pedido.quitar_producto(1))
    debe_fallar(lambda: pedido.items[0].cambiar_cantidad(2))
    debe_fallar(pedido.cancelar)
    pedido.cambiar_estado(EstadoPedido.LISTO)
    pedido.cambiar_estado(EstadoPedido.ENTREGADO)
    assert pedido.estado == EstadoPedido.ENTREGADO
    debe_fallar(lambda: pedido.cambiar_estado(EstadoPedido.REGISTRADO))

def prueba_cancelacion():
    reglas, plato, bebida, combo = productos()
    pedido = Llevar(1, CLIENTE, reglas, LUNES)
    pedido.cancelar()
    assert pedido.estado == EstadoPedido.CANCELADO
    debe_fallar(lambda: pedido.agregar_producto(plato, 1))
    debe_fallar(lambda: pedido.cobrar(QR(1, '1234567890', reglas)))

def prueba_validaciones():
    reglas, plato, bebida, combo = productos()
    debe_fallar(lambda: Plato(5, 'Sin precio', 0, reglas))
    debe_fallar(lambda: Plato(5, 'Infinito', 'Infinity', reglas))
    debe_fallar(lambda: Plato(5, 'No numérico', 'abc', reglas))
    debe_fallar(lambda: Cliente(1, 'X', '51234567'))
    debe_fallar(lambda: Cliente(1, 'X', '7123456'))
    debe_fallar(lambda: Local(1, CLIENTE, reglas, 16))
    pedido = Llevar(1, CLIENTE, reglas, LUNES)
    for cantidad in (0, 21, 1.5):
        debe_fallar(lambda: pedido.agregar_producto(plato, cantidad))
    pedido.agregar_producto(plato, 20)
    debe_fallar(lambda: pedido.agregar_producto(plato, 1))

def prueba_mesa_unica_y_liberacion():
    reglas = ReglasVariante('A')
    restaurante = Restaurante(reglas=reglas)
    restaurante.registrar_cliente(CLIENTE)
    pedido = Local(1, CLIENTE, reglas, 3, LUNES)
    restaurante.crear_pedido(pedido)
    debe_fallar(lambda: restaurante.crear_pedido(Local(2, CLIENTE, reglas, 3, LUNES)))
    pedido.cancelar()
    restaurante.crear_pedido(Local(2, CLIENTE, reglas, 3, LUNES))
    assert len(restaurante.pedidos) == 2

def prueba_qr_y_tarjeta():
    reglas = ReglasVariante('A')
    debe_fallar(lambda: QR(1, '123', reglas))
    debe_fallar(lambda: QR(1, 'abcdefghij', reglas))
    assert QR(1, '0123456789', reglas).procesar_pago(dinero(50)) == dinero(50)
    assert Tarjeta(2, reglas).procesar_pago(dinero(100)) == dinero(103)

def prueba_delivery_rechaza_tarjeta():
    reglas, plato, bebida, combo = productos()
    pedido = Delivery(1, CLIENTE, reglas, 'Cercado', 'Dirección', LUNES)
    pedido.agregar_producto(plato, 2)
    tarjeta = Tarjeta(1, reglas)
    debe_fallar(lambda: pedido.cobrar(tarjeta))
    assert tarjeta.fecha is None and pedido.pago is None
    pedido.cobrar(QR(2, '1234567890', reglas))
    debe_fallar(lambda: pedido.cobrar(Efectivo(3, 100, reglas)))

def prueba_pedido_cobrado_inmutable():
    reglas, plato, bebida, combo = productos()
    pedido = Llevar(1, CLIENTE, reglas, LUNES)
    pedido.agregar_producto(plato, 1)
    pedido.cobrar(Efectivo(1, 100, reglas))
    debe_fallar(pedido.cancelar)
    debe_fallar(lambda: pedido.items[0].cambiar_cantidad(2))
    debe_fallar(lambda: pedido.agregar_producto(bebida, 1))

def prueba_reporte_y_top():
    restaurante = Restaurante(reglas=ReglasVariante('A'))
    cargar_demostracion(restaurante)
    pedido = Llevar(1, restaurante.clientes[1], restaurante.reglas, LUNES)
    pedido.agregar_producto(restaurante.productos[8], 2)
    restaurante.crear_pedido(pedido)
    restaurante.cobrar_pedido(1, Efectivo(1, 100, restaurante.reglas))
    pendiente = Llevar(2, restaurante.clientes[1], restaurante.reglas, LUNES)
    pendiente.agregar_producto(restaurante.productos[1], 10)
    restaurante.crear_pedido(pendiente)
    reporte = restaurante.reporte_ventas(date.today())
    assert reporte['por_modalidad']['llevar']['pedidos'] == 1
    assert reporte['cobrado_total'] == dinero('77.80')
    assert reporte['top_3'][0]['id_producto'] == 8
    assert reporte['top_3'][0]['cantidad'] == 2

def prueba_reporte_hojas_y_empates():
    reglas = ReglasVariante('A', {'top_productos': 'hojas'})
    restaurante = Restaurante(reglas=reglas)
    cargar_demostracion(restaurante)
    pedido = Local(1, restaurante.clientes[1], reglas, 1, LUNES)
    pedido.agregar_producto(restaurante.productos[9], 1)
    restaurante.crear_pedido(pedido)
    restaurante.cobrar_pedido(1, QR(1, '0000000001', reglas))
    top = restaurante.productos_mas_vendidos(date.today())
    assert [r['id_producto'] for r in top] == [1, 2, 5]
    assert [r['cantidad'] for r in top] == [1, 1, 1]

def prueba_precio_historico():
    reglas, plato, bebida, combo = productos()
    pedido = Llevar(1, CLIENTE, reglas, LUNES)
    pedido.agregar_producto(combo, 1)
    anterior = pedido.calcular_total()
    plato.precio_base = 100
    combo.agregar_componente(plato)
    assert pedido.calcular_total() == anterior
    assert pedido.contar_platos() == 1
    pedido.items[0].cambiar_cantidad(2)
    assert pedido.calcular_total() == anterior * 2

def prueba_colecciones_protegidas():
    reglas, plato, bebida, combo = productos()
    pedido = Llevar(1, CLIENTE, reglas, LUNES)
    pedido.agregar_producto(plato, 1)
    debe_fallar(lambda: pedido.items.append('x'), AttributeError)
    debe_fallar(lambda: combo.componentes.append(plato), AttributeError)
    debe_fallar(lambda: setattr(pedido, 'estado', EstadoPedido.CANCELADO), AttributeError)
    restaurante = Restaurante(reglas=reglas)
    debe_fallar(lambda: restaurante.productos.__setitem__(1, plato), AttributeError)

def prueba_json_corrupto_y_ciclo():
    with tempfile.TemporaryDirectory() as carpeta:
        restaurante = Restaurante()
        cargar_demostracion(restaurante)
        ruta = Path(carpeta) / 'malo.json'
        restaurante.guardar_json(ruta)
        datos = json.loads(ruta.read_text(encoding='utf-8'))
        datos['productos'][-1]['componentes'] = [9, 1]
        ruta.write_text(json.dumps(datos), encoding='utf-8')
        debe_fallar(lambda: Restaurante.cargar_json(ruta))

def prueba_ids_duplicados_y_pago_reutilizado():
    restaurante = Restaurante()
    cargar_demostracion(restaurante)
    debe_fallar(lambda: restaurante.registrar_cliente(restaurante.clientes[1]))
    debe_fallar(lambda: restaurante.registrar_producto(restaurante.productos[1]))
    for numero in (1, 2):
        pedido = Llevar(numero, restaurante.clientes[1], restaurante.reglas, LUNES)
        pedido.agregar_producto(restaurante.productos[1], 1)
        restaurante.crear_pedido(pedido)
    restaurante.cobrar_pedido(1, QR(1, '1111111111', restaurante.reglas))
    debe_fallar(lambda: restaurante.cobrar_pedido(2, QR(2, '1111111111', restaurante.reglas)))
    debe_fallar(lambda: restaurante.cobrar_pedido(2, Efectivo(1, 100, restaurante.reglas)))

def prueba_abstractas():
    debe_fallar(lambda: Producto(1, 'X', ReglasVariante('A')), TypeError)
    debe_fallar(lambda: Pedido(1, CLIENTE, ReglasVariante('A')), TypeError)
    debe_fallar(lambda: MetodoPago(1, ReglasVariante('A')), TypeError)

def prueba_importe_fuera_de_precision():
    debe_fallar(lambda: dinero('1e100'))

def prueba_polimorfismo_sin_comprobar_tipos():
    base = Path(__file__).resolve().parent
    for archivo in ['modelo/productos.py', 'modelo/pedidos.py']:
        arbol = ast.parse((base / archivo).read_text(encoding='utf-8'))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name):
                assert nodo.func.id not in ('type', 'isinstance'), archivo

def ejecutar():
    if not __debug__:
        raise RuntimeError('Ejecute sin -O: las pruebas dependen de assert.')
    pruebas = [(nombre, funcion) for nombre, funcion in globals().items() if nombre.startswith('prueba_')]
    aprobadas, fallidas = (0, [])
    for nombre, funcion in pruebas:
        try:
            funcion()
            aprobadas += 1
            print('OK  ', nombre)
        except Exception as error:
            fallidas.append(nombre)
            print('FALLO', nombre, repr(error))
    print(f'\nResultado: {aprobadas}/{len(pruebas)} casos aprobados.')
    if fallidas:
        raise AssertionError('Fallaron: ' + ', '.join(fallidas))

def prueba_jarra_a_sin_promocion():
    reglas, plato, bebida, combo = productos()
    jarra = Bebida(4, 'Jarra', 6, reglas, 'jarra', True)
    assert jarra.calcular_precio() == dinero(18)
    assert bebida.calcular_importe(2, 'martes') == dinero(12)

def prueba_envases_a_solo_platos():
    reglas, plato, bebida, combo = productos()
    pedido = Llevar(1, CLIENTE, reglas, LUNES)
    pedido.agregar_producto(bebida, 3)
    assert pedido.calcular_cargos() == dinero(0)
    pedido.agregar_producto(combo, 2)
    assert pedido.cantidad_envases == 2
    assert pedido.calcular_cargos() == dinero(4)

def prueba_umbral_a_cercado():
    reglas = ReglasVariante('A')
    for subtotal, envio in [('149.99', '8'), ('150', '0'), ('150.01', '0')]:
        pedido = Delivery(1, CLIENTE, reglas, 'Cercado', 'Dirección', LUNES)
        pedido.agregar_producto(Plato(1, 'Importe de prueba', subtotal, reglas), 1)
        assert pedido.calcular_cargos() == dinero(envio)

def prueba_otras_zonas_a_siempre_cobran():
    reglas = ReglasVariante('A')
    for zona, tarifa in [('Quillacollo', 15), ('Sacaba', 15), ('Vinto', 20)]:
        pedido = Delivery(1, CLIENTE, reglas, zona, 'Dirección', LUNES)
        pedido.agregar_producto(Plato(1, 'Importe alto', 500, reglas), 1)
        assert pedido.calcular_cargos() == dinero(tarifa)

def prueba_minimo_a_40():
    reglas = ReglasVariante('A')
    pedido = Delivery(1, CLIENTE, reglas, 'Cercado', 'Dirección', LUNES)
    pedido.agregar_producto(Plato(1, 'Bajo', '39.99', reglas), 1)
    debe_fallar(lambda: pedido.cambiar_estado(EstadoPedido.EN_PREPARACION))
    debe_fallar(lambda: pedido.cobrar(QR(1, '1234567890', reglas)))
    pedido.quitar_producto(1)
    pedido.agregar_producto(Plato(2, 'Justo', 40, reglas), 1)
    pedido.cambiar_estado(EstadoPedido.EN_PREPARACION)
    assert pedido.estado == EstadoPedido.EN_PREPARACION

def prueba_efectivo_a_sin_redondeo_extra():
    reglas = ReglasVariante('A')
    pago = Efectivo(1, 100, reglas)
    assert pago.procesar_pago(dinero('88.80')) == dinero('88.80')
    assert pago.cambio == dinero('11.20')
    debe_fallar(lambda: pago.procesar_pago(dinero(10)))
    debe_fallar(lambda: Efectivo(2, 10, reglas).procesar_pago(dinero(11)))

def prueba_a_rechaza_otras_variantes():
    for codigo in 'BCDEF':
        debe_fallar(lambda: ReglasVariante(codigo))

def prueba_json_a_tres_medios_y_cotizacion():
    with tempfile.TemporaryDirectory() as carpeta:
        fabricas = [lambda r: Efectivo(1, 100, r), lambda r: QR(1, '0123456789', r), lambda r: Tarjeta(1, r)]
        for fabrica in fabricas:
            restaurante = Restaurante()
            cargar_demostracion(restaurante)
            pedido = Local(1, restaurante.clientes[1], restaurante.reglas, 1, LUNES)
            pedido.agregar_producto(restaurante.productos[8], 2)
            restaurante.crear_pedido(pedido)
            restaurante.cobrar_pedido(1, fabrica(restaurante.reglas))
            restaurante.productos[1].precio_base = 50
            ruta = Path(carpeta) / 'a.json'
            restaurante.guardar_json(ruta)
            nuevo = Restaurante.cargar_json(ruta)
            assert nuevo.reglas.codigo == 'A'
            assert nuevo.pedidos[1].calcular_total() == dinero('73.80')
            assert nuevo.pedidos[1].generar_comprobante() == pedido.generar_comprobante()

def prueba_delivery_a_entrega_json():
    with tempfile.TemporaryDirectory() as carpeta:
        restaurante = Restaurante()
        cargar_demostracion(restaurante)
        pedido = Delivery(1, restaurante.clientes[1], restaurante.reglas, 'Quillacollo', 'Dirección', LUNES)
        pedido.agregar_producto(restaurante.productos[8], 2)
        restaurante.crear_pedido(pedido)
        restaurante.cobrar_pedido(1, QR(1, '1234567890', restaurante.reglas))
        pedido.cambiar_estado(EstadoPedido.EN_PREPARACION)
        pedido.cambiar_estado(EstadoPedido.LISTO)
        pedido.registrar_entrega(LUNES + timedelta(minutes=61))
        ruta = Path(carpeta) / 'delivery_a.json'
        restaurante.guardar_json(ruta)
        nuevo = Restaurante.cargar_json(ruta)
        assert nuevo.pedidos[1].fecha_entrega == pedido.fecha_entrega
        assert nuevo.reporte_ventas(date.today()) == restaurante.reporte_ventas(date.today())

def prueba_combo_a_minimo_sin_maximo_c():
    reglas, plato, bebida, combo = productos()
    debe_fallar(lambda: Combo(4, 'Insuficiente', [plato], reglas))
    debe_fallar(lambda: combo.quitar_componente(plato))
    for _ in range(4):
        combo.agregar_componente(plato)
    assert len(combo.componentes) == 6
def prueba_configuracion_antigua_no_activa_reglas_ajenas():
    decisiones = {'conteo_productos_c': 'unidad', 'promo_dentro_combos': True}
    reglas, plato, bebida, combo = productos('A', decisiones)
    assert combo.contar_productos() == 2
    assert combo.calcular_importe(2, 'martes') == dinero('73.80')
    pedido = Llevar(1, CLIENTE, reglas, MARTES)
    pedido.agregar_producto(combo, 2)
    assert pedido.calcular_envases() == 2
    assert pedido.calcular_total() == dinero('77.80')
    assert set(reglas.decisiones) == {'top_productos'}


def prueba_json_legacy_conserva_cobro_variante_a():
    with tempfile.TemporaryDirectory() as carpeta:
        restaurante = Restaurante()
        cargar_demostracion(restaurante)
        pedido = Llevar(1, restaurante.clientes[1], restaurante.reglas, LUNES)
        pedido.agregar_producto(restaurante.productos[8], 2)
        restaurante.crear_pedido(pedido)
        restaurante.cobrar_pedido(1, Efectivo(1, 100, restaurante.reglas))
        ruta = Path(carpeta) / 'anterior.json'
        restaurante.guardar_json(ruta)
        datos = json.loads(ruta.read_text(encoding='utf-8'))
        datos['reglas']['decisiones'].update({'conteo_productos_c': 'unidad', 'promo_dentro_combos': True})
        ruta.write_text(json.dumps(datos), encoding='utf-8')
        nuevo = Restaurante.cargar_json(ruta)
        assert nuevo.pedidos[1].calcular_total() == dinero('77.80')
        assert nuevo.pedidos[1].pago.monto_cobrado == dinero('77.80')
        assert nuevo.pedidos[1].pago.cambio == dinero('22.20')
        assert set(nuevo.reglas.decisiones) == {'top_productos'}


if __name__ == '__main__':
    ejecutar()
