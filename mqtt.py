from paho import client as mqtt_client
import json
import uuid

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

def suscribe(client: mqtt_client):
    def on_messaje(client, userdata, msg):
        pass