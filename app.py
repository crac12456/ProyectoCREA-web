from flask import Flask, render_template, send_from_directory
import os

app = Flask(__name__)

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/GPS')
def gps():
    return render_template('GPS.html')

@app.route('/datos')
def datos():
    return render_template('datos.html')

@app.route('/control')
def control():
    return render_template('control.html')

# Ruta para servir el archivo JS
@app.route('/controles.js')
def controles_js():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'controles.js')

# Ruta para recibir comandos WASD
@app.route('/control/<key>', methods=['POST'])
def control_key(key):
    if key == "w":
        print("Mover hacia adelante")
    elif key == "a":
        print("Mover a la izquierda")
    elif key == "s":
        print("Mover hacia atrás")
    elif key == "d":
        print("Mover a la derecha")
    else:
        print(f"Tecla desconocida: {key}")
    return f"Comando {key} recibido"

if __name__ == "__main__":
    app.run(debug=True)
