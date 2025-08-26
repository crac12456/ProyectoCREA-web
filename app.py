from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
import os
import threading
import paho.mqtt.client as mqtt

# ---------------------------
# Configuración de Flask
# ---------------------------
app = Flask(__name__)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    # Intenta conectar. Si la base de datos no existe, la crea.
    conn = sql.connect("database.db", check_same_thread=False)
    conn.row_factory = sql.Row
    return conn

# Función para crear la tabla de mediciones (si no existe)
def create_table_if_not_exists():
    conn = get_db_connection()
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
# Lógica de MQTT en un hilo separado
# ---------------------------
def on_connect(client, userdata, flags, rc):
    print("Conectado con código de resultado: " + str(rc))
    client.subscribe("temperatura")
    client.subscribe("ph")
    client.subscribe("turbidez")
    client.subscribe("GPS")
    client.subscribe("velocidad")

def on_message(client, userdata, msg):
    # Aquí puedes agregar la lógica para guardar los datos en la base de datos
    # A modo de ejemplo, solo se imprime el mensaje
    print(f"Mensaje recibido: {msg.payload.decode()}")

def mqtt_worker():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Asegúrate de usar las credenciales y el broker correctos
    client.connect("broker.hivemq.com", 1883, 60)
    client.loop_forever()

# ---------------------------
# Rutas de las páginas
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

@app.route('/data')
def get_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT temperatura, ph, turbidez FROM mediciones ORDER BY id DESC LIMIT 1")
    last_record = cursor.fetchone()
    conn.close()
    
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
    # Aquí tu lógica para enviar el mensaje MQTT
    print(f"Comando {key} recibido")
    return f"Comando {key} recibido"

# ---------------------------
# Iniciar servidor
# ---------------------------
if __name__ == "__main__":
    create_table_if_not_exists()
    mqtt_thread = threading.Thread(target=mqtt_worker)
    mqtt_thread.daemon = True
    mqtt_thread.start()
    app.run(debug=True)