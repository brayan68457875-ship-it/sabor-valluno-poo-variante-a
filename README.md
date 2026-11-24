# Sabor Valluno · Sistema de pedidos · Variante A

Proyecto académico de **Programación Orientada a Objetos**, desarrollado en Python para administrar los pedidos de un restaurante de comida típica de Cochabamba.

| Dato | Información |
|---|---|
| Estudiante | Brayan Saravia Garay |
| Institución | Universidad Adventista de Bolivia |
| Carrera | Ingeniería de Sistemas |
| Asignatura y paralelo | Programación Orientada a Objetos · B |
| Docente | Ing. Roy Carrasco |
| Fecha de entrega | 24 de noviembre de 2026 |
| Variante asignada | **A** |
| Tipo de aplicación | **Consola / terminal** |
| Tecnología | Python 3.10 o posterior; biblioteca estándar |

## Ejecutar el sistema

Descarga la carpeta desde **Code → Download ZIP**, extrae los archivos y abre la carpeta que contiene `main.py` en VS Code. También puedes clonar el repositorio copiando su URL desde **Code**.

Abre una terminal dentro de esa carpeta:

```console
python main.py --demo
```

En Windows puedes sustituir `python` por `py -3`. No se requiere instalar paquetes con pip. `--demo` carga un cliente y un menú ficticios para practicar; omite ese parámetro si quieres comenzar con un restaurante vacío. La variante A se selecciona automáticamente.

```console
python main.py
python main.py --variante A --demo
python main.py --cargar datos/ejemplo_A.json
```

Los pagos son una simulación académica; no se realizan transacciones bancarias ni se emiten facturas fiscales. El programa conserva los datos entre sesiones únicamente si se usa la opción de guardar JSON.

## Probar el proyecto

```console
python pruebas.py
```

Hay **32 casos con assert**. Verifican el caso de referencia, combos anidados, detección de ciclos, disponibilidad, envases, mínimos de delivery, mesas, estados, pagos, reportes y persistencia JSON. Incluyen la lectura de archivos antiguos sin activar reglas ajenas a A. No ejecutar con `-O`, porque ese modo elimina los assert.

La pestaña **Actions** ejecuta las pruebas, la comprobación de sintaxis y el inicio de la consola con Python 3.11 y 3.12 después de cada actualización de `main` y en solicitudes de cambios. La configuración está en [pruebas.yml](.github/workflows/pruebas.yml). Los resultados locales de la revisión están en [resultados_pruebas.txt](docs/resultados_pruebas.txt); el resultado del servidor se consulta en Actions.

## Funciones del menú

| Opción | Función |
|---|---|
| 1 | Registrar platos, bebidas y combos |
| 2 | Consultar el menú disponible para un día |
| 3–4 | Registrar y consultar clientes |
| 5 | Crear pedidos Local, Llevar o Delivery |
| 6 | Agregar o quitar productos mientras el pedido sea editable |
| 7 | Mostrar detalle y comprobante |
| 8 | Cambiar estado o cancelar cuando corresponda |
| 9 | Cobrar con Efectivo, QR o Tarjeta |
| 10 | Reporte diario por modalidad y tres productos más vendidos |
| 11–12 | Guardar o cargar JSON; funcionalidad opcional de la guía |
| 13 | Cargar los datos de demostración en un restaurante vacío |
| 15 | Agregar o quitar componentes de un combo |
| 0 | Salir |

## Reglas de la variante A

| Concepto | Regla implementada |
|---|---|
| Combo | Dos o más componentes, incluidos otros combos; 10 % de descuento en cada nivel; sin ciclos |
| Bebida | Jarra = tres veces el precio por vaso; sin 2×1 |
| Disponibilidad | Chicharrón solo domingo; un combo exige disponibilidad de todos sus componentes |
| Local | Mesa 1–15, sin dos pedidos abiertos en la misma mesa; sin cargos adicionales |
| Llevar | Bs 2 por plato, incluidos los platos dentro de combos; bebidas sin envase |
| Delivery | Subtotal mínimo Bs 40 |
| Tarifas | Cercado Bs 8; Quillacollo Bs 15; Sacaba Bs 15; Vinto Bs 20 |
| Envío gratuito | Solo Cercado con subtotal desde Bs 150 |
| Efectivo | Debe cubrir el total; calcula cambio; sin redondeo extra a Bs 0,50 |
| QR | Código de transacción de diez dígitos |
| Tarjeta | Comisión del 3 %; no admitida para delivery |
| Validaciones | Precio positivo; cantidad 1–20; teléfono de ocho dígitos que comienza en 6 o 7 |

Los importes se calculan con `Decimal` y se redondean a dos decimales. Los precios de los combos ya incluyen el descuento: no se vuelve a restar al cobrar.

