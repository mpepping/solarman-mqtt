"""
Api
"""

import http.client
import json
import logging
import sys


class SolarmanApi:
    """
    Connect to the Solarman API and return PV data
    """

    def __init__(self, config):
        self.config = config
        self.station_id = config["stationId"]
        self.url = config["url"]
        self.token = self.get_token(
            self.config["appid"],
            self.config["secret"],
            self.config["username"],
            self.config["passhash"],
        )
        self.station_realtime = self.get_station_realtime()
        self.device_current_data_inverter = self.get_device_current_data(
            self.config["inverterId"]
        )
        self.device_current_data_logger = self.get_device_current_data(
            self.config["loggerId"]
        )

    def get_token(self, appid, secret, username, passhash):
        """
        Get a token from the API
        :return: access_token
        """
        try:
            conn = http.client.HTTPSConnection(self.url)
            payload = json.dumps(
                {"appSecret": secret, "email": username, "password": passhash}
            )
            headers = {"Content-Type": "application/json"}
            url = f"//account/v1.0/token?appId={appid}&language=en"
            conn.request("POST", url, payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read())
            logging.debug("Received token")
            return data["access_token"]
        except Exception as error:  # pylint: disable=broad-except
            logging.error("Unable to fetch token: %s", str(error))
            sys.exit(1)

    def get_station_realtime(self):
        """
        Return station realtime data
        :return: realtime data
        """
        conn = http.client.HTTPSConnection(self.url)
        payload = json.dumps({"stationId": self.station_id})
        headers = {
            "Content-Type": "application/json",
            "Authorization": "bearer " + self.token,
        }
        conn.request("POST", "//station/v1.0/realTime?language=en", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        return data

    def get_device_current_data(self, device_sn):
        """
        Return device current data
        :return: current data
        """
        conn = http.client.HTTPSConnection(self.url)
        payload = json.dumps({"deviceSn": device_sn})
        headers = {
            "Content-Type": "application/json",
            "Authorization": "bearer " + self.token,
        }
        conn.request("POST", "//device/v1.0/currentData?language=en", payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        return data


class ConstructData:  # pylint: disable=too-few-public-methods
    """
    Return restructured and separated device current data
    Original data is removed
    :return: new current data
    """

    def __init__(self, data):
        self.data = data
        self.device_current_data = self.construct_data()

    def construct_data(self):
        """
        Return restructured and separated device current data
        """
        new_data_list = {}
        try:
            for i in self.data["dataList"]:
                del i["key"]
                name = i["name"]
                name = name.replace(" ", "_")
                del i["name"]
                new_data_list[name] = i["value"]
            del self.data["dataList"]
        except KeyError:
            pass
        return new_data_list
