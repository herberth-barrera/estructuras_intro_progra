import io
import os
import mysql.connector
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, abort, send_file

app = Flask(__name__)

SUCURSALES = ["Escalón", "Santa Elena", "Colonia Médica"]

# --- TAREA 3: configuración de la subida de archivos ---
EXTENSIONES_PERMITIDAS = (".pdf", ".doc", ".docx")
# El MySQL de XAMPP trae max_allowed_packet en 1 MB: el límite se deja por debajo
# para que la conexión no se corte. Si suben max_allowed_packet en my.ini, pueden subir este valor.
MAX_BYTES = 700 * 1024
# Tope duro de Flask para rechazar de entrada cualquier subida enorme (error 413)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


def conectar():
    # En XAMPP el usuario es root y la contraseña va vacía
    return mysql.connector.connect(host="localhost", user="root", password="",
                                   database="hospital_hdd", charset="utf8mb4")


@app.errorhandler(mysql.connector.Error)
def error_mysql(e):
    return ('<link rel="stylesheet" href="/static/style.css">'
            "<h1>No se pudo usar la base de datos</h1>"
            "<p class='error'>Verifica que MySQL esté iniciado en XAMPP y que importaste "
            "crear_bd.sql en phpMyAdmin.</p>"), 500


# --- TAREA 3 ---
@app.errorhandler(413)
def archivo_demasiado_grande(e):
    return ('<link rel="stylesheet" href="/static/style.css">'
            "<h1>Archivo demasiado grande</h1>"
            "<p class='error'>El archivo supera el tamaño máximo permitido (%d KB). "
            "Vuelve atrás y elige uno más liviano.</p>" % (MAX_BYTES // 1024)), 413


def obtener_empleados():
    """Empleados con su checklist, sus archivos subidos y sus documentos vencidos (JOIN y subconsultas)."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*,
               CAST(COALESCE(SUM(x.entregado), 0) AS UNSIGNED) AS entregados,
               COUNT(x.documento_id) AS total,
               (SELECT COUNT(DISTINCT a.documento_id) FROM archivos a
                WHERE a.empleado_id = e.id) AS con_archivo,
               (SELECT COUNT(*) FROM archivos a
                WHERE a.empleado_id = e.id AND a.fecha_vencimiento < CURDATE()
                  AND a.version = (SELECT MAX(a2.version) FROM archivos a2
                                   WHERE a2.empleado_id = a.empleado_id
                                     AND a2.documento_id = a.documento_id)) AS vencidos
        FROM empleados e
        LEFT JOIN expediente x ON x.empleado_id = e.id
        GROUP BY e.id
        ORDER BY e.id
    """)
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()
    return filas


@app.route("/")
def inicio():
    return redirect("/empleados")


# ---------- CONSULTAR ----------
@app.route("/empleados")
def listar():
    filas = obtener_empleados()
    empleados = []
    for fila in filas:
        if fila["total"] > 0 and fila["con_archivo"] == fila["total"] and fila["vencidos"] == 0:
            estado, clase = "Completo", "completo"
        elif fila["vencidos"] > 0:
            estado, clase = "Con vencidos", "vencidos"
        else:
            estado, clase = "Incompleto", "incompleto"
        empleados.append({"datos": fila, "estado": estado, "clase": clase})
    return render_template("empleados.html", empleados=empleados)


# ---------- REGISTRAR ----------
@app.route("/empleados/nuevo", methods=["GET", "POST"])
def nuevo():
    error = ""
    datos = {"codigo": "", "nombre": "", "puesto": "", "area": "", "sucursal": "", "fecha_ingreso": ""}
    if request.method == "POST":
        for campo in datos:
            datos[campo] = request.form.get(campo, "").strip()

        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id FROM empleados WHERE codigo = %s", (datos["codigo"],))
        repetido = cursor.fetchone()

        fecha_valida = True
        try:
            datetime.strptime(datos["fecha_ingreso"], "%Y-%m-%d")
        except ValueError:
            fecha_valida = False

        if "" in datos.values():
            error = "Todos los campos son obligatorios."
        elif datos["sucursal"] not in SUCURSALES:
            error = "Selecciona una sucursal válida."
        elif not fecha_valida:
            error = "La fecha de ingreso no es válida."
        elif repetido:
            error = "Ya existe un empleado con ese código."
        else:
            cursor.execute(
                "INSERT INTO empleados (codigo, nombre, puesto, area, sucursal, fecha_ingreso) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (datos["codigo"], datos["nombre"], datos["puesto"], datos["area"],
                 datos["sucursal"], datos["fecha_ingreso"]))
            emp_id = cursor.lastrowid
            cursor.execute("SELECT id FROM documentos")
            for doc in cursor.fetchall():
                cursor.execute(
                    "INSERT INTO expediente (empleado_id, documento_id, entregado) VALUES (%s, %s, 0)",
                    (emp_id, doc["id"]))
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect("/empleados")
        cursor.close()
        conexion.close()
    return render_template("nuevo.html", error=error, datos=datos, sucursales=SUCURSALES)


