# Expedientes Digitales – Hospital de Diagnóstico (Fase 2)

## Qué hace el sistema
Administra los expedientes de personal del Hospital de Diagnóstico. Permite registrar empleados, consultar el estado de su expediente, modificar qué documentos del checklist ya entregó y eliminar empleados. Además, una página de resumen recorre todos los expedientes y los clasifica como completos o incompletos.

## Cómo ejecutarlo
```
pip install flask
python crear_bd.py
python app.py
```
Abrir en el navegador: http://127.0.0.1:5000/empleados

## Estructura de archivos
```
fase2_equipo/
|-- app.py              # rutas de Flask y lógica del sistema
|-- crear_bd.py         # crea las tablas y carga 6 empleados de ejemplo
|-- README.md
|-- templates/
|   |-- base.html       # plantilla común (enlaza static/style.css)
|   |-- empleados.html  # listado de empleados con su estado
|   |-- nuevo.html      # formulario de registro
|   |-- expediente.html # formulario para modificar documentos
|   |-- resumen.html    # resumen con clasificaciones
|-- static/
|   |-- style.css       # hoja de estilos única del sitio
```

## Rutas
| Ruta | Método | Función |
|---|---|---|
| http://127.0.0.1:5000/empleados | GET | Consultar: lista de empleados y estado del expediente |
| http://127.0.0.1:5000/empleados/nuevo | GET, POST | Registrar: formulario con validación |
| http://127.0.0.1:5000/empleados/editar/1 | GET, POST | Modificar: marcar/desmarcar documentos entregados |
| http://127.0.0.1:5000/empleados/eliminar/1 | POST | Eliminar un empleado (pide confirmación en el navegador) |
| http://127.0.0.1:5000/resumen | GET | Resumen con contadores por clasificación |

## Base de datos (SQLite, `hospital.db`)
- **empleados**: id, codigo (único), nombre, puesto, area, sucursal, fecha_ingreso
- **documentos**: id, nombre (catálogo de los 13 documentos del checklist)
- **expediente**: empleado_id, documento_id, entregado (0 = falta, 1 = entregado)

Todas las sentencias SQL usan parámetros `?`.

## Cómo funciona el resumen
`/resumen` lee todos los empleados con cuántos documentos entregó cada uno y los recorre con un `for`. En cada vuelta usa `if/elif/else`:
- **Completo** (verde): entregó todos los documentos.
- **Incompleto en proceso** (naranja): entregó al menos uno, pero no todos.
- **Incompleto sin documentos** (rojo): no ha entregado ninguno.

Cada rama suma a un contador y la página muestra cuántos hay de cada tipo, el total de incompletos y el detalle por empleado.

## Equipo: parte de código desarrollada por cada integrante
- Herberth Barrera: (completar) conexión a la base de datos y `crear_bd.py`
- Andrés Romero: (completar) registro con validación
- Camila Herrera: (completar) listado, bucle y decisión del resumen
- Héctor Calderón: (completar) formularios, modificar/eliminar y hoja de estilos
