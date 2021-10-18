"""
Collect PV data from the SolarmanPV API and send Power+Energy data (W+kWh) to MQTT
"""

import argparse
import http.client
import json
import logging
import sys
import time

import mqtt

logging.basicConfig(level=logging.INFO)


def load_config(file):
    """
    Load configuration
    :return: Configuration object
    """
    try:
        with open(file, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
            return config
    except (FileNotFoundError, PermissionError) as error:
        logging.info("%s - Unable to open config file: %s", timestamp(), str(error))
        sys.exit(1)


def today():
    """
    :return: Returns the date in YYYY-MM-DD format
    """
    date = time.strftime("%Y-%m-%d")
    return date


def timestamp():
    """
    :return: Timestamp in YY-MM-DD hh:mm:ss
    """
    _t = time.strftime("%Y-%m-%d %H:%M:%S")
    return _t


def get_token(url, appid, secret, username, passhash):
    """
    Get a token from the API
    :return: access_token
    """
    try:
        conn = http.client.HTTPSConnection(url)
        payload = json.dumps({
            "appSecret": secret,
            "email": username,
            "password": passhash
        })
        headers = {
            'Content-Type': 'application/json'
        }
        url = f"//account/v1.0/token?appId={appid}&language=en"
        conn.request("POST", url, payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        logging.debug("Received token")
        return data["access_token"]
    except (KeyError, TypeError) as error:
        logging.error("%s - Unable to fetch token: %s", timestamp(), str(error))
        sys.exit(1)


def get_power_realtime(url, stationid, token):
    """
    Return current energy usage in W
    :return: watts
    """
    conn = http.client.HTTPSConnection(url)
    payload = json.dumps({
        "stationId": stationid
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': "bearer " + token
    }
    conn.request("POST", "//station/v1.0/realTime?language=en", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    watts = data["generationPower"]
    if isinstance(watts, float):
        return watts
    logging.error("%s - Unable to get watts", timestamp())
    sys.exit(1)


def get_energy_today(url, stationid, token):
    """
    Return today usage in kWh
    :return: kilowatts/hour
    """
    date = today()
    conn = http.client.HTTPSConnection(url)
    payload = json.dumps({
        "startTime": date,
        "timeType": 2,
        "stationId": stationid,
        "endTime": date
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': "bearer " + token
    }
    conn.request("POST", "//station/v1.0/history?language=en", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    kwh = data["stationDataItems"][0]["generationValue"]
    if isinstance(kwh, float):
        return kwh
    logging.error("%s - Unable to get kWh", timestamp())
    sys.exit(1)


def single_run(file):
    """
    Output current watts and kilowatts
    :param file: Config file
    """
    config = load_config(file)
    token = get_token(
                        config["url"],
                        config["appid"],
                        config["secret"],
                        config["username"],
                        config["passhash"]
                      )
    _w = get_power_realtime(config["url"], config["stationId"], token)
    _kw = get_energy_today(config["url"], config["stationId"], token)
    mqtt.message(config["mqtt"], "solar/power", _w)
    mqtt.message(config["mqtt"], "solar/energy", _kw)
    logging.info("%s - %s kWH day total and currently %s W", timestamp(), _kw, _w)


def daemon(file, interval):
    """
    Run as a daemon process
    :param file: Config file
    :param interval: Run interval in seconds
    """
    interval = int(interval)
    logging.info("Starting daemonized with a %s seconds run interval", str(interval))
    while True:
        try:
            single_run(file)
            time.sleep(interval)
        except ValueError as error:
            logging.error("%s - Configuration error: %s ", timestamp(), str(error))
            sys.exit(1)
        except KeyboardInterrupt:
            logging.error("%s - Caught interrupt", timestamp())
            sys.exit(1)
        # except Exception as error:  # pylint: disable=broad-except
        #     logging.error("%s - Error on start: %s", timestamp(), str(error))
        #     sys.exit(1)


def main():
    """
    Main
    :return:
    """
    parser = argparse.ArgumentParser(description="Collect data from Trannergy / Solarman API")
    parser.add_argument("-d", "--daemon",
                        action="store_true",
                        help="run as a service")
    parser.add_argument("-s", "--single",
                        action="store_true",
                        help="single run and exit")
    parser.add_argument("-i", "--interval",
                        default="300",
                        help="run interval in seconds (default 300 sec.)")
    parser.add_argument("-f", "--file",
                        default="config.json",
                        help="config file (default ./config.json)")
    parser.add_argument("-v", "--version",
                        action='version',
                        version='%(prog)s 0.0.1')
    args = parser.parse_args()
    if args.single:
        single_run(args.file)
    elif args.daemon:
        daemon(args.file, args.interval)
    else:
        parser.print_help(sys.stderr)


if __name__ == '__main__':
    main()
