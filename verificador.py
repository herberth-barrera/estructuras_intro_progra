from flask import Flask, request

app = Flask(__name__)

@app.route("/documentos")
def documentos():
    dui = request.args.get("dui") == "si"
    antecedentes = request.args.get("antecedentes") == "si"
    cv = request.args.get("cv") == "si"
    licencia = request.args.get("licencia") == "si"

    # Dos listas paralelas: el nombre y su estado, en el mismo orden
    nombres_documentos = ["DUI", "Antecedentes", "Curriculum vitae", "Licencia médica"]
    estados_documentos = [dui, antecedentes, cv, licencia]
    
    # Nombres de parámetros para la URL (corresponden a las 4 variables)
    params = ["dui", "antecedentes", "cv", "licencia"]

    contador = 0
    filas_html = ""
    for i in range(len(estados_documentos)):
        if estados_documentos[i]:
            contador += 1
            checked_attr = "checked"
        else:
            checked_attr = ""
            
        # Generamos el checklist dentro de tu misma variable filas_html
        filas_html += f"""
        <li>
            <input type="checkbox" id="{params[i]}" name="{params[i]}" value="si" {checked_attr} onchange="this.form.submit()">
            <label for="{params[i]}">{nombres_documentos[i]}</label>
        </li>
        """

    # Evaluacion de estado del perfil según el contador
    if contador == 0:
        estado_perfil = "Perfil incompleto"
        color_badge = "#e74c3c"  # Rojo
    elif contador < len(estados_documentos):
        estado_perfil = "Perfil en proceso"
        color_badge = "#f39c12"  # Naranja
    else:
        estado_perfil = "Perfil completado"
        color_badge = "#2ecc71"  # Verde

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Expediente Digital</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f7f6;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .card {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                width: 350px;
            }}
            h2 {{
                margin-top: 0;
                color: #2c3e50;
            }}
            .badge {{
                display: inline-block;
                padding: 6px 12px;
                color: white;
                background-color: {color_badge};
                border-radius: 15px;
                font-weight: bold;
                font-size: 14px;
                margin-bottom: 15px;
            }}
            ul {{
                list-style-type: none;
                padding-left: 0;
            }}
            li {{
                padding: 10px 0;
                border-bottom: 1px solid #eee;
                font-size: 16px;
                display: flex;
                align-items: center;
            }}
            input[type="checkbox"] {{
                width: 18px;
                height: 18px;
                margin-right: 10px;
                cursor: pointer;
            }}
            label {{
                cursor: pointer;
            }}
            p {{
                font-weight: bold;
                color: #555;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Expediente de doctor Herberth</h2>
            <div class="badge">{estado_perfil}</div>
            
            <form method="GET" action="/documentos">
                <ul>{filas_html}</ul>
            </form>

            <p>Documentos completos: {contador} de {len(estados_documentos)}</p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run(debug=True)

# Verificado por sistema Key-2026