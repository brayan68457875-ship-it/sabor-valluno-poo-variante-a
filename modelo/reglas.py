"""Reglas de la variante A asignada a Brayan; se conserva el contrato del diagrama."""
from decimal import Decimal
from types import MappingProxyType
from .utilidades import dinero, entero, normalizar_dia

class ReglasVariante:
    def __init__(self, codigo, decisiones=None):
        codigo = str(codigo).strip().upper()
        if codigo != 'A':
            raise ValueError('Esta entrega corresponde exclusivamente a la variante A.')
        self._codigo = codigo
        self._porcentaje_combo = Decimal('0.10')
        self._minimo_componentes_descuento = 2
        self._maximo_componentes = None
        self._costo_envase = dinero('2')
        self._base_envase = 'platos'
        self._umbral_envio_gratis = dinero('150')
        self._zonas_gratis = frozenset({'Cercado'})
        self._minimo_delivery = dinero('40')
        self._dias_venta = {'chicharron': frozenset({'domingo'})}
        # Los JSON antiguos pueden contener opciones B/C: no se aplican en A.
        propuestas = {'top_productos': (decisiones or {}).get('top_productos', 'lineas')}
        if propuestas['top_productos'] not in ('lineas', 'hojas'):
            raise ValueError('Top de productos: lineas u hojas.')
        self._decisiones = propuestas

    @staticmethod
    def desde_codigo(codigo, decisiones=None):
        return ReglasVariante(codigo, decisiones)

    @property
    def codigo(self):
        return self._codigo

    @property
    def decisiones(self):
        return MappingProxyType(self._decisiones)

    @property
    def minimo_delivery(self):
        return self._minimo_delivery

    @property
    def dias_venta(self):
        return MappingProxyType(self._dias_venta)

    @property
    def base_envase(self):
        return self._base_envase

    def descontar_combo(self, suma, cantidad):
        self.validar_componentes(cantidad)
        return dinero(dinero(suma) * (1 - self._porcentaje_combo))

    def validar_componentes(self, cantidad):
        entero(cantidad, self._minimo_componentes_descuento, self._maximo_componentes)

    def calcular_envases(self, platos, productos):
        return dinero(self._costo_envase * entero(platos, 0))

    def calcular_envio(self, zona, subtotal, tarifa):
        if zona in self._zonas_gratis and dinero(subtotal) >= self._umbral_envio_gratis:
            return dinero(0)
        return dinero(tarifa)

    def descontar_local(self, subtotal, platos):
        return dinero(0)

    def calcular_promocion(self, importe, cantidad, dia, es_natural, es_vaso):
        normalizar_dia(dia)
        return dinero(dinero(importe) * entero(cantidad, 1, 20))

    def ajustar_efectivo(self, total):
        return dinero(total)

    def a_dict(self):
        return {'codigo': self.codigo, 'decisiones': dict(self.decisiones)}
