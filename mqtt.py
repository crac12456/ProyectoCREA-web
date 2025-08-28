import paho.mqtt.client as mqtt_client
import json
import uuid
import sqlite3

#Definición de variables que requiere el protocolo mqtt
broker = 'broker.emqx.io'
port = 1883
topic_pub = "esp32/robot/control"
topic_sub = "esp32/robot/sensores"
client_id = f'python-mqtt-client-{uuid.getnode()}'

username = None
password = None

# Iniciar el cliente 
mqtt_client_instance = None

# Función de coneccion, en esta se conecta al broker para enviar y recibir datos
def connect_mqtt() -> mqtt_client:
    global mqtt_client_instance

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conected to broker")
            client.subscribe(topic_sub)
        else:
            print("Conecction failed, return code: %d\n", rc)

    
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)

    if username and password: 
        client.username_pw_set(username, password)
        
    try:    
        client.connect(broker, port)
        mqtt_client_instance = client
        return client
    except Exception as e:
        print(f"Error al conectar con el broker {e}")
        return None

def on_message(client, user_data, msg):
    print("Mensaje recibido")

    try:
        required_fields = ["dispositivo", "temperatura", "ph", "turbidez", 
                        "latitud", "longitud", "altitud", "velocidad"]
        
        if not all(field in data for field in required_fields):
            print("datos faltantes en el json recibido")
            return
    
        data = json.loads(msg.payload.decode())

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
        conn.close()

        print("Datos guardados en la bse de datos")

    except json.JSONDecodeError:
        print("Error al decodificar el json")
    except sqlite3.Error:
        print("Error en la base de datos")
    except Exception as e:
        print(f"Error inesperado al recibir el mensaje {e}")
    

def publish_message (topic_pub, mensaje):
    global mqtt_client_instance

    if mqtt_client_instance is not None:
        try:
            result = mqtt_client_instance.publish(topic_pub, mensaje)
            status = result[0]
            if status == 0:
                print(f"Mensaje enviado {topic_pub}: {mensaje}")
                return True
            else:
                print(f"Error al mandar en mensaje{status}")
                return False
        except Exception as e:
            print("Error al conectarse")
            return False
    else:
        print("No se a conectado con el broker")
        return False
    