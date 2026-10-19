import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, abort

app = Flask(__name__)

SUCURSALES = ["Escalón", "Santa Elena", "Colonia Médica"]


def conectar():
    conexion = sqlite3.connect("hospital.db")
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


def obtener_empleados():
    """Empleados con cuántos documentos entregó y cuántos le corresponden."""
    conexion = conectar()
    filas = conexion.execute("""
        SELECT e.*, COALESCE(SUM(x.entregado), 0) AS entregados, COUNT(x.documento_id) AS total
        FROM empleados e
        LEFT JOIN expediente x ON x.empleado_id = e.id
        GROUP BY e.id
        ORDER BY e.id
    """).fetchall()
    conexion.close()
    return filas


@app.route("/")
def inicio():
    return redirect("/empleados")


# Consulta de empleados y sus documentos
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


# Registro de nuevo empleado
@app.route("/empleados/nuevo", methods=["GET", "POST"])
def nuevo():
    error = ""
    datos = {"codigo": "", "nombre": "", "puesto": "", "area": "", "sucursal": "", "fecha_ingreso": ""}
    if request.method == "POST":
        for campo in datos:
            datos[campo] = request.form.get(campo, "").strip()

        conexion = conectar()
        repetido = conexion.execute("SELECT id FROM empleados WHERE codigo = ?", (datos["codigo"],)).fetchone()

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
            cur = conexion.execute(
                "INSERT INTO empleados (codigo, nombre, puesto, area, sucursal, fecha_ingreso) VALUES (?, ?, ?, ?, ?, ?)",
                (datos["codigo"], datos["nombre"], datos["puesto"], datos["area"], datos["sucursal"], datos["fecha_ingreso"]))
            emp_id = cur.lastrowid
            for doc in conexion.execute("SELECT id FROM documentos").fetchall():
                conexion.execute(
                    "INSERT INTO expediente (empleado_id, documento_id, entregado) VALUES (?, ?, 0)",
                    (emp_id, doc["id"]))
            conexion.commit()
            conexion.close()
            return redirect("/empleados")
        conexion.close()
    return render_template("nuevo.html", error=error, datos=datos, sucursales=SUCURSALES)


# Modificar información de empleado
@app.route("/empleados/editar/<int:emp_id>", methods=["GET", "POST"])
def editar(emp_id):
    conexion = conectar()
    empleado = conexion.execute("SELECT * FROM empleados WHERE id = ?", (emp_id,)).fetchone()
    if empleado is None:
        conexion.close()
        abort(404)
    docs = conexion.execute("""
        SELECT d.id, d.nombre, x.entregado
        FROM expediente x JOIN documentos d ON d.id = x.documento_id
        WHERE x.empleado_id = ? ORDER BY d.id
    """, (emp_id,)).fetchall()

    error = ""
    if request.method == "POST":
        validos = {str(d["id"]) for d in docs}
        marcados = request.form.getlist("doc")
        if any(m not in validos for m in marcados):
            error = "Se recibió un documento que no pertenece al expediente."
        else:
            conexion.execute("UPDATE expediente SET entregado = 0 WHERE empleado_id = ?", (emp_id,))
            for m in marcados:
                conexion.execute(
                    "UPDATE expediente SET entregado = 1 WHERE empleado_id = ? AND documento_id = ?",
                    (emp_id, int(m)))
            conexion.commit()
            conexion.close()
            return redirect("/empleados")
    conexion.close()
    return render_template("expediente.html", empleado=empleado, docs=docs, error=error)


# Eliminar registro de empleado
@app.route("/empleados/eliminar/<int:emp_id>", methods=["POST"])
def eliminar(emp_id):
    conexion = conectar()
    conexion.execute("DELETE FROM expediente WHERE empleado_id = ?", (emp_id,))
    conexion.execute("DELETE FROM empleados WHERE id = ?", (emp_id,))
    conexion.commit()
    conexion.close()
    return redirect("/empleados")


# Resumen de los empleados
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
