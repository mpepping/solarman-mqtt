"""
MQTT connect and publish
"""

import logging
import random
from paho.mqtt import client as mqtt_client

logging.basicConfig(level=logging.INFO)


def connect_mqtt(broker, port, username, password):
    """
    Create an MQTT connection
    :param broker: MQTT broker
    :param port: MQTT broker port
    :param username: MQTT username
    :param password: MQTT password
    :return:
    """
    client_id = f'solarmanpv-mqtt-{random.randint(0, 1000)}'
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.connect(broker, port)
    return client


def publish(client, topic, msg):
    """
    Publish a message on a MQTT topic
    :param client: Connect parameters
    :param topic: MQTT topic
    :param msg: Message payload
    :return:
    """
    result = client.publish(topic, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        logging.debug("Send %s to %s", msg, topic)
    else:
        logging.error("Failed to send message to topic %s", topic)


def message(config, topic, msg):
    """
    MQTT Connect and send
    :param config: Broker configuration
    :param topic: MQTT topic
    :param msg: Message payload
    """
    client = connect_mqtt(config["broker"], config["port"], config["username"], config["password"])
    publish(client, topic, msg)
