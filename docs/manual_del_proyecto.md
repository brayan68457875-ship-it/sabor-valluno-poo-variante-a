# Manual del proyecto Sabor Valluno

Brayan Saravia Garay · Ingeniería de Sistemas · Paralelo B  
Ing. Roy Carrasco · Entrega 24 de noviembre de 2026

## Problema y resultado esperado

Sabor Valluno registra pedidos de comida típica y necesita calcular correctamente combos, envases, envíos y cobros. Una suma manual puede olvidar que un combo contiene otros productos o que un envío cambia según la zona. El programa reúne esas reglas en objetos y permite atender un pedido completo desde su registro hasta su entrega.

El resultado es una aplicación de consola, sin paquetes externos, con las clases del diagrama suministrado. Aplica la variante A, confirmada por Brayan el 23/11/2026; la versión anterior con seis perfiles se reemplaza para esta entrega. Las decisiones no confirmadas se conservan identificadas en el acta.

## Objetivos

El objetivo general es administrar el ciclo de pedidos con un modelo coherente de programación orientada a objetos. Los objetivos específicos son registrar el menú y los clientes, calcular importes recursivos, validar estados y pagos, separar los cargos por modalidad, generar reportes diarios y conservar la información en JSON.

## Cómo se distribuyen las responsabilidades

| Clase | Responsabilidad y datos principales |
|---|---|
| Restaurante | Registra productos, clientes y pedidos; evita mesas ocupadas; genera reportes; guarda y carga JSON. |
| Cliente | Identificador, nombre, teléfono validado y dirección. |
| Producto | Contrato abstracto común de precio, disponibilidad y conteo de platos. |
| Plato | Precio base y días de venta; cuenta como un plato. |
| Bebida | Precio por vaso, presentación y condición de refresco natural; jarra al triple del vaso, sin 2×1 en A; cuenta cero platos. |
| Combo | Agrega productos compartidos, incluidos otros combos; aplica descuento y recorre componentes recursivamente. |
| Pedido | Cliente, fecha, estado, detalles y pago; controla edición, subtotal, total y transiciones. |
| Local | Mesa de 1 a 15; sin cargos adicionales ni descuento local. |
| Llevar | Envases: Bs 2 por cada plato, incluidos los de combos anidados. |
| Delivery | Zona, dirección, tarifas y fecha de entrega; verifica mínimo, medios de pago y retraso. |
| DetalleProducto | Producto, cantidad y cotización histórica; calcula el subtotal y las promociones de la línea. |
| MetodoPago | Contrato abstracto del procesamiento del cobro. |
| Efectivo | Monto recibido suficiente y cambio; sin redondeo adicional en A. |
| QR | Código de transacción de diez dígitos. |
| Tarjeta | Comisión de 3 % y rechazo para delivery mediante comportamiento polimórfico. |
| EstadoPedido | Enumeración de los cinco estados permitidos. |
| ReglasVariante | Valores de A y criterio configurable del reporte; evita esparcir tasas fijas en las clases de pedidos. |

Los nombres `Local`, `Llevar`, `Delivery`, `Combo`, `Efectivo`, `QR` y `Tarjeta` se conservan del boceto. `Pago` se precisó como `MetodoPago` para ajustarse a la guía; `Detalle Producto` se escribe `DetalleProducto` por la convención de nombres de clases de Python.

## Relaciones del diagrama

Un cliente puede realizar varios pedidos; cada pedido tiene un cliente. El restaurante registra muchos productos, clientes y pedidos. Un pedido compone sus detalles: un detalle pertenece a ese pedido y no se reutiliza en otro. Cada detalle referencia un producto del menú.

Un combo agrega productos compartidos: el mismo plato puede aparecer en varios combos y también venderse por separado. Por eso la relación usa agregación, no composición que sugiera que al eliminar el combo desaparece el plato. La relación con `Producto` permite incluir otro `Combo` sin añadir una clase especial para combos anidados.

Cada pedido puede estar sin pagar o tener un solo pago. Las tres familias usan herencia con un triángulo dirigido hacia su clase abstracta. `EstadoPedido` expresa el estado mediante valores limitados, mientras `ReglasVariante` se comparte por referencia dentro del contexto.

## Evidencia de los cuatro pilares

**Abstracción.** `Producto`, `Pedido` y `MetodoPago` heredan de `ABC`. Los métodos decorados con `@abstractmethod` expresan qué deben implementar sus descendientes. Intentar instanciarlas directamente produce `TypeError`, comprobado en las pruebas.

