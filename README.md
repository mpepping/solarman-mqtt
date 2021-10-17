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
solarmanpv/station/dischargePower
solarmanpv/station/generationPower
solarmanpv/station/gridPower
solarmanpv/station/irradiateIntensity
solarmanpv/station/lastUpdateTime
solarmanpv/station/purchasePower
solarmanpv/station/usePower
solarmanpv/station/wirePower
```

### Inverter

```
solarmanpv/inverter/deviceId
solarmanpv/inverter/deviceSn
solarmanpv/inverter/deviceState
solarmanpv/inverter/deviceType

solarmanpv/inverter/attributes # contains all inverter datalist entries.
```

#### Attributes: 
```
SN: XXXXXXXXXX
Device_Type: 4
Production_Compliance_Type: 0
Rated_Power: 300.00
Year: 48
Month: 0
Day: 0
Hour: 0
Minute: 0
Seconds: 0
Communication_Protocol_Version: V0.2.0.1
Control_Board_Firmware_Version: V0.1.1.2
Communication_Board_Firmware_Version: V0.2.0.7
DC_Voltage_PV1: 0.00
DC_Voltage_PV2: 0.00
DC_Voltage_PV3: 0.00
DC_Voltage_PV4: 0.00
DC_Current_PV1: 0.00
DC_Current_PV2: 0.00
DC_Current_PV3: 0.00
DC_Current_PV4: 0.00
DC_Power_PV1: 0.00
DC_Power_PV2: 0.00
DC_Power_PV3: 0.00
DC_Power_PV4: 0.00
AC_Voltage_1: 0.00
AC_Current_1: 0.00
Total_AC_Output_Power(Active): 0
AC_Output_Frequency_1: 0.00
Total_Production(Active): 2.50
Total_Production_1: 2.50
Total_Production_2: 0.00
Total_Production_3: 0.00
Total_Production_4: 0.00
Daily_Production(Active): 0.70
Daily_Production_1: 0.70
Daily_Production_2: 0.00
Daily_Production_3: 0.00
Daily_Production_4: 0.00
AC_Radiator_Temp: -10.00
Micro_Inverter_Port_1: XXXXXXXXXX-1
Micro_Inverter_Port_2: XXXXXXXXXX-2
Micro_Inverter_Port_3: XXXXXXXXXX-3
Micro_Inverter_Port_4: XXXXXXXXXX-4
Number_Of_MPPT_Paths: 1
Number_Of_Phases: 1
Running_Status: 4
Overfrequency_And_Load_Reduction_Starting_Point: 50.20
Islanding Protection Enabled: Enable
Overfrequency_And_Load_Reduction_Percentage: 44
GFDI Enabled: Disable
Grid-connected Standard: 0
Grid Voltage_Upper_Limit: 275.00
Grid Voltage_Lower_Limit: 180.00
Grid Frequency_Upper_Limit: 52.00
Grid Frequency_Lower_Limit: 47.50
Start-up Self-checking Time: 60
```

### Logger (Collector)

```
solarmanpv/logger/deviceId
solarmanpv/logger/deviceSn
solarmanpv/logger/deviceState
solarmanpv/logger/deviceType

solarmanpv/logger/attributes # contains all logger datalist entries
```

#### Attributes
```
Embedded_Device_SN: XXXXXXXXXX
Module_Version_No: MW3_15_5406_1.35
Extended_System_Version: V1.1.00.07
Total_running_time: 1
Offset_time: 1634486607
Data_Uploading_Period: 5
Data_Acquisition_Period: 60
Max._No._of_Connected_Devices: 1
Signal_Strength: 100
Heart_Rate: 120
IV_Curve_Supported: 1
Batch_Command_Supported: 1
Support_Reporting_Upgrading_Progress: 0
AT+UPGRADE_Command_Supported: 255
Method_Of_Protocol_Upgrade: 255
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

### Screenshot

![Screenshot](https://github.com/lechk82/solarman-mqtt/raw/main/screenshot.png "Screenshot")
![Screenshot](https://github.com/lechk82/solarman-mqtt/raw/main/screenshot_haenergy.png "Screenshot")

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

