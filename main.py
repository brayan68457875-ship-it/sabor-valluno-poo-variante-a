"""Aplicación de consola. Ejecutar: python main.py"""
import argparse
import json
from datetime import date, datetime
from pathlib import Path
from restaurante import Restaurante
from datos_demo import cargar_demostracion
from modelo.reglas import ReglasVariante
from modelo.productos import Plato, Bebida, Combo
from modelo.clientes import Cliente
from modelo.pedidos import Local, Llevar, Delivery, EstadoPedido
from modelo.pagos import Efectivo, QR, Tarjeta
from modelo.utilidades import entero, dia_fecha

BASE = Path(__file__).resolve().parent

def pedir_entero(mensaje): return entero(input(mensaje).strip())

def registrar_producto(restaurante):
    opcion = input('Producto: 1 Plato, 2 Bebida, 3 Combo: ').strip()
    identificador = restaurante.siguiente_id_producto()
    nombre = input('Nombre: ')
    reglas = restaurante.reglas
    def plato():
        precio = input('Precio en Bs: ')
        dias = input('Días separados por coma (vacío = todos o restricción de variante): ').strip()
        return Plato(identificador, nombre, precio, reglas, None if not dias else dias.split(','))
    def bebida():
        precio = input('Precio por vaso en Bs: ')
        presentacion = input('Presentación (vaso/jarra): ').strip().lower()
        natural = input('¿Refresco natural? (s/n): ').strip().lower() == 's'
        return Bebida(identificador, nombre, precio, reglas, presentacion, natural)
    def combo():
        mostrar_productos(restaurante)
        codigos = [int(c.strip()) for c in input('IDs de al menos 2 componentes, separados por coma: ').split(',')]
        return Combo(identificador, nombre, [restaurante.productos[i] for i in codigos], reglas)
    fabricas = {'1': plato, '2': bebida, '3': combo}
    if opcion not in fabricas:
        raise ValueError('Tipo de producto inválido.')
    producto = fabricas[opcion]()
    restaurante.registrar_producto(producto)
    print(f'Producto #{identificador} registrado. Precio: Bs {producto.calcular_precio():.2f}')

def mostrar_productos(restaurante, disponibles=None):
    productos = restaurante.productos.values() if disponibles is None else disponibles
    for producto in productos:
        print(f'{producto.id_producto}: {producto.nombre} | Bs {producto.calcular_precio():.2f}')

def menu_disponible(restaurante):
    dia = input('Día (vacío = hoy): ').strip() or dia_fecha(date.today())
    print(f'Precios unitarios antes de promociones por cantidad | Variante {restaurante.reglas.codigo}')
    mostrar_productos(restaurante, restaurante.listar_menu(dia))

def registrar_cliente(restaurante):
    cliente = Cliente(restaurante.siguiente_id_cliente(), input('Nombre del cliente: '),
                      input('Teléfono: '), input('Dirección (opcional): '))
    restaurante.registrar_cliente(cliente)
    print(f'Cliente #{cliente.id_cliente} registrado.')

def elegir_pedido(restaurante):
    for pedido in restaurante.pedidos.values():
        print(f'{pedido.id_pedido}: {pedido.modalidad} | {pedido.cliente.nombre} | {pedido.estado.value}')
    return restaurante.pedidos[pedir_entero('ID del pedido: ')]

def crear_pedido(restaurante):
    for cliente in restaurante.clientes.values():
        print(f'{cliente.id_cliente}: {cliente.nombre}')
    cliente = restaurante.clientes[pedir_entero('ID de cliente: ')]
    identificador = restaurante.siguiente_id_pedido()
    opcion = input('Modalidad: 1 Local, 2 Llevar, 3 Delivery: ').strip()
    reglas = restaurante.reglas
    fabricas = {
        '1': lambda: Local(identificador, cliente, reglas, pedir_entero('Mesa (1–15): ')),
        '2': lambda: Llevar(identificador, cliente, reglas),
        '3': lambda: Delivery(identificador, cliente, reglas,
                               input('Zona (Cercado/Quillacollo/Sacaba/Vinto): ').strip().title(),
                               input('Dirección de entrega: ')),
    }
    if opcion not in fabricas: raise ValueError('Modalidad inválida.')
    restaurante.crear_pedido(fabricas[opcion]())
    print(f'Pedido #{identificador} creado. Agregue productos con la opción 6.')

def editar_pedido(restaurante):
    pedido = elegir_pedido(restaurante)
    opcion = input('1 Agregar producto | 2 Quitar producto: ').strip()
    if opcion == '1':
        mostrar_productos(restaurante)
        producto = restaurante.productos[pedir_entero('ID del producto: ')]
        pedido.agregar_producto(producto, pedir_entero('Cantidad (1–20): '))
    elif opcion == '2':
        pedido.quitar_producto(pedir_entero('ID del producto a quitar: '))
    else: raise ValueError('Opción de edición inválida.')
    print(pedido.generar_comprobante())

def cambiar_estado(restaurante):
    pedido = elegir_pedido(restaurante)
    print('Siguientes estados:', ', '.join(e.value for e in pedido.siguientes_estados()))
    estado = EstadoPedido(input('Nuevo estado: ').strip().upper())
    pedido.cambiar_estado(estado)
    print(pedido.generar_comprobante())

