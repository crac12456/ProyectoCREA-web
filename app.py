# Importa jsonify para poder enviar respuestas en formato JSON
from flask import Flask, render_template, send_from_directory, request, jsonify
from mqtt import publish_message, topic_pub, connect_mqtt
import paho.mqtt.client as mqtt
import sqlite3 as sql
import os
import threading

client = connect_mqtt()
if client:
    client.loop_start()
else: 
    print("error al conectarse con el broker")
    

# ---------------------------
# Creación de la base de datos
# ---------------------------

db_lock = threading.Lock()

def init_database():
    with db_lock:
        conn = sql.connect("database.db", check_same_thread=False) 
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

init_database()

# ---------------------------
# Configuración de Flask
# ---------------------------
app = Flask(__name__)

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
# enviar datos a las gráficas
# ----------------------------------------------------
@app.route('/data')
def get_data():
    try:
        with db_lock:
            conn = sql.connect("database.db")
            conn.row_factory = sql.Row  # Permite acceder a los datos por nombre de columna
            cursor = conn.cursor()
            
            # Consulta para obtener el último registro insertado en la base de datos
            cursor.execute("""
                SELECT temperatura, ph, turbidez, timestamp 
                FROM mediciones 
                ORDER BY id DESC LIMIT 1
            """)
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
                    "turbidez": 0,
                    "timestamp": None
                }
        
        return jsonify(data) # Convierte el diccionario de Python a una respuesta JSON
    except Exception as e:
        print(f"error fatal al conseguir los datos {e}")
        return jsonify({"error":"Error al obtener los datos"})

# ---------------------------
# Servir archivos estáticos 
# ---------------------------
@app.route('/script.js')
def controles_js():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'controles.js')

# ---------------------------
# Recibir comandos WASD 
# ---------------------------
@app.route('/control/<key>', methods=['POST'])
def control_key(key):
    commands = {
        "w":"adelante",
        "s":"atras",
        "a":"izquierda",
        "d":"derecha",
        "stop":"stop"
    }

    command = commands.get(key.lower())

    if command:
        success = publish_message(topic_pub, command)
        print(f"comando enviado: {command}")

        return jsonify({
            "status":"success" if success else "error",
            "command": command,
            "key": key
        })
    else:
        publish_message(topic_pub, "stop")
        print(f"tecla desconocida: {key}, deteniendo")
        return jsonify({"status":"unknown key", "key": key}), 400
    

@app.route('/status')
def system_status():
    return jsonify({
        "mqtt_connected": client is not None and client.is_connected() if client else False,
        "broker": "localhost",
        "port": 1883,
        "topics": {
            "publish": topic_pub,
            "subscribe": "esp32/robot/sensores"
        }
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500
    
# ---------------------------
# Ejecutar servidor
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)