# Expediente Digital

Aplicación web sencilla hecha con **Flask** que muestra un checklist de documentos y calcula automáticamente el estado del perfil según cuántos documentos se han marcado como entregados.

## Características

- Checklist interactivo con 4 documentos: **DUI**, **Antecedentes**, **Curriculum vitae** y **Licencia médica**.
- Al marcar o desmarcar una casilla, el formulario se envía solo (`onchange="this.form.submit()"`) y la página se actualiza.
- Insignia (badge) de color que indica el estado del perfil.
- Contador de documentos completos (por ejemplo, `2 de 4`).
- Todo el HTML y CSS se genera desde una sola ruta, sin plantillas externas.

## Requisitos

- Python 3.8 o superior
- Flask

## Instalación

```bash
# 1. (Opcional) Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate      # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install flask
```

## Ejecución

Guarda el código en un archivo, por ejemplo `app.py`, y ejecútalo:

```bash
python app.py
```

Luego abre en el navegador:

```
http://127.0.0.1:5000/documentos
```

> El servidor corre con `debug=True`, por lo que se reinicia solo al guardar cambios. **No uses este modo en producción.**

## Uso

### Ruta disponible

| Método | Ruta          | Descripción                                   |
|--------|---------------|-----------------------------------------------|
| GET    | `/documentos` | Muestra el expediente y el estado del perfil. |

### Parámetros de la URL

Cada documento se controla con un parámetro. Un documento se considera **entregado** solo si su valor es exactamente `si`.

| Parámetro      | Documento         |
|----------------|-------------------|
| `dui`          | DUI               |
| `antecedentes` | Antecedentes      |
| `cv`           | Curriculum vitae  |
| `licencia`     | Licencia médica   |

### Ejemplos

```
/documentos                                   → ningún documento marcado
/documentos?dui=si&cv=si                      → 2 de 4 documentos
/documentos?dui=si&antecedentes=si&cv=si&licencia=si   → perfil completo
```

## Estados del perfil

El estado depende del número de documentos marcados:

| Documentos completos | Estado             | Color              |
|----------------------|--------------------|--------------------|
| 0                    | Perfil incompleto  | Rojo `#e74c3c`     |
| 1 a 3                | Perfil en proceso  | Naranja `#f39c12`  |
| 4                    | Perfil completado  | Verde `#2ecc71`    |

## Cómo funciona

1. **Lectura de parámetros:** con `request.args.get(...)` se leen los cuatro valores y se convierten a booleano (`True` si el valor es `"si"`).
2. **Listas paralelas:** `nombres_documentos`, `estados_documentos` y `params` mantienen el mismo orden, de modo que el índice `i` corresponde al mismo documento en las tres.
3. **Generación del checklist:** se recorre `estados_documentos`; por cada documento se construye un `<li>` con su checkbox (marcado si corresponde) y se incrementa el `contador`.
4. **Evaluación del perfil:** según el valor de `contador` se elige el texto y el color de la insignia.
5. **Respuesta:** la función devuelve una página HTML completa (con CSS incrustado) usando f-strings. Las llaves del CSS se escapan duplicándolas (`{{ }}`).

## Estructura del proyecto

```
.
├── app.py        # Aplicación Flask (ruta /documentos)
└── README.md     # Este archivo
```

## Posibles mejoras

- Mover el HTML a plantillas **Jinja2** (`render_template`) para separar lógica y presentación.
- Guardar el estado de los documentos en una base de datos en lugar de la URL.
- Agregar un nombre de usuario dinámico en lugar de un título fijo.
- Añadir un campo para subir los archivos de cada documento.
- Desactivar `debug=True` y usar un servidor como Gunicorn en producción.

## Autor

Proyecto creado por **Herberth Barrera**.
