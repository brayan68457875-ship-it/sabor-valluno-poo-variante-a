# Preparación para la defensa individual

Brayan Saravia Garay · POO · Paralelo B · Ing. Roy Carrasco

## Explicar el diagrama en dos minutos

Describir primero el recorrido: Restaurante registra un Cliente; el cliente tiene un Pedido; el pedido compone DetalleProducto; cada detalle referencia un Producto. Después mostrar las tres jerarquías y explicar por qué Producto, Pedido y MetodoPago son abstractas. Cerrar con Combo agregando Producto para admitir anidamientos y con ReglasVariante separando los variante A.

Explicar los cambios respecto al papel: nombres precisados, gestor añadido, estados explícitos, tipos y visibilidad, composición de detalles, agregación de componentes, métodos sobrescritos y reglas configurables. Usar los archivos reales; no memorizar una explicación que no se pueda relacionar con el código.

## Preparar una explicación de código de tres minutos

Practicar con `Combo.calcular_precio()`: recorre componentes, cada uno responde su precio, suma los importes y aplica el perfil. Si un componente es otro combo, la misma llamada continúa recursivamente. No se pregunta por su clase.

Practicar `Pedido.agregar_producto()`: comprueba edición, cantidad, configuración y disponibilidad. Si la línea ya existe, consolida la cantidad; si no, crea un detalle con cotización. Explicar por qué la lista se devuelve como tupla y por qué el detalle también necesita validar su edición.

Practicar `Delivery.validar_pago()`: delega la compatibilidad al método de pago. Explicar cómo Tarjeta devuelve False sin introducir condiciones por clase en Pedido.

Explicar con palabras propias `ABC`, `@abstractmethod`, `@property`, `Decimal`, `Enum`, las fábricas de carga JSON y el guardado de cotizaciones. Si alguna construcción no se estudió en clase, revisarla antes de defenderla.

## Traza de combo anidado

En A, silpancho 35 + mocochinchi 6 suman 41; con 10 % quedan 36,90. Un combo exterior agrega ese combo y pique macho 45: (36,90 + 45) × 0,90 = 73,71. Ambos niveles descuentan 10 %. El exterior contiene dos platos y una bebida.

Contar platos a mano: el combo interior tiene uno; el exterior añade otro, por lo que tiene dos. Contar los componentes finales: dos platos y una bebida. Mostrar después que las pruebas producen el mismo resultado.

## Ejercicios de modificación sin IA

1. Añadir una zona: preparar un diccionario de tarifas con Tiquipaya a Bs 18 y pasarlo al constructor de Delivery. No cambiar Combo ni las clases de productos. En A el envío gratis sigue limitado a Cercado; la nueva zona no es gratuita.
2. Diseñar Postre heredando de Producto: almacenar precio base y condición de crema; calcular precio base más Bs 3 si lleva crema; disponibilidad definida para el ejemplo; contar cero platos. Registrar el objeto y comprobar que Pedido y Combo lo usan sin cambios. El nuevo constructor debe llamar a super.
3. Cambiar la comisión de tarjeta o el descuento de un perfil, localizar la prueba afectada y calcular primero el resultado esperado a mano.
4. Predecir qué ocurre si un combo contiene a otro que intenta contener al primero; explicar la búsqueda `contiene()`.

El ejercicio de Postre es una preparación de defensa, no una clase adicional entregada en el modelo actual. El documento exige que el estudiante haga el cambio en vivo y sin IA.

## Lista personal antes de presentar

Ejecutar el sistema desde cero, repetir una venta completa, guardar/cargar, ejecutar pruebas, comprobar que la variante activa sea A y revisar el alcance registrado. Poder justificar cada decisión del acta y explicar el alcance elegido. Completar el registro de IA con la comprensión real; no firmar afirmaciones que todavía no se puedan sostener.
