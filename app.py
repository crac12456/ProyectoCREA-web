
from flask import Flask, render_template, send_from_directory
from paho import client 
import sqlite3 as sql
import os

#creacion de la base de datos 

conn = sql.connect("database.bd")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXIST mediciones(
    id INTEGRER PRIMARY KEY AUTOINCREMENT,
    dispositivo TEXT,
    temperatura REAL,
    ph INTEGRER,
    turbidez REAL,
    latitud REAL,
    longitud REAL,
    altitud REAL,
    velocidad REAL,
    )
""")
conn.commit()
conn.close



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
@app.route('/script.js')
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
