# Importa jsonify para poder enviar respuestas en formato JSON
from flask import Flask, render_template, send_from_directory, request, jsonify
from mqtt import publish_message, topic_pub, connect_mqtt
from datetime import datetime
import paho.mqtt.client as mqtt
import sqlite3 as sql
import os
import threading

# ---------------------------
# Configuración de Flask
# ---------------------------
app = Flask(__name__)

ultimo_dispositivo = None # Nombre del dispositivo 

# Datos de los sensores 
ultimo_temperatura = None
ultimo_ph = None
ultimo_turbidez = None

# datos del GPS
ultimo_latitud = None
ultimo_longitud = None
ultimo_altitud = None
ultimo_velocidad = None

ultimo_frame = None
frame_lock = threading.Lock()
ultimo_frame_time = None

# La base de datos debe ser gestionada por cada hilo o proceso de forma independiente
db_lock = threading.Lock()
def get_db():
    conn = sql.connect("datos_esp32.db", check_same_thread=False)
    conn.row_factory = sql.Row
    return conn

# Iniciamos la base de datos, verifica que este creada y si no lo esta, la crea
def init_database():
    with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS lecturas(
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

@app.route('/admin')
def admin():
    return render_template('admin.html')

"""
API de datos
este apartado se encarga de recibir los datos del ESP32
Esto es una REST API, la cual funciona a travez de datos en formato JSON
"""

@app.route('/api/datos', methods=['POST'])
def api_datos():
    data = request.get_json() # convierte los datos del json a una variable

    #convetimos las variables en globales para poder utilizarlas en diferentes puntos
    global ultimo_dispositivo, ultimo_temperatura, ultimo_ph, ultimo_turbidez
    global ultimo_latitud, ultimo_longitud, ultimo_altitud, ultimo_velocidad

    # Nombre del dispositivo 
    ultimo_dispositivo = data.get("dispositivo") 

    # Datos de los sensores 
    ultimo_temperatura =data.get("temperatura")
    ultimo_ph = data.get("ph")
    ultimo_turbidez = data.get("turbidez")

    # datos del GPS
    ultimo_latitud = data.get("latitud")
    ultimo_longitud = data.get("longitud")
    ultimo_altitud = data.get("altitud")
    ultimo_velocidad = data.get("velocidad")

    #enviamos los datos que recibimos del esp32 a la base de datos sqlite
    conn = sql.connect("datos_esp32.db")
    c = conn.cursor()
    c.execute('''INSERT INTO lecturas
              (dispositivo, temperatura, ph, turbidez, latitud, longitud, altitud, velocidad, timestamp)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) ''', 
              (ultimo_dispositivo, ultimo_temperatura, ultimo_ph, ultimo_turbidez,
               ultimo_longitud, ultimo_latitud, ultimo_altitud, ultimo_velocidad, datetime.now().isoformat())) 
    conn.commit()
    conn.close()

    print(f"Los datos se han recibido, temperatura: {ultimo_temperatura}, ph: {ultimo_ph}, turbidez: {ultimo_turbidez}")
    return jsonify({"ok": True}), 201

@app.route('/api/datos', methods = ['GET'])
def obtener_datos():
    with db_lock:
        with get_db() as conn: 
            c = conn.cursor()
            c.execute('SELECT * FROM lecturas ORDER BY id DESC LIMIT 100')
            rows = c.fetchall()    

    lecturas = []
    for row in rows:
        lecturas.append({
            'id': row[0],
            'dispositivo': row[1],
            'temperatura': row[2],
            'ph': row[3],
            'turbidez': row[4],
            'latitud': row[5],
            'longitud': row[6], 
            'altitud': row[7],
            'velocidad': row[8],
            'timestamp': row[9]
        })

    return jsonify(lecturas)

@app.route('/api/ultimo', methods = ['GET'])
def obtener_ultimo():
    return jsonify({
        'dispositivo': ultimo_dispositivo, 
        'temperatura': ultimo_temperatura, 
        'ph': ultimo_ph, 
        'turbidez': ultimo_turbidez, 
        'latitud': ultimo_latitud, 
        'longitud': ultimo_longitud, 
        'altitud': ultimo_altitud, 
        'velocidad': ultimo_velocidad, 
    })

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

@app.route('/api/camara', methods=['POST'])
def get_frame():
    global ultimo_frame, ultimo_frame_time

    try:
        image_data = request.data

        if not image_data:
            return {'error':'No recibio imagen'}
        
        with frame_lock:
            ultimo_frame = image_data  
            ultimo_frame_time = datetime.now()

        print(f"Frame recibido {len(image_data)} bytes - {ultimo_frame_time.strftime('%H:%M:%S')}")

        return {
            'status' : 'correcto',
            'mensaje' : 'Frame recibido correctamente',
            'tamaño' : len(image_data),
            'timestamp' : ultimo_frame_time.isoformat()
        }, 200
    
    except Exception as e:
        print(f"Error al recibir el frame: {e}")
        return {'error': str (e)}, 500
    
@app.route('/api/ultimo_frame', methods=['GET'])
def get_ultimo_frame():
    from flask import Response

    with frame_lock:
        if ultimo_frame is not None:
            return Response(ultimo_frame, mimetype='image/jpeg')
        else:
            return {'error': 'no hay frames que mostrar'}, 404
        
@app.route('/api/video_feed', methods=['GET'])
def video_feed():
    from flask import Response

    import time 

    def generate():
        while True:
            with frame_lock:
                if ultimo_frame is not None:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + ultimo_frame + b'\r\n')
                else: 
                    time.sleep(0.1)

    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9000, debug=True)
