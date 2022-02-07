"""
Validate the JSON schema and contents used for the config file.
"""

import hashlib
import sys
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "solarman-mqtt-schema",
    "type": "object",
    "required": [
        "name",
        "url",
        "appid",
        "secret",
        "username",
        "passhash",
        "stationId",
        "inverterId",
        "loggerId",
    ],
    "properties": {
        "name": {
            "type": "string",
        },
        "url": {"type": "string"},
        "appid": {"type": "string", "minLength": 15, "maxLength": 15},
        "secret": {"type": "string", "minLength": 32, "maxLength": 32},
        "username": {"type": "string"},
        "passhash": {"type": "string", "minLength": 64, "maxLength": 64},
        "stationId": {"type": "number", "minimum": 100000, "maximum": 9999999},
        "inverterId": {
            "type": "string",
            "minLength": 10,
        },
        "loggerId": {"type": "string", "minLength": 10, "maxLength": 10},
        "debug": {"type": "boolean", "optional": True},
        "mqtt": {
            "type": "object",
            "properties": {
                "broker": {
                    "type": "string",
                },
                "port": {"type": "integer", "minimum": 1024, "maximum": 65535},
                "topic": {
                    "type": "string",
                },
                "username": {
                    "type": "string",
                },
                "password": {
                    "type": "string",
                },
            },
        },
    },
}

_VALID = """
The provided config file is valid. This check validates if:

  * The config file is a valid JSON file
  * The config file contains the required keys
  * The config file contains the correct types for the provided keys

Although that is not a guarantee that the contents are valid. If
you still have issues, please check all values and try again.

If you need any further help, please see:
<https://github.com/mpepping/solarman-mqtt>
"""


class ConfigCheck:  # pylint: disable=too-few-public-methods
    """
    Validate the config file
    """

    def __init__(self, config):
        """
        Main
        :return:
        """
        self.config = config
        try:
            validate(instance=self.config, schema=_SCHEMA)
        except ValidationError as err:
            print(err.message)
            sys.exit(1)
        except SchemaError as err:
            print(err.message)
            sys.exit(1)

        print(_VALID)
        sys.exit(0)


class HashPassword:  # pylint: disable=too-few-public-methods
    """
    Hash the password
    """

    def __init__(self, password):
        self.password = password
        self.hashed = ""
        HashPassword.hash(self)

    def hash(self):
        """
        Return hashed string
        :return:
        """
        self.hashed = hashlib.sha256(self.password.encode("utf-8")).hexdigest()
        return self.hashed
