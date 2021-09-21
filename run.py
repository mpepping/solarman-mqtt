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

logging.basicConfig(level=logging.DEBUG)


def load_config(file):
    """
    Load configuration
    :return:
    """
    try:
        f = open(file)
    except:
        logging.error("Could not open {}".format(file))
        sys.exit(1)
    config = json.load(f)
    return config


def today():
    """
    Return date in YYYY-MM-DD
    :return:
    """
    date = time.strftime("%Y-%m-%d")
    return date


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
        url = "//account/v1.0/token?appId={}&language=en".format(appid)
        conn.request("POST", url, payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        logging.info("Received token")
        return data["access_token"]
    except:
        logging.error("Unable to fetch token")
        sys.exit(1)


def get_power_realtime(url, stationid, token):
    """
    Return current energy usage in W
    :return:
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
    else:
        logging.error("Unable to get watts")
        sys.exit(1)


def get_energy_today(url, stationid, token):
    """
    Return today usage in kW
    :return:
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
    else:
        logging.error("Unable to get kWh")
        exit(1)


def single_run(file):
    """
    Output current watts and kilowatts
    :return:
    """
    config = load_config(file)
    token = get_token(config["url"], config["appid"], config["secret"], config["username"], config["passhash"])
    t = time.strftime("%Y-%m-%d %H:%M:%S")
    w = get_power_realtime(config["url"], config["stationId"], token)
    kw = get_energy_today(config["url"], config["stationId"], token)
    mqtt.main(config["mqtt"], "solar/power", w)
    mqtt.main(config["mqtt"], "solar/energy", kw)
    logging.info("{} - {}kWH day total and currently {}W".format(t, kw, w))


def daemon(file, interval):
    interval = int(interval)
    logging.info("Starting daemonized with a {} seconds run interval".format(str(interval)))
    while True:
        try:
            single_run(file)
            time.sleep(interval)
        except:
            logging.error("Catched break .. exiting")
            sys.exit(1)


def main():
    """
    Main
    :return:
    """
    parser = argparse.ArgumentParser(description="Collect data from Trannergy / Solarman API")
    parser.add_argument("-d", "--daemon", action="store_true", help="run as a service")
    parser.add_argument("-s", "--single", action="store_true", help="single run and exit")
    parser.add_argument("-i", "--interval", default="300", help="run interval in seconds (default 300 sec.)")
    parser.add_argument("-f", "--file", default="config.json", help="config file (default ./config.json)")
    parser.add_argument("-v", "--version", action='version', version='%(prog)s 0.0.1')
    args = parser.parse_args()
    if args.single:
        single_run(args.file)
    elif args.daemon:
        daemon(args.file, args.interval)
    else:
        parser.print_help(sys.stderr)


if __name__ == '__main__':
    main()
