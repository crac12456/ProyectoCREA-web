import paho.mqtt.client as mqtt_client
import json
import uuid
import sqlite3
import threading

# ---------------------------
# Definición de variables
# ---------------------------
broker = '192.168.0.113'
port = 1883
topic_pub = "esp32/robot/control"
topic_sub = "esp32/robot/sensores"
client_id = f'python-mqtt-client-{uuid.getnode()}'

username = None
password = None

# Cliente MQTT global para ser accesible en todas las funciones
mqtt_client_instance = None
# Bloqueo de hilos para garantizar que solo un hilo a la vez acceda a la base de datos
db_lock = threading.Lock()

# ---------------------------
# Funciones de la base de datos
# ---------------------------
def init_database():
    """Crea la tabla si no existe, de forma segura."""
    with db_lock:
        conn = None
        try:
            conn = sqlite3.connect("database.db")
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
        except sqlite3.Error as e:
            print(f"Error al inicializar la base de datos: {e}")
        finally:
            if conn:
                conn.close()

def save_data_to_db(data):
    """Guarda los datos en la base de datos de forma segura."""
    with db_lock:
        conn = None
        try:
            conn = sqlite3.connect("database.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO mediciones(dispositivo, temperatura, ph, turbidez, latitud, longitud, altitud, velocidad)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["dispositivo"],
                data["temperatura"],
                data["ph"],
                data["turbidez"],
                data["latitud"],
                data["longitud"],
                data["altitud"],
                data["velocidad"],
            ))
            conn.commit()
            print("Datos guardados en la base de datos")
        except sqlite3.Error as e:
            print(f"Error en la base de datos al guardar datos: {e}")
        finally:
            if conn:
                conn.close()

# ---------------------------
# Funciones del cliente MQTT
# ---------------------------
def on_connect(client, userdata, flags, rc):
    """Función que se llama cuando el cliente se conecta."""
    if rc == 0:
        print("Conectado al broker MQTT")
        client.subscribe(topic_sub)
    else:
        print(f"Error de conexión, código de retorno: {rc}")

def on_message(client, user_data, msg):
    """Función que se llama cuando se recibe un mensaje MQTT."""
    print("Mensaje recibido")
    try:
        data = json.loads(msg.payload.decode())
        
        required_fields = ["dispositivo", "temperatura", "ph", "turbidez", 
                         "latitud", "longitud", "altitud", "velocidad"]
        
        if not all(field in data for field in required_fields):
            print("Datos faltantes en el JSON recibido")
            return
        
        # Llama a la función segura para guardar los datos
        save_data_to_db(data)

    except json.JSONDecodeError:
        print("Error al decodificar el JSON")
    except Exception as e:
        print(f"Error inesperado al recibir el mensaje: {e}")

def connect_mqtt() -> mqtt_client:
    """Intenta conectar el cliente MQTT al broker."""
    global mqtt_client_instance
    try:
        client = mqtt_client.Client(client_id, protocol=mqtt_client.MQTTv311)
        client.on_connect = on_connect
        client.on_message = on_message
        
        if username and password:
            client.username_pw_set(username, password)
            
        client.connect(broker, port)
        mqtt_client_instance = client
        return client
    except Exception as e:
        print(f"Error al conectar con el broker: {e}")
        return None

def publish_message(topic, message):
    """Publica un mensaje en el broker MQTT."""
    if mqtt_client_instance is not None and mqtt_client_instance.is_connected():
        try:
            result = mqtt_client_instance.publish(topic, message)
            status = result[0]
            if status == 0:
                print(f"Mensaje enviado a {topic}: {message}")
                return True
            else:
                print(f"Error al enviar el mensaje, código: {status}")
                return False
        except Exception as e:
            print(f"Error al publicar mensaje: {e}")
            return False
    else:
        print("No se ha conectado con el broker")
        return False
