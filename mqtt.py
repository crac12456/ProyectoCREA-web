import paho.mqtt.client as mqtt_client
import json
import uuid
import sqlite3

#definicion de variables que requiere el protocolo mqtt
broker = 'broker.emqx.io'
port = 1883
topic = "backend/mqtt"
topic_sensores = "esp32/sensores"
client_id = f'python-mqtt-client-{uuid.getnode()}'

mqtt_client_instance = None

# funcion de coneccion, en esta se conecta al broker para enviar y recibir datos
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("conected to broker")
            client.subscribe(topic_sensores)
        else:
            print("conecction failed, return code: %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker, port)

    return client

def on_message(client, user_data, msg):
    print("mensaje recibido")
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
    except Exception as e:
        print("error al procesar el json")
        
def publish_message (topic, mensaje):
    global mqtt_client_instance

    if mqtt_client_instance is not None:
        try:
            result = mqtt_client_instance.publish

    mqtt_client.publish(topic, mensaje)
    print(f"enviado {topic}:{mensaje}")