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

## MQTT topics

### Station (Plant)

```
solarmanpv/station/batteryPower
solarmanpv/station/batterySoc
solarmanpv/station/chargePower
solarmanpv/station/code
solarmanpv/station/dischargePower
solarmanpv/station/generationPower
solarmanpv/station/gridPower
solarmanpv/station/irradiateIntensit
solarmanpv/station/lastUpdateTime
solarmanpv/station/msg
solarmanpv/station/purchasePower
solarmanpv/station/requestId
solarmanpv/station/success
solarmanpv/station/usePower
solarmanpv/station/wirePower
```

### Inverter

```
solarmanpv/inverter/code
solarmanpv/inverter/deviceId
solarmanpv/inverter/deviceSn
solarmanpv/inverter/deviceState
solarmanpv/inverter/deviceType
solarmanpv/inverter/msg
solarmanpv/inverter/requestId
solarmanpv/inverter/success

olarmanpv/inverter/attributes # contains all inverter datalist entries

```

### Logger (Collector)

```
solarmanpv/logger/code
solarmanpv/logger/deviceId
solarmanpv/logger/deviceSn
solarmanpv/logger/deviceState
solarmanpv/logger/deviceType
solarmanpv/logger/msg
solarmanpv/logger/requestId
solarmanpv/logger/success

solarmanpv/logger/attributes # contains all logger datalist entries
```

## Home Assistant
```
sensor:
  - platform: mqtt
    name: "solarmanpv_station_generationPower"
    state_topic: "solarmanpv/station/generationPower"
    unit_of_measurement: "W"
    state_class: measurement
```

Repeat for every station topic needed. 

```
sensor:
  - platform: mqtt
    name: "solarmanpv_inverter"
    state_topic: "solarmanpv/inverter/deviceState"
    json_attributes_topic: "solarmanpv/inverter/attributes"
    
  - platform: mqtt
    name: "solarmanpv_logger"
    state_topic: "solarmanpv/logger/deviceState"
    json_attributes_topic: "solarmanpv/logger/attributes"
```

Extract inverter and logger attributes as usual by means of e.g. templates.

# Docker Usage has not been updated yet for this fork. However, Dockerfile in this repo should work. 

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

