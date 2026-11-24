from abc import ABC, abstractmethod
from decimal import Decimal
from .utilidades import DIAS, dinero, entero, normalizar_dia, texto_obligatorio

class Producto(ABC):
    def __init__(self, id_producto: int, nombre: str, reglas):
        self._id_producto = entero(id_producto)
        self._nombre = texto_obligatorio(nombre)
        self._reglas = reglas

    @property
    def id_producto(self): return self._id_producto
    @property
    def nombre(self): return self._nombre
    @property
    def reglas(self): return self._reglas

    @abstractmethod
    def calcular_precio(self) -> Decimal: pass
    @abstractmethod
    def esta_disponible(self, dia: str) -> bool: pass
    @abstractmethod
    def contar_platos(self) -> int: pass

    def contar_productos(self) -> int: return 1

    def calcular_importe(self, cantidad: int, dia: str) -> Decimal:
        entero(cantidad, 1, 20)
        normalizar_dia(dia)
        return dinero(self.calcular_precio() * cantidad)

    @staticmethod
    def validar_precio(precio: Decimal):
        if dinero(precio) <= 0:
            raise ValueError('El precio debe ser mayor que cero.')

    def contiene(self, producto): return self is producto

    def desglosar_ventas(self, cantidad):
        return {self.id_producto: {'nombre': self.nombre, 'cantidad': cantidad}}

    def a_dict(self):
        return {'id_producto': self.id_producto, 'nombre': self.nombre}

class Plato(Producto):
    def __init__(self, id_producto: int, nombre: str, precio_base, reglas, dias_venta=None):
        super().__init__(id_producto, nombre, reglas)
        self.precio_base = precio_base
        clave = nombre.strip().lower().translate(str.maketrans('áéíóú', 'aeiou'))
        obligatorios = reglas.dias_venta.get(clave)
        self._restriccion_variante = obligatorios
        self.actualizar_dias(obligatorios if obligatorios is not None else (DIAS if dias_venta is None else dias_venta))

    @property
    def precio_base(self): return self._precio_base
    @precio_base.setter
    def precio_base(self, valor):
        self.validar_precio(valor)
        self._precio_base = dinero(valor)
    @property
    def dias_venta(self): return frozenset(self._dias_venta)

    def actualizar_dias(self, dias):
        dias = {normalizar_dia(dia) for dia in dias}
        if not dias:
            raise ValueError('Debe existir al menos un día de venta.')
        if self._restriccion_variante is not None and not dias.issubset(self._restriccion_variante):
            raise ValueError('Los días contradicen la disponibilidad de la variante.')
        self._dias_venta = dias

    def calcular_precio(self) -> Decimal: return self.precio_base
    def esta_disponible(self, dia: str) -> bool: return normalizar_dia(dia) in self._dias_venta
    def contar_platos(self) -> int: return 1

    def a_dict(self):
        return dict(super().a_dict(), clase='Plato', precio_base=str(self.precio_base), dias_venta=sorted(self.dias_venta))

class Bebida(Producto):
    def __init__(self, id_producto: int, nombre: str, precio_vaso, reglas, presentacion='vaso', es_natural=False):
        super().__init__(id_producto, nombre, reglas)
        self.precio_vaso = precio_vaso
        if presentacion not in ('vaso', 'jarra'):
            raise ValueError('Presentación: vaso o jarra.')
        self._presentacion, self._es_natural = presentacion, bool(es_natural)

    @property
    def precio_vaso(self): return self._precio_vaso
    @precio_vaso.setter
    def precio_vaso(self, valor):
        self.validar_precio(valor)
        self._precio_vaso = dinero(valor)
    @property
    def presentacion(self): return self._presentacion
    @property
    def es_natural(self): return self._es_natural

    def calcular_precio(self) -> Decimal:
        return dinero(self.precio_vaso * {'vaso': 1, 'jarra': 3}[self.presentacion])
    def esta_disponible(self, dia: str) -> bool:
        normalizar_dia(dia)
        return True
    def contar_platos(self) -> int: return 0

    def calcular_importe(self, cantidad: int, dia: str) -> Decimal:
        entero(cantidad, 1, 20)
        return self.reglas.calcular_promocion(self.calcular_precio(), cantidad, dia, self.es_natural, self.presentacion == 'vaso')

    def a_dict(self):
        return dict(super().a_dict(), clase='Bebida', precio_vaso=str(self.precio_vaso),
                    presentacion=self.presentacion, es_natural=self.es_natural)

class Combo(Producto):
    def __init__(self, id_producto: int, nombre: str, componentes, reglas):
        super().__init__(id_producto, nombre, reglas)
        self._componentes = list(componentes)
        reglas.validar_componentes(len(self._componentes))
        for componente in self._componentes:
            self.validar_sin_ciclos(componente)
        self.validar_precio(self.calcular_precio())

    @property
    def componentes(self): return tuple(self._componentes)

    def calcular_precio(self) -> Decimal:
        suma = sum((p.calcular_precio() for p in self._componentes), dinero(0))
        precio = self.reglas.descontar_combo(suma, len(self._componentes))
        self.validar_precio(precio)
        return precio

    def esta_disponible(self, dia: str) -> bool:
        normalizar_dia(dia)
        return all(p.esta_disponible(dia) for p in self._componentes)

    def contar_platos(self) -> int:
        return sum(p.contar_platos() for p in self._componentes)

    def contar_productos(self) -> int:
        return sum(p.contar_productos() for p in self._componentes)

    def calcular_importe(self, cantidad: int, dia: str) -> Decimal:
        return super().calcular_importe(cantidad, dia)

    def contiene(self, p: Producto) -> bool:
        return self is p or any(componente.contiene(p) for componente in self._componentes)

    def validar_sin_ciclos(self, p: Producto):
        if p.contiene(self):
            raise ValueError('Un combo no puede formar un ciclo directo ni indirecto.')
        if p.reglas is not self.reglas:
            raise ValueError('Los componentes deben compartir la misma configuración de reglas.')

    def agregar_componente(self, p: Producto):
        self.validar_sin_ciclos(p)
        self.reglas.validar_componentes(len(self._componentes) + 1)
        self._componentes.append(p)
        try:
            self.calcular_precio()
        except ValueError:
            self._componentes.pop()
            raise

    def quitar_componente(self, p: Producto):
        self.reglas.validar_componentes(len(self._componentes) - 1)
        indice = self._componentes.index(p)
        anterior = self._componentes.pop(indice)
        try:
            self.calcular_precio()
        except ValueError:
            self._componentes.insert(indice, anterior)
            raise

    def desglosar_ventas(self, cantidad):
        resultado = {}
        for componente in self._componentes:
            for codigo, dato in componente.desglosar_ventas(cantidad).items():
                resultado.setdefault(codigo, {'nombre': dato['nombre'], 'cantidad': 0})
                resultado[codigo]['cantidad'] += dato['cantidad']
        return resultado

    def a_dict(self):
        return dict(super().a_dict(), clase='Combo', componentes=[p.id_producto for p in self._componentes])
