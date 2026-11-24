from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from .utilidades import dinero, entero

class MetodoPago(ABC):
    def __init__(self, id_pago: int, reglas):
        self._id_pago = entero(id_pago)
        self._reglas = reglas
        self._fecha = None
        self._monto_cobrado = dinero(0)
        self._nombre = 'Método de pago'

    @property
    def id_pago(self): return self._id_pago
    @property
    def fecha(self): return self._fecha
    @property
    def monto_cobrado(self): return self._monto_cobrado
    @property
    def reglas(self): return self._reglas

    @abstractmethod
    def procesar_pago(self, total: Decimal) -> Decimal: pass

    def permite_delivery(self) -> bool: return True

    def _validar_cobro(self, total):
        if self.fecha is not None:
            raise ValueError('Este pago ya fue procesado; cree otro identificador.')
        if dinero(total) <= 0:
            raise ValueError('El total por cobrar debe ser positivo.')

    def _registrar_cobro(self, monto):
        self._monto_cobrado = dinero(monto)
        self._fecha = datetime.now()
        return self.monto_cobrado

    def generar_comprobante(self) -> str:
        return f'{self._nombre} | pago #{self.id_pago} | cobrado Bs {self.monto_cobrado:.2f}'

    def a_dict(self):
        return {'id_pago': self.id_pago, 'fecha': None if self.fecha is None else self.fecha.isoformat(),
                'monto_cobrado': str(self.monto_cobrado)}

    def restaurar_cobro(self, datos):
        # Solo se usa al cargar el JSON, sin volver a cobrar.
        monto = dinero(datos['monto_cobrado'])
        if monto < 0 or datos['fecha'] is None:
            raise ValueError('Registro de pago incompleto.')
        self._monto_cobrado = monto
        self._fecha = datetime.fromisoformat(datos['fecha'])

class Efectivo(MetodoPago):
    def __init__(self, id_pago: int, monto_recibido, reglas):
        super().__init__(id_pago, reglas)
        self._nombre = 'Efectivo'
        self._monto_recibido = dinero(monto_recibido)
        if self._monto_recibido < 0:
            raise ValueError('El monto recibido no puede ser negativo.')
        self._cambio = dinero(0)

    @property
    def monto_recibido(self): return self._monto_recibido
    @property
    def cambio(self): return self._cambio

    def procesar_pago(self, total: Decimal) -> Decimal:
        self._validar_cobro(total)
        cobro = self.reglas.ajustar_efectivo(total)
        if self.monto_recibido < cobro:
            raise ValueError('El efectivo recibido no cubre el importe a cobrar.')
        self._cambio = dinero(self.monto_recibido - cobro)
        return self._registrar_cobro(cobro)

    def calcular_cambio(self) -> Decimal: return self.cambio

    def generar_comprobante(self) -> str:
        return super().generar_comprobante() + f' | recibido {self.monto_recibido:.2f} | cambio {self.cambio:.2f}'

    def a_dict(self):
        return dict(super().a_dict(), clase='Efectivo', monto_recibido=str(self.monto_recibido), cambio=str(self.cambio))

    def restaurar_cobro(self, datos):
        super().restaurar_cobro(datos)
        self._cambio = dinero(datos['cambio'])
        if self.cambio != dinero(self.monto_recibido - self.monto_cobrado):
            raise ValueError('Cambio inconsistente en el pago almacenado.')

class QR(MetodoPago):
    def __init__(self, id_pago: int, codigo_transaccion: str, reglas):
        super().__init__(id_pago, reglas)
        self._nombre = 'QR'
        if not self.validar_codigo(codigo_transaccion):
            raise ValueError('El código QR debe tener exactamente 10 dígitos.')
        self._codigo_transaccion = str(codigo_transaccion)

    @property
    def codigo_transaccion(self): return self._codigo_transaccion

    @staticmethod
    def validar_codigo(codigo: str) -> bool:
        codigo = str(codigo)
        return len(codigo) == 10 and codigo.isascii() and codigo.isdecimal()

    def procesar_pago(self, total: Decimal) -> Decimal:
        self._validar_cobro(total)
        return self._registrar_cobro(total)

    def generar_comprobante(self) -> str:
        return super().generar_comprobante() + f' | transacción {self.codigo_transaccion}'

    def a_dict(self):
        return dict(super().a_dict(), clase='QR', codigo_transaccion=self.codigo_transaccion)

class Tarjeta(MetodoPago):
    def __init__(self, id_pago: int, reglas):
        super().__init__(id_pago, reglas)
        self._nombre = 'Tarjeta'
        self._comision = Decimal('0.03')

    @property
    def comision(self): return self._comision

    def calcular_comision(self, total: Decimal) -> Decimal:
        return dinero(total * self.comision)

    def procesar_pago(self, total: Decimal) -> Decimal:
        self._validar_cobro(total)
        return self._registrar_cobro(dinero(total) + self.calcular_comision(dinero(total)))

    def permite_delivery(self) -> bool: return False

    def a_dict(self):
        return dict(super().a_dict(), clase='Tarjeta', comision=str(self.comision))
