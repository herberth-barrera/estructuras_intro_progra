import mysql.connector
from datetime import datetime
from flask import Flask, render_template, request, redirect, abort

app = Flask(__name__)

SUCURSALES = ["Escalón", "Santa Elena", "Colonia Médica"]


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


def obtener_empleados():
    """Empleados con cuántos documentos entregó y cuántos le corresponden (JOIN)."""
    conexion = conectar()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("""
        SELECT e.*, CAST(COALESCE(SUM(x.entregado), 0) AS UNSIGNED) AS entregados,
               COUNT(x.documento_id) AS total
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
        if fila["total"] > 0 and fila["entregados"] == fila["total"]:
            estado, clase = "Completo", "completo"
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
    cursor.execute("DELETE FROM expediente WHERE empleado_id = %s", (emp_id,))
    cursor.execute("DELETE FROM empleados WHERE id = %s", (emp_id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect("/empleados")


# ---------- RESUMEN (repetición + decisión) ----------
@app.route("/resumen")
def resumen():
    filas = obtener_empleados()
    completos = 0
    en_proceso = 0
    sin_documentos = 0
    detalle = []
    for fila in filas:
        if fila["total"] > 0 and fila["entregados"] == fila["total"]:
            completos = completos + 1
            clase, estado = "completo", "Completo"
        elif fila["entregados"] > 0:
            en_proceso = en_proceso + 1
            clase, estado = "proceso", "Incompleto (en proceso)"
        else:
            sin_documentos = sin_documentos + 1
            clase, estado = "vacio", "Incompleto (sin documentos)"
        detalle.append({"datos": fila, "estado": estado, "clase": clase})
    return render_template("resumen.html", detalle=detalle, total=len(filas),
                           completos=completos, en_proceso=en_proceso,
                           sin_documentos=sin_documentos,
                           incompletos=en_proceso + sin_documentos)


if __name__ == "__main__":
    app.run(debug=True)
