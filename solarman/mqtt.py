"""
MQTT connect and publish
"""

import logging
import random
from paho.mqtt import client as mqtt_client

logging.basicConfig(level=logging.INFO)

class Mqtt:
    """
    MQTT connect and publish
    """

    def __init__(self, config, topic, msg):
        """
        MQTT Connect and send
        """
        self.broker = config["broker"]
        self.port = config["port"]
        self.username = config["username"]
        self.password = config["password"]
        self.topic = topic
        self.msg = msg
        Mqtt.message(self)

    def connect(self):
        """
        Create an MQTT connection
        :return:
        """
        client_id = f'solarmanpv-mqtt-{random.randint(0, 1000)}'
        client = mqtt_client.Client(client_id)
        client.username_pw_set(self.username, self.password)
        client.connect(self.broker, self.port)
        return client

    def publish(self, client):
        """
        Publish a message on a MQTT topic
        :param client: Connect parameters
        :param topic: MQTT topic
        :param msg: Message payload
        :return:
        """
        result = client.publish(self.topic, self.msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            logging.debug("Send %s to %s", self.msg, self.topic)
        else:
            logging.error("Failed to send message to topic %s", self.topic)

    def message(self):
        """
        MQTT Connect and send
        """
        client = Mqtt.connect(self)
        Mqtt.publish(self, client)
