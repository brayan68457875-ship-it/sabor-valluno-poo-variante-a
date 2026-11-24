"""Precios y datos ficticios de demostración, salvo 35 y 6 del caso de la guía."""
from modelo.productos import Plato, Bebida, Combo
from modelo.clientes import Cliente

def cargar_demostracion(restaurante):
    if restaurante.productos or restaurante.clientes or restaurante.pedidos:
        raise ValueError('La demostración se carga únicamente en un restaurante vacío.')
    reglas = restaurante.reglas
    productos = [Plato(1, 'Silpancho', '35', reglas), Plato(2, 'Pique macho', '45', reglas),
                 Plato(3, 'Chicharrón', '40', reglas), Plato(4, 'Sopa de maní', '15', reglas),
                 Bebida(5, 'Mocochinchi vaso', '6', reglas, 'vaso', True),
                 Bebida(6, 'Mocochinchi jarra', '6', reglas, 'jarra', True),
                 Bebida(7, 'Gaseosa vaso', '5', reglas)]
    for producto in productos:
        restaurante.registrar_producto(producto)
    combo = Combo(8, 'Combo silpancho y mocochinchi', [productos[0], productos[4]], reglas)
    restaurante.registrar_producto(combo)
    restaurante.registrar_producto(Combo(9, 'Combo anidado familiar', [combo, productos[1]], reglas))
    restaurante.registrar_cliente(Cliente(1, 'Cliente de demostración', '70000001', 'Dirección ficticia, Cochabamba'))
