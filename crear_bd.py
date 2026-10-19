import sqlite3

DOCUMENTOS = [
    "2 fotografías tamaño cédula",
    "Título de último grado académico y certificaciones",
    "Carnet de Junta de Vigilancia (según aplique)",
    "Curriculum vitae",
    "Solvencia de la Policía Nacional Civil",
    "Antecedentes penales",
    "2 recomendaciones laborales",
    "2 recomendaciones personales",
    "Fotocopia de NIT",
    "Fotocopia de DUI",
    "Fotocopia de AFP",
    "Fotocopia de ISSS",
    
]

# Informacion de cada empleado
EMPLEADOS = [
    ("HDD-001", "Camila Herrera", "Médico general", "Consulta externa", "Escalón", "2024-02-12", 13),
    ("HDD-002", "Andres Weil", "Técnico de laboratorio", "Laboratorio", "Santa Elena", "2025-05-20", 9),
    ("HDD-003", "Hector Calderon", "Recepcionista", "Admisión", "Colonia Médica", "2026-01-08", 4),
    ("HDD-004", "Herberth Barrera", "Radiólogo", "Imagenología", "Escalón", "2023-09-01", 13),
    ("HDD-005", "Daniel Gregg", "Enfermero", "Emergencias", "Santa Elena", "2026-08-17", 0),
    ("HDD-006", "Belen Diaz", "Analista de talento humano", "Talento Humano", "Colonia Médica", "2025-11-03", 12),
]

conexion = sqlite3.connect("hospital.db")
conexion.execute("PRAGMA foreign_keys = ON")
conexion.executescript("""
DROP TABLE IF EXISTS expediente;
DROP TABLE IF EXISTS documentos;
DROP TABLE IF EXISTS empleados;

CREATE TABLE empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre TEXT NOT NULL,
    puesto TEXT NOT NULL,
    area TEXT NOT NULL,
    sucursal TEXT NOT NULL,
    fecha_ingreso TEXT NOT NULL
);
CREATE TABLE documentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL
);
CREATE TABLE expediente (
    empleado_id INTEGER NOT NULL,
    documento_id INTEGER NOT NULL,
    entregado INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (empleado_id, documento_id),
    FOREIGN KEY (empleado_id) REFERENCES empleados(id) ON DELETE CASCADE,
    FOREIGN KEY (documento_id) REFERENCES documentos(id)
);
""")

for nombre in DOCUMENTOS:
    conexion.execute("INSERT INTO documentos (nombre) VALUES (?)", (nombre,))
ids_docs = [f[0] for f in conexion.execute("SELECT id FROM documentos ORDER BY id")]

for codigo, nombre, puesto, area, sucursal, fecha, entregados in EMPLEADOS:
    cur = conexion.execute(
        "INSERT INTO empleados (codigo, nombre, puesto, area, sucursal, fecha_ingreso) VALUES (?, ?, ?, ?, ?, ?)",
        (codigo, nombre, puesto, area, sucursal, fecha))
    emp_id = cur.lastrowid
    for posicion, doc_id in enumerate(ids_docs):
        estado = 1 if posicion < entregados else 0
        conexion.execute(
            "INSERT INTO expediente (empleado_id, documento_id, entregado) VALUES (?, ?, ?)",
            (emp_id, doc_id, estado))

conexion.commit()
conexion.close()
print("Base de datos hospital.db creada con", len(EMPLEADOS), "empleados y", len(DOCUMENTOS), "documentos por expediente.")
