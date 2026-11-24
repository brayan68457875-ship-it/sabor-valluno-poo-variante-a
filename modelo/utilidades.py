"""Validaciones y redondeo comunes; solo biblioteca estándar."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import date

DIAS = ('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo')

def dinero(valor):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ValueError('El importe debe ser numérico.') from None
    if not numero.is_finite():
        raise ValueError('El importe debe ser finito.')
    try:
        return numero.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except InvalidOperation:
        raise ValueError('El importe excede la precisión monetaria admitida.') from None

def entero(valor, minimo=1, maximo=None):
    texto = str(valor)
    if not texto.isdecimal():
        raise ValueError('Se requiere un número entero.')
    numero = int(texto)
    if numero < minimo or (maximo is not None and numero > maximo):
        raise ValueError(f'Valor fuera del intervalo: {minimo} a {maximo or "sin límite"}.')
    return numero

def texto_obligatorio(valor):
    texto = str(valor).strip()
    if not texto:
        raise ValueError('El texto no puede estar vacío.')
    return texto

def normalizar_dia(dia):
    nombre = str(dia).strip().lower().translate(str.maketrans('áéíóú', 'aeiou'))
    if nombre not in DIAS:
        raise ValueError('Día inválido. Use lunes, martes, miércoles, jueves, viernes, sábado o domingo.')
    return nombre

def dia_fecha(fecha):
    return DIAS[fecha.weekday()]
