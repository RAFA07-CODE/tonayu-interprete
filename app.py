from flask import Flask, request, jsonify
from interpreter import ejecutar_codigo  # Tu función personalizada de Tonayu

app = Flask(__name__)

@app.route("/ejecutar", methods=["POST"])
def ejecutar():
    datos = request.json
    codigo = datos.get("codigo", "")
    resultado = ejecutar_codigo(codigo)
    return jsonify({"resultado": resultado})

if __name__ == "__main__":
    app.run()
