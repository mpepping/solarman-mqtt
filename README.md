# solarman-mqtt

Script to retrieve current Solar PV data from the Solarman API, and send Power (W) and Energy (kWh) metrics to a MQTT broker, for further use in home automation. Several PV vendors use the Solarman Smart platform for statistics. One example is the Trannergy PV converter.

```lang=bash
podman run -ti --rm ghcr.io/mpepping/solarman-mqtt:latest -h

usage: run.py [-h] [-d] [-s] [-i INTERVAL] [-f FILE] [-v]

Collect data from Trannergy / Solarman API

optional arguments:
-h, --help                       show this help message and exit
-d, --daemon                     run as a service (default)
-s, --single                     single run and exit
-i INTERVAL, --interval INTERVAL run interval in seconds (default 300 sec.)
-f FILE, --file FILE             config file (default ./config.json)
-v, --version                    show program's version number and exit
```

## Usage

You can run this script as a Docker container or in Python 3. Either way a configuration file is required. See the sample `config.sample.json` file in this repository for reference. Also, a Solarman API appid+secret is required, which can be requested via <mailto:service@solarmanpv.com>. 


### Using Docker

Docker example to run this script every 5 minutes and providing a config file:

`docker run -ti --rm -v $PWD/config.json:/opt/app-root/src ghcr.io/mpepping/solarman-mqtt:latest`


### Using docker-compose

This `docker-compose.yml` example can be used with docker-compose or podman-compose

```lang=yaml
version: '3'

services:
  solarman-mqtt:
    image: ghcr.io/mpepping/solarman-mqtt:latest
    container_name: "solarman-mqtt"
    environment:
    - TZ=Europe/Amsterdam
    volumes:
      - ./config.json:/opt/app-root/src/config.json
    restart: always
```

### Using Python

Run `pip install -r requirements.txt` and start `python3 run.py`.

