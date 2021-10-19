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
    :return:
    """
    with open(file, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
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
        url = f"//account/v1.0/token?appId={appid}&language=en"
        conn.request("POST", url, payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        logging.debug("Received token")
        return data["access_token"]
    except Exception as error:  # pylint: disable=broad-except
        logging.error("Unable to fetch token: %s", str(error))
        sys.exit(1)

def get_station_realtime(url, stationid, token):
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
    return data

def get_device_currentData(url, deviceSn, token):
    conn = http.client.HTTPSConnection(url)
    payload = json.dumps({
        "deviceSn": deviceSn
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': "bearer " + token
    }
    conn.request("POST", "//device/v1.0/currentData?language=en", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    return data

def restruct_and_separate_currentData(data):
    dataList = data["dataList"]
    newdataList = {}
    for i in dataList:
        del i["key"]
        name = i["name"]
        name = name.replace(" ", "_")
        del i["name"]
        newdataList[name] = i["value"]
    del data["dataList"]
    return newdataList

def single_run(file):
    """
    Output current watts and kilowatts
    :return:
    """
    config = load_config(file)
    token = get_token(
                        config["url"],
                        config["appid"],
                        config["secret"],
                        config["username"],
                        config["passhash"]
                      )
    #_t = time.strftime("%Y-%m-%d %H:%M:%S")

    stationData = get_station_realtime(config["url"], config["stationId"], token)
    inverterData = get_device_currentData(config["url"], config["inverterId"] , token)
    loggerData = get_device_currentData(config["url"], config["loggerId"] , token)

    inverterDataList = restruct_and_separate_currentData(inverterData)
    loggerDataList = restruct_and_separate_currentData(loggerData)

    if config["debug"]:
        logging.info(json.dumps(stationData, indent=4, sort_keys=True))
        logging.info(json.dumps(inverterData, indent=4, sort_keys=True))
        logging.info(json.dumps(inverterDataList, indent=4, sort_keys=True))
        logging.info(json.dumps(loggerData, indent=4, sort_keys=True))
        logging.info(json.dumps(loggerDataList, indent=4, sort_keys=True))


    discard = ["code", "msg", "requestId", "success"]
    topic = config["mqtt"]["topic"]
    diff_timestamp = round((time.time()) - round(stationData["lastUpdateTime"]))

    if diff_timestamp < config["maxAge"]:
        logging.info("local and remote timestamp diff: %s seconds -> Publishing MQTT...",diff_timestamp)
        for p in stationData:
            if p not in discard:
                mqtt.message(config["mqtt"], topic+"/station/" + p, stationData[p])

        for p in inverterData:
            if p not in discard:
                mqtt.message(config["mqtt"], topic+"/inverter/" + p, inverterData[p])
        mqtt.message(config["mqtt"], topic+"/inverter/attributes", json.dumps(inverterDataList))

        for p in loggerData:
            if p not in discard:
                mqtt.message(config["mqtt"], topic+"/logger/" + p, loggerData[p])
        mqtt.message(config["mqtt"], topic+"/logger/attributes", json.dumps(loggerDataList))
    else:
        logging.info("local and remote timestamp diff: %s seconds -> NOT Publishing MQTT (Station probably offline due to nighttime shutdown)",diff_timestamp)


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
                        default="60",
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
