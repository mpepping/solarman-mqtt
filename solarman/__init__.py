"""
Collect PV data from the SolarmanPV API and send Power+Energy data to MQTT
"""

import argparse
import json
import logging
import sys
import time

from .api import SolarmanApi, ConstructData
from .helpers import ConfigCheck, HashPassword
from .mqtt import Mqtt

logging.basicConfig(level=logging.INFO)

VERSION = "1.0.0"


def load_config(file):
    """
    Load configuration
    :return:
    """
    with open(file, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
        return config


def validate_config(file):
    """
    Validate config file
    :param file: Config file
    :return:
    """
    config = load_config(file)
    ConfigCheck(config)


def create_passhash(password):
    """
    Create passhash from password
    :param password: Password
    :return:
    """
    pwstring = HashPassword(password)
    print(pwstring.hashed)


def single_run(file):
    """
    Output current watts and kilowatts
    :return:
    """
    config = load_config(file)
    pvdata = SolarmanApi(config)

    station_data = pvdata.station_realtime
    inverter_data = pvdata.device_current_data_inverter
    logger_data = pvdata.device_current_data_logger

    inverter_data_list = ConstructData(inverter_data).device_current_data
    logger_data_list = ConstructData(logger_data).device_current_data

    if config.get("debug", False):
        logging.info(json.dumps(station_data, indent=4, sort_keys=True))
        logging.info(json.dumps(inverter_data, indent=4, sort_keys=True))
        logging.info(json.dumps(inverter_data_list, indent=4, sort_keys=True))
        logging.info(json.dumps(logger_data, indent=4, sort_keys=True))
        logging.info(json.dumps(logger_data_list, indent=4, sort_keys=True))

    discard = ["code", "msg", "requestId", "success"]
    topic = config["mqtt"]["topic"]

    _t = time.strftime("%Y-%m-%d %H:%M:%S")
    inverter_device_state = inverter_data["deviceState"]
    mqtt_connection = Mqtt(config["mqtt"])

    if inverter_device_state == 1:
        logging.info(
            "%s - Inverter DeviceState: %s -> Publishing to MQTT ...",
            _t,
            inverter_device_state,
        )
        for i in station_data:
            if station_data[i] and i not in discard:
                mqtt_connection.message(topic + "/station/" + i, station_data[i])

        for i in inverter_data:
            if inverter_data[i] and i not in discard:
                mqtt_connection.message(topic + "/inverter/" + i, inverter_data[i])
        if inverter_data_list:
            mqtt_connection.message(
                topic + "/inverter/attributes",
                json.dumps(inverter_data_list),
            )

        for i in logger_data:
            if logger_data[i] and i not in discard:
                mqtt_connection.message(topic + "/logger/" + i, logger_data[i])
        if logger_data_list:
            mqtt_connection.message(
                topic + "/logger/attributes",
                json.dumps(logger_data_list),
            )
    else:
        mqtt_connection.message(
            topic + "/inverter/deviceState",
            inverter_data["deviceState"],
        )
        mqtt_connection.message(
            topic + "/logger/deviceState", logger_data["deviceState"]
        )
        logging.info(
            "%s - Inverter DeviceState: %s"
            "-> Only status MQTT publish (probably offline due to nighttime shutdown)",
            _t,
            inverter_device_state,
        )


def daemon(file, interval):
    """
    Run as a daemon process
    :param file: Config file
    :param interval: Run interval in seconds
    :return:
    """
    interval = int(interval)
    logging.info("Starting daemonized with a %s seconds run interval", str(interval))
    while True:
        try:
            single_run(file)
            time.sleep(interval)
        except Exception as error:  # pylint: disable=broad-except
            logging.error("Error on start: %s", str(error))
            sys.exit(1)
        except KeyboardInterrupt:
            logging.info("Exiting on keyboard interrupt")
            sys.exit(0)


def main():
    """
    Main
    :return:
    """
    parser = argparse.ArgumentParser(
        description="Collect data from Trannergy / Solarman API"
    )
    parser.add_argument("-d", "--daemon", action="store_true", help="run as a service")
    parser.add_argument(
        "-s", "--single", action="store_true", help="single run and exit"
    )
    parser.add_argument(
        "-i",
        "--interval",
        default="300",
        help="run interval in seconds (default 300 sec.)",
    )
    parser.add_argument(
        "-f",
        "--file",
        default="config.json",
        help="config file (default ./config.json)",
    )
    parser.add_argument(
        "--validate", action="store_true", help="validate config file and exit"
    )
    parser.add_argument(
        "--create-passhash",
        default="",
        help="create passhash from provided password string and exit",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="solarman-mqtt (%(prog)s) " + VERSION,
    )

    args = parser.parse_args()
    if args.single:
        single_run(args.file)
    elif args.daemon:
        daemon(args.file, args.interval)
    elif args.validate:
        validate_config(args.file)
    elif args.create_passhash:
        create_passhash(args.create_passhash)
    else:
        parser.print_help(sys.stderr)


if __name__ == "__main__":
    main()
