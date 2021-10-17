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
solarmanpv/station/irradiateIntensity
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

solarmanpv/inverter/attributes # contains all inverter datalist entries.
```

#### Attributes: 
```
SN, Device Type, Production Compliance Type, Rated Power, Year, Month, Day, Hour, Minute, Seconds, Communication Protocol Version,Control Board Firmware Version, Communication Board Firmware Version, DC Voltage PV1, DC Voltage PV2, DC Voltage PV3, DC Voltage PV4, DC Current PV1, DC Current PV2, DC Current PV3, DC Current PV4, DC Power PV1, DC Power PV2, DC Power PV3, DC Power PV4, AC Voltage 1, AC Current 1, Total AC Output Power(Active), AC Output Frequency 1, Total Production(Active), Total Production 1, Total Production 2, Total Production 3, Total Production 4, Daily Production(Active), Daily Production 1, Daily Production 2, Daily Production 3, Daily Production 4, AC Radiator Temp, Micro Inverter Port 1, Micro Inverter Port 2,Micro Inverter Port 3, 
Micro Inverter Port 4, Number Of MPPT Paths, Number Of Phases, Running Status, Overfrequency And Load Reduction Starting Point, Islanding Protection Enabled, Overfrequency And Load Reduction Percentage, GFDI Enabled, Grid-connected Standard, Grid Voltage Upper Limit, Grid Voltage Lower Limit, Grid Frequency Upper Limit, Grid Frequency Lower Limit, Start-up Self-checking Time
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

#### Attributes
```
Embedded Device SN, Module Version No, Extended System Version, Total running time, Offset time, Data Uploading Period, Data Acquisition Period, Max. No. of Connected Devices, Signal Strength, Heart Rate, IV Curve Supported, Batch Command Supported, Support Reporting Upgrading Progress, AT+UPGRADE Command Supported, Method Of Protocol Upgrade
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

### Templates

```
template:
  - sensor:
      - name: solarmanpv_inverter_dc_voltage_pv1
        unit_of_measurement: 'V'
        state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Voltage_PV1') }}"
        state_class: measurement
  - sensor:
    - name: solarmanpv_inverter_dc_current_pv1
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Current_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_dc_power_pv1
      unit_of_measurement: 'W'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Power_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_dc_power_pv1
      unit_of_measurement: 'W'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Power_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_total_production_1
      unit_of_measurement: 'kWh'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Total_Production_1') }}"
      state_class: total_increasing
      
  - sensor:
    - name: solarmanpv_inverter_daily_production_1
      unit_of_measurement: 'kWh'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Daily_Production_1') }}"
      state_class: total_increasing

  - sensor:
    - name: solarmanpv_inverter_ac_radiator_temp
      unit_of_measurement: '°C'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Radiator_Temp') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_ac_voltage_1
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Voltage_1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_ac_current_1
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Current_1') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_output_frequency_1
      unit_of_measurement: 'Hz'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Output_Frequency_1') }}"
      state_class: measurement

```

### Templates

```
template:
  - sensor:
    - name: solarmanpv_inverter_dc_voltage_pv1
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Voltage_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_dc_current_pv1
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Current_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_dc_power_pv1
      unit_of_measurement: 'W'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Power_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_total_production_1
      unit_of_measurement: 'kWh'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Total_Production_1') }}"
      state_class: total_increasing
      
  - sensor:
    - name: solarmanpv_inverter_daily_production_1
      unit_of_measurement: 'kWh'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Daily_Production_1') }}"
      state_class: total_increasing

  - sensor:
    - name: solarmanpv_inverter_ac_radiator_temp
      unit_of_measurement: '°C'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Radiator_Temp') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_ac_voltage_1
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Voltage_1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_ac_current_1
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Current_1') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_output_frequency_1
      unit_of_measurement: 'Hz'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Output_Frequency_1') }}"
      state_class: measurement

```

### Screenshot

![Screenshot](https://github.com/lechk82/solarman-mqtt/raw/main/screenshot.png "Screenshot")

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

