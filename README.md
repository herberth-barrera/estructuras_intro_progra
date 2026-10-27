Expedientes Digitales – Hospital de Diagnóstico (Desafío 2)
Qué hace el sistema

Administra los expedientes de personal del Hospital de Diagnóstico sobre MySQL (XAMPP). Permite registrar empleados, consultar el estado de su expediente, modificar qué documentos del checklist ya entregó y eliminar empleados sin dejar documentos huérfanos. Una página de resumen recorre todos los expedientes y los clasifica como completos o incompletos.

Cómo ejecutarlo desde cero
Abrir el Panel de Control de XAMPP e iniciar MySQL (y Apache, para phpMyAdmin).
Abrir http://localhost/phpmyadmin/, ir a la pestaña Importar, elegir crear_bd.sql y presionar Continuar. Se crea la base hospital_hdd con sus tablas y datos de ejemplo.
Instalar las dependencias:
   pip install -r requirements.txt
Ejecutar el sistema:
   python app.py
Abrir en el navegador: http://127.0.0.1:5000/empleados

Usuario de MySQL: root, sin contraseña (valores por defecto de XAMPP).

Estructura de archivos
desafio2_equipo/
|-- app.py              # rutas de Flask y lógica del sistema
|-- crear_bd.sql        # crea la base, las tablas y carga datos de ejemplo
|-- requirements.txt    # flask y mysql-connector-python
|-- README.md
|-- templates/
|   |-- base.html       # plantilla común (enlaza static/style.css)
|   |-- empleados.html  # listado con estado del expediente
|   |-- nuevo.html      # formulario de registro
|   |-- expediente.html # formulario para modificar documentos
|   |-- resumen.html    # resumen con clasificaciones
|-- static/
|   |-- style.css       # única hoja de estilos del sitio
Rutas
Ruta	Método	Función
http://127.0.0.1:5000/empleados	GET	Consultar: empleados con su estado (consulta con JOIN)
http://127.0.0.1:5000/empleados/nuevo	GET, POST	Registrar con validación
http://127.0.0.1:5000/empleados/editar/1	GET, POST	Modificar: marcar/desmarcar documentos entregados
http://127.0.0.1:5000/empleados/eliminar/1	POST	Eliminar un empleado y su expediente
http://127.0.0.1:5000/resumen	GET	Resumen con contadores por clasificación
Base de datos (MySQL, base hospital_hdd)
empleados: id (PK), codigo (único), nombre, puesto, area, sucursal, fecha_ingreso
documentos: id (PK), nombre (catálogo de los 12 documentos del checklist)
expediente: empleado_id (PK, FK), documento_id (PK, FK), entregado (0 = falta, 1 = entregado)

Llaves foráneas:

expediente.empleado_id → empleados.id con ON DELETE CASCADE: al eliminar un empleado se eliminan sus documentos y no quedan registros huérfanos.
expediente.documento_id → documentos.id.

Las consultas usan la librería mysql-connector-python con parámetros %s.

Consulta con JOIN

/empleados y /resumen obtienen los datos con un LEFT JOIN entre empleados y expediente (agrupado por empleado) que calcula cuántos documentos entregó cada uno y cuántos le corresponden. /empleados/editar/<id> usa un JOIN entre expediente y documentos para mostrar el nombre de cada documento y su estado.

Cómo funciona el resumen

/resumen lee todos los empleados con su conteo de documentos y los recorre con un for. En cada vuelta decide con if/elif/else:

Completo (verde): entregó todos los documentos.
Incompleto en proceso (naranja): entregó al menos uno, pero no todos.
Incompleto sin documentos (rojo): no ha entregado ninguno.

Cada rama suma a un contador y la página muestra cuántos hay de cada tipo.

## Equipo: parte de código desarrollada por cada integrante
- Herberth Barrera: conexión a la base de datos y `crear_bd.py`
- Andrés Romero: registro con validación
- Camila Herrera: listado, bucle y decisión del resumen
- Héctor Calderón: formularios, modificar/eliminar y hoja de estilos