**Herencia.** Hay tres descendientes de cada clase abstracta: nueve subclases de dominio. Sus constructores llaman a `super().__init__()` y los campos comunes se definen en las bases. Por ejemplo, las modalidades de pedido no vuelven a declarar cliente, estado ni lista de detalles.

**Encapsulación.** Los campos de los objetos usan prefijo protegido `_`. Se accede mediante propiedades. Los precios y el teléfono tienen validaciones; las colecciones se exponen como tuplas, conjuntos inmutables o vistas de solo lectura. Devolver una tupla de detalles no bastaría si sus cantidades pudieran cambiar sin control: cada `DetalleProducto` conserva una función de validación del pedido y la ejecuta antes de cambiar cantidad.

**Polimorfismo.** `Pedido` suma los subtotales de sus detalles; no pregunta si un producto es plato, bebida o combo. `Combo` llama a `calcular_precio()`, `esta_disponible()` y `contar_platos()` de cada componente. `Delivery` pregunta `permite_delivery()` al método de pago en vez de comprobar si el objeto es una tarjeta. Las tasas de A se resuelven con datos, no con condicionales de clases dentro de las jerarquías.

Los diccionarios de fábricas de `main.py` y de carga JSON traducen elecciones textuales a constructores. Esa decisión en la frontera de entrada no reemplaza el polimorfismo del cálculo: una vez creado el objeto, los métodos del modelo trabajan con su contrato común.

## Precios, promociones y total

Todos los importes se almacenan como `Decimal` y se redondean a dos decimales con `ROUND_HALF_UP`. Se construyen desde texto para evitar errores de números binarios en operaciones monetarias. El precio unitario debe ser positivo.

Un vaso utiliza su precio base y la jarra cuesta tres veces ese valor. En A, un combo suma los precios de sus componentes y descuenta 10 % en cada nivel, incluidos combos anidados. Requiere al menos dos componentes y no tiene el máximo de cuatro de C. No hay descuentos fijos ni promociones 2×1.

El detalle conserva la cotización que existía al agregar el producto. Guarda importes para las cantidades 1–20 y los conteos necesarios: así un cambio posterior en el menú no altera un pedido anterior. Esto también conserva el efecto de una promoción por cantidad, que no siempre se puede representar multiplicando un precio fijo.

En A no hay 2×1 del martes. Las cantidades iguales del mismo producto se consolidan en una línea y se respeta el límite de 1 a 20.

La fórmula usada es:

```text
subtotal del pedido = suma de subtotales de detalles, ya con promociones
total del pedido = subtotal − descuento local + envases o envío
importe cobrado = total + comisión de tarjeta si corresponde (efectivo y QR: sin ajuste)
```

El descuento de combo ya está incorporado en el precio del producto y no se vuelve a descontar al cerrar el pedido. La comisión de tarjeta se aplica una sola vez al cobrar. El comprobante separa subtotal, descuento de pedido, cargos, total y ajuste de cobro.

## Caso de referencia recalculado

Silpancho Bs 35 y mocochinchi vaso Bs 6 suman Bs 41. Se venden dos combos por delivery a Quillacollo, donde el envío vale Bs 15. El caso se evalúa fuera de una promoción de martes.

| Perfil | Cálculo de un combo | Precio combo | Total de dos con envío |
|---|---|---|---|
| A | 41 × 0,90 | 36,90 | 88,80 |

En A, efectivo y QR mantienen el total de Bs 88,80. La tarjeta añade 3 % para modalidades admitidas, pero delivery solo permite Efectivo o QR.

Para un combo anidado de A, el combo de Bs 36,90 más otro silpancho de Bs 35 suman 71,90; con 10 % quedan 64,71. Contiene dos platos y una bebida. Dos unidades para llevar cuestan 129,42 más cuatro envases de Bs 2: total Bs 137,42.

## Disponibilidad y envases

Cada plato tiene días de venta. En A, el chicharrón solo se vende los domingos. Los otros platos se registran con sus días de venta; sin restricción adicional se ofrecen todos los días. Un combo solo está disponible si lo están todos sus componentes.

El pedido utiliza el día de su fecha de registro. Una consulta del menú para otro día es informativa y no modifica esa fecha.

