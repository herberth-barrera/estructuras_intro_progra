import mysql.connector

# Datos de conexion por defecto de XAMPP: usuario root, sin contrasena
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="hospital_hdd",
)
cursor = conexion.cursor(dictionary=True)

cursor.execute("SELECT id, nombre FROM empleados ORDER BY id")
empleados = cursor.fetchall()

for empleado in empleados:
    print(empleado["id"], empleado["nombre"])

cursor.close()
conexion.close()
