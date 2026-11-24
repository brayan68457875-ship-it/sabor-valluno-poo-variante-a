# Sistema de pedidos Sabor Valluno · Variante A

**Estudiante:** Brayan Saravia Garay  
**Carrera:** Ingeniería de Sistemas  
**Asignatura:** Programación Orientada a Objetos  
**Variante asignada:** A  
**Paralelo:** B  
**Docente:** Ing. Roy Carrasco  
**Entrega:** 24 de noviembre de 2026  
**Institución:** Universidad Adventista de Bolivia.

Aplicación de consola en Python para registrar productos, clientes, pedidos y pagos del restaurante ficticio Sabor Valluno. Conserva las clases del diagrama entregado y aplica exclusivamente la variante A, confirmada por Brayan el 23/11/2026. El paralelo del estudiante continúa siendo B.

## Cómo ejecutarlo

1. Extraer el ZIP completo y abrir la carpeta `Sabor_Valluno_Variante_A` en VS Code.
2. Usar Python 3.10 o posterior. No se instala nada con pip: todo utiliza la biblioteca estándar.
3. Abrir una terminal dentro de esta carpeta y ejecutar:

```console
python main.py --variante A --demo
```

En Windows también puede usarse `py -3` en lugar de `python`. `python main.py` inicia directamente con la variante A asignada. `--demo` carga productos y un cliente ficticios; omitirlo permite empezar sin registros. Esta entrega rechaza variantes distintas de A.

```console
python pruebas.py
python main.py --demo
python main.py --cargar datos/restaurante.json
```

No ejecutar las pruebas con `-O`, porque ese modo elimina las comprobaciones `assert`.

El menú permite registrar productos y combos, consultar el menú por día, registrar clientes, crear las tres modalidades de pedido, agregar/quitar productos, cambiar estados, cobrar, consultar el detalle, generar reportes y guardar/cargar JSON. La opción 15 permite agregar o quitar componentes de un combo. Los datos se conservan entre sesiones únicamente si se guardan en JSON.

## Primera demostración

Con `python main.py --variante A --demo`, elegir 5 para crear un pedido del cliente 1, modalidad 3, zona Quillacollo y una dirección de ejemplo. Elegir 6, seleccionar el pedido 1, agregar el producto 8, cantidad 2. El comprobante mostrará Bs 73,80 de subtotal, Bs 15 de envío y Bs 88,80 de total. Elegir 9 y pagar con QR de diez dígitos o efectivo suficiente. Para entregarlo, elegir 8 sucesivamente con EN_PREPARACION, LISTO y ENTREGADO.

La demostración usa los precios 35 y 6 que aparecen en la guía; los otros precios y el cliente son ficticios y están identificados en `datos_demo.py`.

## Estructura de la entrega

```text
Sabor_Valluno_Variante_A/
  main.py                    Menú de consola
  restaurante.py             Registros, mesas, reportes y JSON
  datos_demo.py              Datos ficticios para practicar
  configuracion.json         Datos del estudiante y alcance actual
  pruebas.py                 Casos ejecutables con assert
  modelo/
    clientes.py              Cliente
    productos.py             Producto, Plato, Bebida, Combo
    pedidos.py               Pedido, Local, Llevar, Delivery,
                             DetalleProducto y EstadoPedido
    pagos.py                 MetodoPago, Efectivo, QR, Tarjeta
    reglas.py                ReglasVariante, variante A
    utilidades.py            Importes, fechas y validaciones
  datos/                     Archivos JSON de ejemplo
  docs/
    diagrama_v1.png           Imagen del boceto proporcionado
    diagrama_v2.png           Diagrama enriquecido actualizado
    manual_del_proyecto.md   Explicación de funcionamiento y diseño
    requisitos_y_evidencias.md
    datos_y_pendientes.md
    acta_consultas.md
    bitacora_ia.md
    registro_ia_saravia.md
    defensa.md
    inventario_clases.md
    resultados_pruebas.txt
    git_y_entrega.md
```

La fotografía del boceto se conserva como evidencia aportada por el usuario. No se afirma que esté firmada por el docente: esa verificación y la firma corresponden al estudiante y al docente.

## Variante A asignada

| Perfil | Combo | Envase para llevar | Envío gratis | Mínimo delivery | Particularidad |
|---|---|---|---|---|---|
| A | 10 % | Bs 2 por plato | Desde Bs 150, Cercado | Bs 40 | Chicharrón solo domingo |

Las tarifas son Cercado 8, Quillacollo 15, Sacaba 15 y Vinto 20. En A, solo Cercado ofrece envío gratuito desde Bs 150 de subtotal. El mínimo de delivery es Bs 40. La variante queda fija en A.

## Estado y alcance de la entrega

Ya se incorporaron los datos personales que proporcionó Brayan. La institución y la variante A están incorporadas. El repositorio existe localmente y todavía no tiene remoto de GitHub. Ver `docs/datos_y_pendientes.md` y `docs/acta_consultas.md`.

El top 3 cuenta unidades por producto vendido como línea, incluidos los combos como productos. Por indicación del estudiante se retiró la gestión de retrasos y compensaciones. El cambio se registra en docs/acta_consultas.md.

La gestión de retrasos y compensaciones que aparecía en la guía original se excluye del alcance actual por indicación del estudiante del 23/11/2026.

Los diagramas y el código se prepararon con ayuda de IA. La bitácora registra la asistencia; la revisión y comprensión son responsabilidad del estudiante. La firma, la defensa, las consultas reales, el historial de trabajo de semanas anteriores y la publicación en GitHub requieren actuaciones reales del estudiante; no se han fabricado.

## Historial local de esta incorporación

Los archivos existentes se incorporan en ocho commits por componentes, todos con las fechas reales de esta sesión. Este historial no acredita semanas de trabajo anteriores. Consultar `docs/git_y_entrega.md`. El repositorio no se ha publicado en GitHub.
