from paho import client as mqtt_client
import json
import uuid
import sqlite3

#definicion de variables que requiere el protocolo mqtt
broker = 'broker.emqx.io'
port = 1883
topic = "backend/mqtt"
client_id = f'python-mqtt-client-{uuid.getnode()}'

# funcion de coneccion, en esta se conecta al broker para enviar y recibir datos
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("conected to broker")
        else:
            print("conecction failed, return code: %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connet() = on_connect
    client.connetc(broker, port)

    return client

def on_message(client, user_data, msg):
    print("mensaje recibido")
    try: 
        data = json.loads(msg.payload.decode())

        conn = sqlite3.connect("database.bd")
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
    except Exception as e:
        print("error al procesar el json")
