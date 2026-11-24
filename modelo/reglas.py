"""Reglas de la variante A asignada a Brayan; se conserva el contrato del diagrama."""
from decimal import Decimal, ROUND_FLOOR
from types import MappingProxyType
from .utilidades import dinero, entero, normalizar_dia

class ReglasVariante:
    PERFILES = {'A': ('0.10', '0', 2, None, '2', 'platos', '150', ('Cercado',), '40')}

    def __init__(self, codigo, decisiones=None):
        codigo = str(codigo).strip().upper()
        if codigo not in self.PERFILES:
            raise ValueError('Esta entrega corresponde exclusivamente a la variante A.')
        self._codigo = codigo
        porcentaje, fijo, minimo, maximo, envase, base, umbral, zonas, pedido_minimo = self.PERFILES[codigo]
        self._porcentaje_combo = Decimal(porcentaje)
        self._descuento_fijo = dinero(fijo)
        self._minimo_componentes_descuento = minimo
        self._maximo_componentes = maximo
        self._costo_envase = dinero(envase)
        self._base_envase = base
        self._umbral_envio_gratis = None if umbral is None else dinero(umbral)
        self._zonas_gratis = frozenset(zonas)
        self._minimo_delivery = dinero(pedido_minimo)
        self._dias_venta = {}
        self._dias_venta['chicharron'] = frozenset({'domingo'})
        self._promo_natural_martes = False
        self._minimo_platos_local = 0
        self._descuento_local = Decimal('0')
        self._paso_redondeo_efectivo = None
        propuestas = {'conteo_productos_c': 'hojas', 'promo_dentro_combos': False, 'top_productos': 'lineas', 'consultas_confirmadas': False}
        propuestas.update(decisiones or {})
        if propuestas['conteo_productos_c'] not in ('hojas', 'componentes', 'unidad'):
            raise ValueError('Conteo C: hojas, componentes o unidad.')
        if propuestas['top_productos'] not in ('lineas', 'hojas'):
            raise ValueError('Top de productos: lineas u hojas.')
        if propuestas['promo_dentro_combos'] not in (True, False):
            raise ValueError('promo_dentro_combos debe ser true o false.')
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
        suma = dinero(suma)
        if cantidad >= self._minimo_componentes_descuento:
            return dinero(suma * (1 - self._porcentaje_combo) - self._descuento_fijo)
        return suma

    def validar_componentes(self, cantidad):
        entero(cantidad, 2, self._maximo_componentes)

    def calcular_envases(self, platos, productos):
        unidades = {'platos': platos, 'productos': productos}[self._base_envase]
        return dinero(self._costo_envase * unidades)

    def calcular_envio(self, zona, subtotal, tarifa):
        if self._umbral_envio_gratis is not None and zona in self._zonas_gratis and (subtotal >= self._umbral_envio_gratis):
            return dinero(0)
        return dinero(tarifa)

    def descontar_local(self, subtotal, platos):
        if self._minimo_platos_local and platos >= self._minimo_platos_local:
            return dinero(subtotal * self._descuento_local)
        return dinero(0)

    def calcular_promocion(self, importe, cantidad, dia, es_natural, es_vaso):
        if self._promo_natural_martes and normalizar_dia(dia) == 'martes' and es_natural and es_vaso:
            return dinero(importe * (cantidad - cantidad // 2))
        return dinero(importe * cantidad)

    def ajustar_efectivo(self, total):
        total = dinero(total)
        if self._paso_redondeo_efectivo is not None:
            pasos = (total / self._paso_redondeo_efectivo).to_integral_value(rounding=ROUND_FLOOR)
            return dinero(pasos * self._paso_redondeo_efectivo)
        return total

    def a_dict(self):
        return {'codigo': self.codigo, 'decisiones': dict(self.decisiones)}