def cobrar(restaurante):
    pedido = elegir_pedido(restaurante)
    print(pedido.generar_comprobante())
    opcion = input('Pago: 1 Efectivo, 2 QR, 3 Tarjeta: ').strip()
    identificador = restaurante.siguiente_id_pago()
    reglas = pedido.reglas
    fabricas = {
        '1': lambda: Efectivo(identificador, input('Monto recibido en Bs: '), reglas),
        '2': lambda: QR(identificador, input('Código de transacción de 10 dígitos: '), reglas),
        '3': lambda: Tarjeta(identificador, reglas),
    }
    if opcion not in fabricas: raise ValueError('Método inválido.')
    restaurante.cobrar_pedido(pedido.id_pedido, fabricas[opcion]())
    print(pedido.generar_comprobante())

def reporte(restaurante):
    texto = input('Fecha AAAA-MM-DD (vacío = hoy): ').strip()
    fecha = date.fromisoformat(texto) if texto else date.today()
    print(json.dumps(restaurante.reporte_ventas(fecha), ensure_ascii=False, indent=2, default=str))

def guardar(restaurante):
    texto = input('Ruta JSON (vacío = datos/restaurante.json): ').strip()
    ruta = Path(texto) if texto else BASE / 'datos' / 'restaurante.json'
    restaurante.guardar_json(ruta)
    print(f'Guardado en {ruta.resolve()}')

def editar_combo(restaurante):
    mostrar_productos(restaurante)
    combo = restaurante.productos[pedir_entero('ID del combo: ')]
    accion = input('1 Agregar componente | 2 Quitar componente: ').strip()
    operaciones = {'1': 'agregar_componente', '2': 'quitar_componente'}
    if accion not in operaciones: raise ValueError('Acción inválida.')
    operacion = getattr(combo, operaciones[accion], None)
    if operacion is None: raise ValueError('El producto elegido no admite edición de componentes.')
    componente = restaurante.productos[pedir_entero('ID del componente: ')]
    operacion(componente)
    print(f'Combo actualizado: Bs {combo.calcular_precio():.2f}. Las cotizaciones de pedidos existentes se conservan.')

def principal():
    analizador = argparse.ArgumentParser(description='Sistema académico Sabor Valluno, solo biblioteca estándar.')
    analizador.add_argument('--variante', choices=['A'], help='Variante asignada A (única admitida en esta entrega).')
    analizador.add_argument('--demo', action='store_true', help='Cargar menú y cliente ficticios.')
    analizador.add_argument('--cargar', help='Ruta JSON existente.')
    argumentos = analizador.parse_args()
    configuracion = json.loads((BASE / 'configuracion.json').read_text(encoding='utf-8'))
    if argumentos.cargar:
        restaurante = Restaurante.cargar_json(argumentos.cargar)
    else:
        variante = argumentos.variante or configuracion['estudiante']['variante_asignada']
        restaurante = Restaurante(reglas=ReglasVariante.desde_codigo(variante, configuracion['decisiones_modelado']))
        if argumentos.demo: cargar_demostracion(restaurante)
    print('\nSABOR VALLUNO | Sistema de consola | Simulación académica')
    print('Estudiante: Brayan Saravia Garay | Variante asignada:', restaurante.reglas.codigo)
    if not restaurante.reglas.decisiones['consultas_confirmadas']:
        print('Hay decisiones propuestas pendientes de consulta. Revise docs/acta_consultas.md y configuracion.json.')
    while True:
        print('\n1 Registrar producto/combo   2 Menú disponible   3 Registrar cliente')
        print('4 Ver clientes              5 Crear pedido      6 Agregar/quitar productos')
        print('7 Detalle de pedido         8 Cambiar estado    9 Cobrar')
        print('10 Reporte diario           11 Guardar JSON     12 Cargar JSON')
        print('13 Cargar datos demo        Variante asignada: A')
        print('15 Editar componentes de combo                  0 Salir')
        try:
            opcion = input('Opción: ').strip()
            acciones = {
                '1': lambda: registrar_producto(restaurante), '2': lambda: menu_disponible(restaurante),
                '3': lambda: registrar_cliente(restaurante),
                '4': lambda: print('\n'.join(f'{c.id_cliente}: {c.nombre} | {c.telefono} | {c.direccion}' for c in restaurante.clientes.values())),
                '5': lambda: crear_pedido(restaurante), '6': lambda: editar_pedido(restaurante),
                '7': lambda: print(elegir_pedido(restaurante).generar_comprobante()),
                '8': lambda: cambiar_estado(restaurante), '9': lambda: cobrar(restaurante),
                '10': lambda: reporte(restaurante), '11': lambda: guardar(restaurante),
                '13': lambda: cargar_demostracion(restaurante),
                '15': lambda: editar_combo(restaurante),
            }
            if opcion == '0':
                print('Fin. Use Guardar JSON antes de salir si desea conservar los datos.')
                return
            if opcion == '12':
                ruta = input('Ruta del archivo JSON: ').strip()
                nuevo = Restaurante.cargar_json(ruta)
                restaurante = nuevo
                print('Archivo cargado. Perfil activo:', restaurante.reglas.codigo)
            elif opcion in acciones: acciones[opcion]()
            else: print('Opción inválida.')
        except (ValueError, KeyError, OSError) as error:
            print('No se pudo realizar la operación:', error)
        except (EOFError, KeyboardInterrupt):
            print('\nSesión terminada. Solo se conservan los datos guardados en JSON.')
            return

if __name__ == '__main__':
    try:
        principal()
    except (ValueError, OSError, EOFError, KeyboardInterrupt) as error:
        print('No se pudo iniciar:', error)
