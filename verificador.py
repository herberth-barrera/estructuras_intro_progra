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

    contador = 0
    filas_html = ""
    for i in range(len(estados_documentos)):
        if estados_documentos[i]:
            contador += 1
            icono = "check"
        else:
            icono = "pendiente"
        filas_html += f"<li>[{icono}] {nombres_documentos[i]}</li>"

    return f"""
    <h2>Expediente de doctor Herberth</h2>
    <ul>{filas_html}</ul>
    <p>Documentos completos: {contador} de {len(estados_documentos)}</p>
    """

if __name__ == "__main__":
    app.run(debug=True)