El flujo de estados es `REGISTRADO → EN_PREPARACION → LISTO → ENTREGADO`. Solo se cancela desde `REGISTRADO`. Los pedidos cobrados no permiten edición ni cancelación simple para mantener la consistencia de sus importes.

## Demostración del caso de referencia

Un silpancho de Bs 35 y un vaso de mocochinchi de Bs 6 forman un combo:

```text
Un combo:             (35 + 6) × 0,90 = Bs 36,90
Dos combos:               36,90 × 2 = Bs 73,80
Delivery a Quillacollo:              + Bs 15,00
Total:                                Bs 88,80
Efectivo recibido:                    Bs 100,00
Cambio:                               Bs 11,20
```

Con los datos demo, crea un delivery del cliente 1 a Quillacollo y agrega dos unidades del producto 8. Elige efectivo o un QR de diez dígitos. Los precios 35 y 6 proceden del caso de referencia de la guía; los otros datos son ficticios.

## Diagrama completo del sistema

![Diagrama de clases actual de la variante A](docs/diagrama_actual_variante_A.png)

[Abrir diagrama en resolución original](docs/diagrama_actual_variante_A.png) · [Tabla de clases corregida](docs/tabla_clases_corregida_A.png) · [Boceto original v1](docs/diagrama_v1.png)

Se conservan las tres jerarquías: `Producto` con `Plato`, `Bebida` y `Combo`; `Pedido` con `Local`, `Llevar` y `Delivery`; `MetodoPago` con `Efectivo`, `QR` y `Tarjeta`. Las tres bases son abstractas. El gestor es `Restaurante`; los detalles pertenecen a un pedido y referencian un producto. El combo agrega productos compartidos de forma recursiva.

## Código y organización

```text
.
├── main.py                 Menú de consola
├── restaurante.py          Registros, mesas, reportes y JSON
├── datos_demo.py            Datos ficticios de práctica
├── configuracion.json       Datos de la entrega y criterio del reporte
├── pruebas.py               32 casos ejecutables con assert
├── modelo/
│   ├── clientes.py          Cliente
│   ├── productos.py         Producto, Plato, Bebida y Combo
│   ├── pedidos.py           Pedido, modalidades, detalles y estados
│   ├── pagos.py             MetodoPago, Efectivo, QR y Tarjeta
│   ├── reglas.py            Exclusivamente las reglas A
│   └── utilidades.py        Validaciones y redondeo
├── datos/ejemplo_A.json      Archivo ficticio de ejemplo
├── docs/                    Diagramas, manuales y evidencias
└── .github/workflows/       Comprobaciones automáticas en GitHub
```

## Documentación detallada

- [Manual del proyecto y decisiones de diseño](docs/manual_del_proyecto.md).
- [Inventario de clases extraído del código](docs/inventario_clases.md).
- [Requisitos y evidencias de la guía](docs/requisitos_y_evidencias.md).
- [Revisión de cumplimiento y alcance](docs/revision_cumplimiento.md).
- [Acta y alcance comunicado por el estudiante](docs/acta_consultas.md).
- [Datos de la entrega](docs/datos_y_pendientes.md).
- [Preparación para la defensa individual](docs/defensa.md).
- [Git, historial y entrega](docs/git_y_entrega.md).
- [Bitácora de asistencia de IA](docs/bitacora_ia.md) y [registro personal](docs/registro_ia_saravia.md).
- [Verificación de las reglas A](docs/verificacion_reglas_a_24.txt).

`LEER_PRIMERO.html` reúne los documentos para leerlos localmente en un navegador. En GitHub, los enlaces Markdown anteriores ofrecen navegación directa.

## Alcance académico y autoría

Por indicación del estudiante del 23/11/2026, se excluyó la gestión de retrasos y compensaciones. El top 3 cuenta unidades por producto vendido como línea, incluidos los combos como productos. El cambio de alcance está registrado en el acta y no se atribuye a una confirmación directa del docente.

El proyecto se preparó con asistencia de IA, identificada en sus registros. La foto v1 no acredita firma docente; la revisión personal, las firmas y la defensa corresponden al estudiante. Los ocho commits iniciales son una incorporación de archivos existentes en una sesión; los siguientes contienen correcciones reales. Ese historial no acredita trabajo distribuido en semanas anteriores.

## Continuar haciendo cambios

```console
python pruebas.py
git status
git add ARCHIVOS_MODIFICADOS
git commit -m "Describe el cambio realizado"
git push
```

Publicar el proyecto no lo congela. Cada actualización conserva el historial y vuelve a ejecutar las comprobaciones de Actions. El archivo operativo `datos/restaurante.json`, los temporales y las cachés de Python están excluidos por `.gitignore`.
