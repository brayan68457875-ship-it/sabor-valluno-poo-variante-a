from .utilidades import entero, texto_obligatorio

class Cliente:
    def __init__(self, id_cliente: int, nombre: str, telefono: str, direccion: str = ''):
        self._id_cliente = entero(id_cliente)
        self.actualizar_datos(nombre, telefono, direccion)

    @property
    def id_cliente(self): return self._id_cliente
    @property
    def nombre(self): return self._nombre
    @nombre.setter
    def nombre(self, valor): self._nombre = texto_obligatorio(valor)
    @property
    def telefono(self): return self._telefono
    @telefono.setter
    def telefono(self, valor):
        if not self.validar_telefono(valor):
            raise ValueError('El teléfono debe tener 8 dígitos e iniciar en 6 o 7.')
        self._telefono = str(valor)
    @property
    def direccion(self): return self._direccion
    @direccion.setter
    def direccion(self, valor): self._direccion = str(valor).strip()

    @staticmethod
    def validar_telefono(valor: str) -> bool:
        texto = str(valor)
        return len(texto) == 8 and texto.isascii() and texto.isdecimal() and texto[0] in '67'

    def actualizar_datos(self, nombre: str, telefono: str, direccion: str):
        # Validar todo antes de cambiar un cliente ya existente.
        nombre = texto_obligatorio(nombre)
        if not self.validar_telefono(telefono):
            raise ValueError('Teléfono inválido: 8 dígitos, inicia en 6 o 7.')
        self._nombre, self._telefono, self._direccion = nombre, str(telefono), str(direccion).strip()

    def a_dict(self):
        return {'id_cliente': self.id_cliente, 'nombre': self.nombre,
                'telefono': self.telefono, 'direccion': self.direccion}
