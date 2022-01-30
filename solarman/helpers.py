"""
Validate the JSON schema and contents used for the config file.
"""

import hashlib
import sys
import time
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

schema = {
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
        "loggerId"
        ],
    "properties": {
        "name": {
            "type": "string",
        },
        "url": {
            "type": "string"
        },
        "appid": {
            "type": "string",
            "minLength": 15,
            "maxLength": 15
        },
        "secret": {
            "type": "string",
            "minLength": 32,
            "maxLength": 32
        },
        "username": {
            "type": "string"
        },
        "passhash": {
            "type": "string",
            "minLength": 64,
            "maxLength": 64
        },
        "stationId": {
            "type": "number",
            "minimum": 100000,
            "maximum": 9999999
        },
        "inverterId": {
            "type": "string",
            "minLength": 10,
        },
        "loggerId": {
            "type": "string",
            "minLength": 10,
            "maxLength": 10
        },
        "debug" : {
            "type": "boolean",
            "optional": True
        },
        "mqtt": {
            "type": "object",
            "properties": {
                "broker": {
                    "type": "string",
                },
                "port": {
                    "type": "integer",
                    "minimum": 1024,
                    "maximum": 65535
                },
                "topic": {
                    "type": "string",
                },
                "username": {
                    "type": "string",
                },
                "password": {
                    "type": "string",
                }
            }
        }
    }
}

VALID = """
The provided config file is valid. This check validates if:

  * The config file is a valid JSON file
  * The config file contains the required keys
  * The config file contains the correct types for the provided keys

Although that is not a guarantee that the contents are valid. If
you still have issues, please check all values and try again.

If you need any further help, please see:
<https://github.com/mpepping/solarman-mqtt>
"""

def check(config):
    """
    Main
    :return:
    """
    try:
        # validate(instance=json.load(open(config)), schema=schema)
        validate(instance=config, schema=schema)
    except ValidationError as err:
        print(err.message)
        sys.exit(1)
    except SchemaError as err:
        print(err.message)
        sys.exit(1)

    print(VALID)
    sys.exit(0)

def hash_password(password):
    """
    Hash the password
    """
    encoded=password.encode('utf-8')
    result = hashlib.sha256(encoded)
    _hash = result.hexdigest()
    return _hash
