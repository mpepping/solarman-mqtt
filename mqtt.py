import logging
import random
from paho.mqtt import client as mqtt_client

logging.basicConfig(level=logging.DEBUG)


def connect_mqtt(broker, port, username, password):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client_id = f'solarmanpv-mqtt-{random.randint(0, 1000)}'
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, topic, msg):
    msg = msg
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        logging.info(f"Send `{msg}` to topic `{topic}`")
    else:
        logging.error(f"Failed to send message to topic {topic}")


def main(config, topic, msg):
    config = config
    a = connect_mqtt(config["broker"], config["port"], config["username"], config["password"])
    publish(a, topic, msg)


# if __name__ == '__main__':
#     main(topic_energy, 1.1)