En A se cobra Bs 2 por cada plato, incluidos los platos de combos anidados. Las bebidas no generan envase. El conteo recorre recursivamente los componentes mediante contar_platos().

## Estados y mesas

El flujo normal es REGISTRADO → EN_PREPARACION → LISTO → ENTREGADO. CANCELADO solo se alcanza desde REGISTRADO. Un salto, una vuelta atrás o una edición después de comenzar la preparación produce `ValueError`.

El registro puede comenzar sin productos, pero no se confirma ni se cobra vacío. El mínimo de delivery se verifica al confirmar o cobrar, para permitir construir el pedido agregando productos en varias operaciones. Una cotización por debajo del mínimo puede mostrarse, pero todavía no puede confirmarse.

La mesa debe estar entre 1 y 15. `Restaurante` revisa los pedidos abiertos antes de registrar otro en esa mesa. Entregar o cancelar libera la mesa. Cobrar no la libera automáticamente porque un pedido pagado todavía puede estar en preparación.

Por consistencia de esta implementación, un pedido cobrado ya no admite edición ni cancelación simple, aunque permanezca REGISTRADO. La guía no define un circuito de reembolsos por cancelación después de cobrar; esa decisión adicional está incluida en las consultas pendientes.

## Pagos y compensación

Efectivo valida que el monto recibido cubra el total y conserva el cambio. QR requiere diez dígitos ASCII; se conserva como texto para no perder ceros iniciales. El gestor rechaza identificadores de pago repetidos y códigos QR ya utilizados. Tarjeta cobra 3 % adicional y responde `False` a `permite_delivery()`.

Se trata de una simulación académica. No se conectan bancos, pasarelas ni lectores QR; el código de transacción se registra manualmente. No se guardan números completos de tarjeta ni datos bancarios.

La fuente proporcionada incluye como respuesta que existe retraso cuando pasan más de 60 minutos desde el registro y corresponde devolver el costo del envío. A los 60 minutos exactos no hay compensación. Un envío que ya era gratuito produce compensación de Bs 0, porque ese fue el importe cobrado por envío.

`calcular_retraso()` devuelve minutos que exceden el límite. `calcular_compensacion()` devuelve el importe que correspondería reembolsar. El sistema lo informa, pero no acredita que el dinero haya sido devuelto. El acta mantiene pendiente la consulta real al docente.

## Reportes

El reporte diario incluye los pedidos cobrados en la fecha del pago, agrupados por local, llevar y delivery. Presenta número de pedidos, suma de totales comerciales, dinero efectivamente cobrado y compensación calculada. Esta separación evita confundir la comisión de tarjeta con el total del pedido.

El top 3 ordena por cantidad descendente y, ante empate, por identificador ascendente. Con el criterio propuesto `lineas`, un combo vendido cuenta como combo; con `hojas`, se desglosan sus productos finales. No se cuentan pedidos cancelados ni pendientes de cobro. La interpretación comercial debe confirmarse antes de afirmar que es la exigida por el docente.

## Persistencia JSON

Guardar exporta el perfil activo, las decisiones, productos, componentes de combos, clientes, pedidos, cotizaciones, estados, pagos y fechas. Los `Decimal` se escriben como texto y las fechas en formato ISO. La escritura usa un archivo temporal y reemplazo final para reducir el riesgo de dejar un archivo incompleto.

Cargar construye un restaurante nuevo y solo lo sustituye en el menú cuando todo termina correctamente. Primero reconstruye los productos resolviendo las dependencias de combos. Si no puede avanzar, informa de referencias faltantes o ciclos. Luego carga clientes y pedidos y verifica los cobros almacenados. No ejecuta una transacción bancaria.

El JSON conserva las cotizaciones históricas y sus propias decisiones. Editar `configuracion.json` no cambia automáticamente un archivo guardado. Se incluye `datos/ejemplo_A.json` con datos ficticios de la variante A.

## Validación y entrega personal

`pruebas.py` contiene casos con `assert` para la referencia A y sus límites, recursión, ciclos, disponibilidad, promociones, envases, mínimos, límites, estados, cobro, reportes y JSON. El resultado real de la ejecución se encuentra en `resultados_pruebas.txt`.

El código y los documentos no sustituyen la revisión del estudiante. Brayan debe completar los datos pendientes, confirmar las consultas, declarar el uso de IA, conservar el proceso real y practicar la defensa. El proyecto no incluye commits retroactivos, firmas ni respuestas docentes inventadas.
