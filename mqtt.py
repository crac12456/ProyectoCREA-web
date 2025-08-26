import paho.mqtt.client as mqtt_client
import json
import uuid
import sqlite3

#definicion de variables que requiere el protocolo mqtt
broker = 'broker.emqx.io'
port = 1883
topic_pub = "esp32/robot/control"
topic_sub = "esp32/robot/sensores"
client_id = f'python-mqtt-client-{uuid.getnode()}'

# Iniciar el cliente 
mqtt_client_instance = None

# funcion de coneccion, en esta se conecta al broker para enviar y recibir datos
def connect_mqtt() -> mqtt_client:
    global mqtt_client_instance

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("conected to broker")
            client.subscribe(topic_sub)
        else:
            print("conecction failed, return code: %d\n", rc)

    
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)

    return client

def on_message(client, user_data, msg):
    print("mensaje recibido")

    data = json.loads(msg.payload.decode())

    required_fields = ["dispositivo", "temperatura", "ph", "turbidez", 
                       "latitud", "longitud", "altitud", "velocidad"]
    
    try: 
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

        print("datos guardados en la bse de datos")

    except json.JSONDecodeError:
        print("error al decodificar el json")
    except sqlite3.Error:
        print("error en la base de datos")
    except Exception as e:
        print(f"error inesperado al recibir el mensaje {e}")
    

def publish_message (topic_pub, mensaje):
    global mqtt_client_instance

    if mqtt_client_instance is not None:
        try:
            result = mqtt_client_instance.publish(topic_pub, mensaje)
            status = result[0]
            if status == 0:
                print(f"mensaje enviado {topic_pub}: {mensaje}")
            else:
                print(f"error al mandar en mensaje{status}")
        except Exception as e:
            print("error al conectarse")
    else:
        print("no se a conectado con el broker")
            

    print(f"enviado {topic_pub}:{mensaje}")