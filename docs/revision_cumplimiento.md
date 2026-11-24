# Revisión de cumplimiento del proyecto

Fecha: 24/11/2026 · Brayan Saravia Garay  
Universidad Adventista de Bolivia · Ingeniería de Sistemas · POO B  
Docente: Ing. Roy Carrasco · Entrega: 24/11/2026 · Variante A

## Resultado técnico

Se volvió a leer el DOCX original y se contrastó con la carpeta actual del proyecto. El sistema utiliza consola, biblioteca estándar y las tres jerarquías del diagrama. Las 32 pruebas del alcance actual aprobaron. Además se ejecutó el menú real de principio a fin con registro de productos, combo y cliente, las tres modalidades de pedido, los tres medios de pago, cambios de estado, cancelación, reporte y JSON.

| Área | Verificación |
|---|---|
| Productos y disponibilidad | Platos, bebidas, jarras, combos anidados, ciclos rechazados y chicharrón solo domingo |
| Variante A | Combo con 10 %; envase Bs 2 por plato; mínimo delivery Bs 40; Cercado gratis desde subtotal Bs 150 |
| Pedidos | Local, Llevar y Delivery; mesa 1–15 y sin duplicar pedidos abiertos; edición limitada a REGISTRADO sin cobrar |
| Estados | Flujo ordenado, cancelación desde REGISTRADO y excepciones ante transiciones inválidas |
| Pagos | Efectivo y cambio; QR de 10 dígitos; tarjeta con 3 %, excluida de delivery |
| POO | Tres abstractas, nueve subclases con super, propiedades y polimorfismo sin comprobar clases en los cálculos |
| Reporte | Ventas cobradas por modalidad y top 3 por cantidades de productos vendidos como línea |
| Pruebas | 32/32 aprobadas; referencia Bs 88,80 y combo anidado incluidos |
| JSON opcional | Guardado y carga comprobados, conservando cotizaciones y pagos |
| Documentos | Diagramas v1/v2, tabla de clases, README, manual, inventario, bitácora y registro de alcance |

Se aclaró en el comprobante que el precio de los combos ya incluye el 10 % de descuento. El descuento adicional del pedido no vuelve a restarlo. Un pedido cancelado indica que no corresponde cobrar.

## Alcance indicado por el estudiante

Se retiró la gestión de retrasos y compensaciones. Se eliminaron su umbral, métodos, campos del reporte y aviso de consultas del inicio. El top 3 sigue contando unidades por producto vendido como línea; un combo cuenta como producto vendido. No se atribuye una confirmación al docente.

La guía original sí incluía retrasos y una consulta al docente; por eso esta revisión distingue ese requisito del alcance actual solicitado. No se presenta como una implementación literal del 100 % de la guía original.

## Estado de evidencias personales y publicación

El repositorio tiene ocho commits iniciales de incorporación, hechos en una misma sesión. Las correcciones actuales constituyen trabajo posterior y se conservan como cambios reales. Ese historial no acredita cuatro commits en la semana 2 y cuatro en la semana 3, que es la distribución indicada por la guía.

El repositorio se publicó el 24/11/2026 en [brayan68457875-ship-it/sabor-valluno-poo-variante-a](https://github.com/brayan68457875-ship-it/sabor-valluno-poo-variante-a), con visibilidad pública. El remoto origin está configurado y las comprobaciones automáticas se encuentran en Actions. La institución ya está registrada.

El archivo v1 es la fotografía aportada: no acredita firma docente. La firma y la defensa individual requieren actuaciones personales. El registro de IA tiene un alcance acotado tras las ediciones solicitadas anteriormente; el estudiante debe comprobar que su declaración personal sea fiel a los usos que efectivamente realizó. Esta revisión no firma ni certifica comprensión por él.

## Corrección en VS Code del 24/11/2026

Se alineó el código con los campos activos del último diagrama. Se retiraron opciones C/B y campos inactivos de descuentos y redondeo de otras variantes. La configuración contiene solo el criterio de reporte; los archivos antiguos siguen cargando. Las 32 pruebas y la venta de referencia desde consola fueron comprobadas. No se cambió el alcance sin gestión de retrasos ni compensaciones.
