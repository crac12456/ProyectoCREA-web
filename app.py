# Importa jsonify para poder enviar respuestas en formato JSON
from flask import Flask, render_template, send_from_directory, request, jsonify
from mqtt import publish_message, topic_pub, connect_mqtt
import paho.mqtt.client as mqtt
import sqlite3 as sql
import os
import threading

# ---------------------------
# Configuración de Flask
# ---------------------------
app = Flask(__name__)

# La base de datos debe ser gestionada por cada hilo o proceso de forma independiente
db_lock = threading.Lock()
def get_db():
    conn = sql.connect("database.db", check_same_thread=False)
    conn.row_factory = sql.Row
    return conn

def init_database():
    with db_lock:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS mediciones(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dispositivo TEXT,
                temperatura REAL,
                ph REAL,
                turbidez REAL,
                latitud REAL,
                longitud REAL,
                altitud REAL,
                velocidad REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            conn.commit()

init_database()

# ---------------------------
# Configuración de MQTT
# ---------------------------
# El cliente MQTT debe ser global para ser accesible
client = connect_mqtt()
if client:
    # Iniciar el bucle en un hilo separado para que no bloquee Flask
    client.loop_start()
else:
    print("Error al conectarse con el broker MQTT. Las funcionalidades de control no estarán disponibles.")

# ---------------------------
# Rutas de la aplicación
# ---------------------------
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

# Endpoint para recibir datos JSON a través de una API POST
@app.route('/api/data', methods=['POST'])
def receive_data():
    """Recibe los datos en formato JSON de una solicitud POST y los guarda en la BD."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No se recibió un JSON válido"}), 400

        # Validar que el JSON contenga los campos esperados
        required_fields = ["dispositivo", "temperatura", "ph", "turbidez",
                          "latitud", "longitud", "altitud", "velocidad"]
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Faltan campos en el JSON"}), 400
        
        # Guardar los datos en la base de datos
        with db_lock:
            with get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mediciones (dispositivo, temperatura, ph, turbidez, latitud, longitud, altitud, velocidad)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (data["dispositivo"], data["temperatura"], data["ph"], data["turbidez"], 
                      data["latitud"], data["longitud"], data["altitud"], data["velocidad"]))
                conn.commit()
        
        # Retorna una respuesta exitosa al cliente
        return jsonify({"message": "Datos recibidos y guardados correctamente"}), 200
        
    except Exception as e:
        print(f"Error al procesar la solicitud API: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/data')
def get_data():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT temperatura, ph, turbidez, timestamp
                FROM mediciones
                ORDER BY id DESC LIMIT 1
            """)
            last_record = cursor.fetchone()

            if last_record:
                data = {
                    "temperatura": last_record["temperatura"],
                    "ph": last_record["ph"],
                    "turbidez": last_record["turbidez"]
                }
            else:
                data = {
                    "temperatura": 0,
                    "ph": 0,
                    "turbidez": 0
                }
        return jsonify(data)
    except Exception as e:
        print(f"Error al obtener los datos: {e}")
        return jsonify({"error": "Error al obtener los datos"}), 500

@app.route('/control/<key>', methods=['POST'])
def control_key(key):
    commands = {
        "w": "adelante",
        "s": "atras",
        "a": "izquierda",
        "d": "derecha",
        "stop": "stop"
    }

    command = commands.get(key.lower())

    if client and client.is_connected():
        if command:
            success = publish_message(topic_pub, command)
            print(f"Comando enviado: {command}")
            return jsonify({
                "status": "success" if success else "error",
                "command": command,
                "key": key
            })
        else:
            publish_message(topic_pub, "stop")
            print(f"Tecla desconocida: {key}, deteniendo")
            return jsonify({"status": "unknown key", "key": key}), 400
    else:
        return jsonify({
            "status": "error",
            "message": "Cliente MQTT no conectado"
        }), 503

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

# Esta parte ya no se ejecuta con Waitress, pero es segura para desarrollo local
# if __name__ == "__main__":
#     app.run(debug=True)