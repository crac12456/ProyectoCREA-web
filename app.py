# Importa jsonify para poder enviar respuestas en formato JSON
from flask import Flask, render_template, send_from_directory, request, jsonify
import paho.mqtt.client as mqtt
import sqlite3 as sql
import os

# ---------------------------
# Creación de la base de datos (sin cambios)
# ---------------------------
conn = sql.connect("database.db", check_same_thread=False) # 'check_same_thread=False' es importante para Flask
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS mediciones(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dispositivo TEXT,
    temperatura REAL,
    ph INTEGER,
    turbidez REAL,
    latitud REAL,
    longitud REAL,
    altitud REAL,
    velocidad REAL
)
""")

conn.commit()
conn.close()

# ---------------------------
# Configuración de Flask
# ---------------------------
app = Flask(__name__)

# Rutas de las páginas (sin cambios)
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

# ----------------------------------------------------
# ¡NUEVA RUTA! - Para enviar datos a las gráficas
# ----------------------------------------------------
@app.route('/data')
def get_data():
    conn = sql.connect("database.db")
    conn.row_factory = sql.Row  # Permite acceder a los datos por nombre de columna
    cursor = conn.cursor()
    
    # Consulta para obtener el último registro insertado en la base de datos
    cursor.execute("SELECT temperatura, ph, turbidez FROM mediciones ORDER BY id DESC LIMIT 1")
    last_record = cursor.fetchone()
    
    conn.close()
    
    # Si hay datos, los enviamos como JSON. Si no, enviamos valores por defecto.
    if last_record:
        data = {
            "temperatura": last_record["temperatura"],
            "ph": last_record["ph"],
            "turbidez": last_record["turbidez"]
        }
    else:
        # Valores por defecto si la base de datos está vacía
        data = {
            "temperatura": 0,
            "ph": 0,
            "turbidez": 0
        }
        
    return jsonify(data) # Convierte el diccionario de Python a una respuesta JSON

# ---------------------------
# Servir archivos estáticos (sin cambios)
# ---------------------------
@app.route('/script.js')
def controles_js():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'controles.js')

# ---------------------------
# Recibir comandos WASD (sin cambios)
# ---------------------------
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

# ---------------------------
# Ejecutar servidor
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)