# ---------- MODIFICAR (estado de los documentos del expediente) ----------
@app.route("/empleados/editar/<int:emp_id>", methods=["GET", "POST"])
def editar(emp_id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM empleados WHERE id = %s", (emp_id,))
    empleado = cursor.fetchone()
    if empleado is None:
        cursor.close()
        conexion.close()
        abort(404)
    cursor.execute("""
        SELECT d.id, d.nombre, x.entregado
        FROM expediente x JOIN documentos d ON d.id = x.documento_id
        WHERE x.empleado_id = %s ORDER BY d.id
    """, (emp_id,))
    docs = cursor.fetchall()

    error = ""
    if request.method == "POST":
        validos = {str(d["id"]) for d in docs}
        marcados = request.form.getlist("doc")
        if any(m not in validos for m in marcados):
            error = "Se recibió un documento que no pertenece al expediente."
        else:
            cursor.execute("UPDATE expediente SET entregado = 0 WHERE empleado_id = %s", (emp_id,))
            for m in marcados:
                cursor.execute(
                    "UPDATE expediente SET entregado = 1 WHERE empleado_id = %s AND documento_id = %s",
                    (emp_id, int(m)))
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect("/empleados")
    cursor.close()
    conexion.close()
    return render_template("expediente.html", empleado=empleado, docs=docs, error=error)


# ---------- ELIMINAR ----------
@app.route("/empleados/eliminar/<int:emp_id>", methods=["POST"])
def eliminar(emp_id):
    conexion = conectar()
    cursor = conexion.cursor()
    # Primero los hijos y luego el padre: no quedan registros huérfanos
    # (la llave foránea con ON DELETE CASCADE también lo garantiza)
    cursor.execute("DELETE FROM archivos WHERE empleado_id = %s", (emp_id,))   # TAREA 3
    cursor.execute("DELETE FROM expediente WHERE empleado_id = %s", (emp_id,))
    cursor.execute("DELETE FROM empleados WHERE id = %s", (emp_id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect("/empleados")


# ---------- TAREA 3: LISTADO DE ARCHIVOS Y VERSIONES ----------
@app.route("/empleados/<int:emp_id>/archivos")
def ver_archivos(emp_id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM empleados WHERE id = %s", (emp_id,))
    empleado = cursor.fetchone()
    if empleado is None:
        cursor.close()
        conexion.close()
        abort(404)
    # Solo las columnas que se muestran: NO se trae la columna contenido
    cursor.execute("""
        SELECT a.id, a.documento_id, d.nombre AS documento, a.version, a.nombre_original,
               a.tamano, a.fecha_vencimiento, a.fecha_subida
        FROM archivos a JOIN documentos d ON d.id = a.documento_id
        WHERE a.empleado_id = %s
        ORDER BY d.id, a.version DESC
    """, (emp_id,))
    filas = cursor.fetchall()
    cursor.execute("""
        SELECT d.nombre FROM documentos d
        WHERE d.id NOT IN (SELECT documento_id FROM archivos WHERE empleado_id = %s)
        ORDER BY d.id
    """, (emp_id,))
    pendientes = cursor.fetchall()
    cursor.close()
    conexion.close()

    hoy = date.today()
    vistos = set()
    lista = []
    for fila in filas:
        # Como vienen de la versión más reciente a la más antigua, la primera de cada documento es la última
        es_ultima = fila["documento_id"] not in vistos
        vistos.add(fila["documento_id"])
        if not es_ultima:
            estado, clase = "Versión anterior", "anterior"
        elif fila["fecha_vencimiento"] is not None and fila["fecha_vencimiento"] < hoy:
            estado, clase = "Vencido", "vencido"
        else:
            estado, clase = "Vigente", "vigente"
        lista.append({"datos": fila, "estado": estado, "clase": clase})
    return render_template("archivos.html", empleado=empleado, archivos=lista, pendientes=pendientes)


# ---------- TAREA 3: SUBIR ARCHIVO (crea una versión nueva) ----------
@app.route("/empleados/<int:emp_id>/archivos/nuevo", methods=["GET", "POST"])
def subir(emp_id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM empleados WHERE id = %s", (emp_id,))
    empleado = cursor.fetchone()
    if empleado is None:
        cursor.close()
        conexion.close()
        abort(404)
    cursor.execute("SELECT id, nombre, requiere_vencimiento FROM documentos ORDER BY id")
    documentos = cursor.fetchall()

    error = ""
    datos = {"documento_id": "", "fecha_vencimiento": ""}
    if request.method == "POST":
        datos["documento_id"] = request.form.get("documento_id", "").strip()
        datos["fecha_vencimiento"] = request.form.get("fecha_vencimiento", "").strip()

        archivo = request.files.get("archivo")
        nombre = ""
        contenido = b""
        if archivo is not None and archivo.filename:
            # Solo el nombre, sin carpetas; el nombre nunca se usa como ruta en disco
            nombre = archivo.filename.replace("\\", "/").split("/")[-1].strip()[:255]
            contenido = archivo.read()
        extension = os.path.splitext(nombre)[1].lower()

        documento = None
        for d in documentos:
            if str(d["id"]) == datos["documento_id"]:
                documento = d

        fecha_valida = True
        if datos["fecha_vencimiento"] != "":
            try:
                datetime.strptime(datos["fecha_vencimiento"], "%Y-%m-%d")
            except ValueError:
                fecha_valida = False

        if documento is None:
            error = "Selecciona el tipo de documento."
        elif nombre == "":
            error = "Selecciona un archivo."
        elif extension not in EXTENSIONES_PERMITIDAS:
            error = "Solo se permiten archivos PDF, DOC o DOCX."
        elif len(contenido) == 0:
            error = "El archivo está vacío."
        elif len(contenido) > MAX_BYTES:
            error = "El archivo supera el tamaño máximo de %d KB." % (MAX_BYTES // 1024)
        elif documento["requiere_vencimiento"] and datos["fecha_vencimiento"] == "":
            error = "Este documento requiere fecha de vencimiento."
        elif not fecha_valida:
            error = "La fecha de vencimiento no es válida."
        else:
            # Versión siguiente: la primera es 1; subir nunca reemplaza a la anterior
            cursor.execute(
                "SELECT MAX(version) AS ultima FROM archivos WHERE empleado_id = %s AND documento_id = %s",
                (emp_id, documento["id"]))
            fila = cursor.fetchone()
            version = (fila["ultima"] or 0) + 1
            cursor.execute(
                "INSERT INTO archivos (empleado_id, documento_id, version, nombre_original, tamano, "
                "contenido, fecha_vencimiento) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (emp_id, documento["id"], version, nombre, len(contenido), contenido,
                 datos["fecha_vencimiento"] or None))
            # Un documento subido cuenta como entregado en el checklist del expediente
            cursor.execute(
                "UPDATE expediente SET entregado = 1 WHERE empleado_id = %s AND documento_id = %s",
                (emp_id, documento["id"]))
            conexion.commit()
            cursor.close()
            conexion.close()
            return redirect("/empleados/%d/archivos" % emp_id)
    cursor.close()
    conexion.close()
    return render_template("subir.html", empleado=empleado, documentos=documentos, datos=datos,
                           error=error, max_kb=MAX_BYTES // 1024)


# ---------- TAREA 3: DESCARGAR ----------
@app.route("/archivos/<int:archivo_id>/descargar")
def descargar(archivo_id):
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT nombre_original, contenido FROM archivos WHERE id = %s", (archivo_id,))
    fila = cursor.fetchone()
    cursor.close()
    conexion.close()
    if fila is None:
        abort(404)
    return send_file(io.BytesIO(fila["contenido"]), as_attachment=True,
                     download_name=fila["nombre_original"])


# ---------- RESUMEN (repetición + decisión), ahora con los archivos realmente subidos ----------
@app.route("/resumen")
def resumen():
    filas = obtener_empleados()
    completos = 0
    con_vencidos = 0
    en_proceso = 0
    sin_archivos = 0
    docs_subidos = 0
    docs_requeridos = 0
    detalle = []
    for fila in filas:
        docs_subidos = docs_subidos + fila["con_archivo"]
        docs_requeridos = docs_requeridos + fila["total"]
        if fila["total"] > 0 and fila["con_archivo"] == fila["total"] and fila["vencidos"] == 0:
            completos = completos + 1
            clase, estado = "completo", "Completo (todos subidos y vigentes)"
        elif fila["vencidos"] > 0:
            con_vencidos = con_vencidos + 1
            clase, estado = "vencidos", "Con documentos vencidos"
        elif fila["con_archivo"] > 0:
            en_proceso = en_proceso + 1
            clase, estado = "proceso", "Incompleto (en proceso)"
        else:
            sin_archivos = sin_archivos + 1
            clase, estado = "vacio", "Incompleto (sin archivos)"
        detalle.append({"datos": fila, "estado": estado, "clase": clase})
    return render_template("resumen.html", detalle=detalle, total=len(filas),
                           completos=completos, con_vencidos=con_vencidos,
                           en_proceso=en_proceso, sin_archivos=sin_archivos,
                           docs_subidos=docs_subidos, docs_requeridos=docs_requeridos)


if __name__ == "__main__":
    app.run(debug=True)
