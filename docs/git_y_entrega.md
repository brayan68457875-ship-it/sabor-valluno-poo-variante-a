# Git y entrega del proyecto

Esta carpeta utiliza un repositorio local en la rama `main`. Los ocho commits corresponden a la incorporación, por componentes, de un proyecto que ya existía. Se crean en la sesión actual, con las fechas reales registradas por Git. No se presentan como desarrollo distribuido en semanas anteriores.

## Ocho bloques de incorporación

| Bloque | Contenido |
|---|---|
| 1 | Configuración de la variante A y exclusiones de Git |
| 2 | Validaciones comunes, cliente y reglas A |
| 3 | Jerarquía de productos y combos anidados |
| 4 | Pedidos, detalles, estados y modalidades |
| 5 | Efectivo, QR y tarjeta |
| 6 | Gestor, menú de consola y demostración |
| 7 | Pruebas y ejemplo JSON |
| 8 | Diagramas, manuales y documentación del uso de IA |

El código y los materiales se generaron con asistencia de IA, declarada en los registros. Esta organización del historial no acredita por sí misma las fases presenciales, el calendario de commits de la guía, las consultas docentes ni la defensa individual.

## Consultar el historial en VS Code

En Control de código fuente se puede revisar el gráfico o historial del repositorio. En una terminal del proyecto también se puede ejecutar:

```console
git log --oneline --reverse
git rev-list --count HEAD
git status
```

Para ver la fecha real de cada commit:

```console
git log --format="%h %ai %s"
```

## GitHub

El repositorio está publicado con visibilidad pública en [brayan68457875-ship-it/sabor-valluno-poo-variante-a](https://github.com/brayan68457875-ship-it/sabor-valluno-poo-variante-a). El remoto origin apunta a esa dirección y la rama de trabajo es main. Las modificaciones futuras se envían con git push. No se modificó el proyecto distinto llamado «proyecto algebra».

La firma, defensa y evidencia del trabajo personal corresponden a actuaciones reales del estudiante. El acta describe el alcance actual. Los cambios futuros deben producir commits que describan cambios efectivos; no se cambian fechas para simular trabajo anterior.
