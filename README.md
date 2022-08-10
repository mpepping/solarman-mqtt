# solarman-mqtt

Script to retrieve current Solar PV data from the Solarman API, and send Power (W) and Energy (kWh) metrics to a MQTT broker, for further use in home automation. Several PV vendors use the Solarman Smart platform for statistics. One example is the Trannergy PV converter.

```lang=bash
usage: run.py [-h] [-d] [-s] [-i INTERVAL] [-f FILE] [--validate] [--create-passhash CREATE_PASSHASH] [-v]

Collect data from Trannergy / Solarman API

optional arguments:
  -h, --help            show this help message and exit
  -d, --daemon          run as a service
  -s, --single          single run and exit
  -i INTERVAL, --interval INTERVAL
                        run interval in seconds (default 300 sec.)
  -f FILE, --file FILE  config file (default ./config.json)
  --validate            validate config file and exit
  --create-passhash CREATE_PASSHASH
                        create passhash from provided passwordand exit
  -v, --version         show program's version number and exit
```

## Usage

You can run this script as a Docker container or in Python 3. Either way, a configuration file is required. Use the sample [config.sample.json](config.sample.json) file in this repository for reference. Also, a Solarman API appid+secret is required, which can be requested via [service@solarmanpv.com](mailto:service@solarmanpv.com?subject=SolarmanPV%20API%20key%20Request).

## How to get all required input for the config file

Create a new config file by copying the [sample config file](config.sample.json) and filling in the required information.

The first part covers your SolarmanPV account:

```lang=json
{
  "name": "Trannergy",
  "url": "api.solarmanpv.com",
  "appid": "",
  "secret": "",
  "username": "",
  "passhash": "",
  [..]
}
```

* **name**: is free text to identify the platform.
* **url**: is the base URL of the API.
* **appid**: is the appid for the API (See Usage).
* **secret**: is the secret for the API (See Usage).
* **username**: is the username for the API (emailadres).
* **passhash**: is a sha256 hash of your password. This can be generated via `--create-passhash`.

The second part covers the PV inverter and logger ID's. These can be retrieved via the Solarman API.

```lang=json
{
  [..]
  "stationId": 123,
  "inverterId": 456,
  "loggerId": 789
  [..]
}
```

* **stationId**: is the ID of the station. This is the value of `stationList[0].id`.

```lang=bash
curl --location --request POST 'https://api.solarmanpv.com//station/v1.0/list?language=en' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: bearer TOKEN' \
  --data-raw '{"size":20,"page":1}'
```

* **inverterId**: is the SN of the inverter. This is the value of `deviceListItems[0].deviceSn`.
* For Bosswerk MI300 and MI600 use "MICRO_INVERTER" instead of "INVERTER".

```lang=bash
curl --location --request POST 'https://api.solarmanpv.com//station/v1.0/device?language=en' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: bearer TOKEN' \
  --data-raw '{"size":10,"page":1,"stationId":1234567,"deviceType":"INVERTER"}'
```

* **loggerId**: is the SN of the logger. This is the value of `deviceListItems[0].deviceSn`.

```lang=bash
curl --location --request POST 'https://api.solarmanpv.com//station/v1.0/device?language=en' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: bearer TOKEN' \
  --data-raw '{"size":10,"page":1,"stationId":1234567,"deviceType":"COLLECTOR"}'
```

A bearer TOKEN to use in the requests above can be retrieved by adding your APPID, APPSECRET, USERNAME, PASSHASH in this request:

```lang=bash
curl --location --request POST 'https://api.solarmanpv.com//account/v1.0/token?appId=APPID&language=en' \
  --header 'Content-Type: application/json' \
  --data-raw '{
  "appSecret": "APPSECRET",
  "email": "USERNAME",
  "password": "PASSHASH"
}'
```

The final section covers the MQTT broker, to where the metrics will be published.

```lang=json
{
  [..]
  "broker": "mqtt.example.com",
  "port": 1883,
  "topic": "solarman",
  "username": "",
  "password": ""
}
```

## MQTT topics

The following topics are published to the MQTT broker. Topics and fields may differ between PV system types. The example output below use `solarmanpv` as the topic, configured in the config file.

### Station (Plant)

Information about the plant, current power and last update time.

```lang=text
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

Inverter information.

```lang=text
solarmanpv/inverter/deviceId
solarmanpv/inverter/deviceSn
solarmanpv/inverter/deviceState
solarmanpv/inverter/deviceType
solarmanpv/inverter/attributes
```

The `attributes` field contains all inverter datalist entries as a JSON object. An expample set of attributes is shown below:

```lang=text
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

```lang=text
solarmanpv/logger/deviceId
solarmanpv/logger/deviceSn
solarmanpv/logger/deviceState
solarmanpv/logger/deviceType
solarmanpv/logger/attributes 
```

The `attributes` field contains all inverter datalist entries as a JSON object.  Some devices may send an empty object for this field.
An example set of attributes is shown below:

```lang=bash
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

```lang=yaml
sensor:
  - platform: mqtt
    name: "solarmanpv_station_generationPower"
    state_topic: "solarmanpv/station/generationPower"
    unique_id: "generatedPower"
    unit_of_measurement: "Wh"
    device_class: energy
    state_class: measurement
```

Repeat for every station topic needed.

```lang=yaml
sensor:
  - platform: mqtt
    name: "solarmanpv_inverter"
    unique_id: "solarmanpv_inverter"
    state_topic: "solarmanpv/inverter/deviceState"
    json_attributes_topic: "solarmanpv/inverter/attributes"

  - platform: mqtt
    name: "solarmanpv_logger"
    unique_id: "solarmanpv_logger"
    state_topic: "solarmanpv/logger/deviceState"
    json_attributes_topic: "solarmanpv/logger/attributes"

  - platform: template
    sensors:
      solarmanpv_inverter_device_state:
        unique_id: "inverter_device_state"
        value_template: >-
          {% set mapper =  {
              '1' : 'Online',
              '2' : 'Failure',
              '3' : 'Offline'} %}
          {% set state =  states.sensor.solarmanpv_inverter.state %}
          {{ mapper[state] if state in mapper else 'Unknown' }}

  - platform: template
    sensors:
      solarmanpv_logger_device_state:
        unique_id: "logger_device_state"
        value_template: >-
          {% set mapper =  {
              '1' : 'Online',
              '2' : 'Failure',
              '3' : 'Offline'} %}
          {% set state =  states.sensor.solarmanpv_logger.state %}
          {{ mapper[state] if state in mapper else 'Unknown' }}
```

### Templates

```lang=yaml
template:

  - sensor:
      - name: "Solarman energy daily"
        unique_id: "solarman_energy_daily"
        unit_of_measurement: 'kWh'
        state: "{{ state_attr('sensor.solarmanpv_inverter', 'Daily_Production_(Active)') }}"
        device_class: energy
        state_class: measurement
        attributes:
          last_reset: '1970-01-01T00:00:00+00:00'

  - sensor:
    - name: solarmanpv_inverter_dc_voltage_pv1
      unique_id: "solarmanpv_inverter_dc_voltage_pv1"
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Voltage_PV1') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_dc_current_pv1
      unique_id: "solarmanpv_inverter_dc_current_pv1"
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Current_PV1') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_dc_voltage_testing
      unique_id: "solarmanpv_inverter_dc_current_testing"
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Voltage_PV1') }}"
      state_class: measurement
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Current_PV1') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_dc_voltage_pv2
      unique_id: " solarmanpv_inverter_dc_voltage_pv2"
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Voltage_PV2') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_dc_current_pv2
      unique_id: "solarmanpv_inverter_dc_current_pv2"
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Current_PV2') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_dc_power_pv1
      unique_id: "solarmanpv_inverter_dc_power_pv1"
      unit_of_measurement: 'W'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Power_PV1') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_dc_power_pv2
      unique_id: "solarmanpv_inverter_dc_power_pv2"
      unit_of_measurement: 'W'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'DC_Power_PV2') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_total_production
      unique_id: "solarmanpv_inverter_total_production"
      unit_of_measurement: 'kWh'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Cumulative_Production_(Active)') }}"
      state_class: total_increasing
      
  - sensor:
    - name: solarmanpv_inverter_daily_production
      unique_id: "solarmanpv_inverter_daily_production"
      unit_of_measurement: 'kWh'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Daily_Production_(Active)') }}"
      state_class: total_increasing

  - sensor:
    - name: solarmanpv_inverter_ac_radiator_temp
      unique_id: "solarmanpv_inverter_ac_radiator_temp"
      unit_of_measurement: '°C'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'Temperature-_Inverter') }}"
      state_class: measurement
      
  - sensor:
    - name: solarmanpv_inverter_ac_voltage_1
      unique_id: "solarmanpv_inverter_ac_voltage_1"
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Voltage_R/U/A') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_current_1
      unique_id: "solarmanpv_inverter_ac_current_1"
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Current_R/U/A') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_voltage_2
      unique_id: "solarmanpv_inverter_ac_volgage_2"
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Voltage_S/V/B') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_current_2
      unique_id: "solarmanpv_inverter_ac_current_2"
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Current_S/V/B') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_voltage_3
      unique_id: "solarmanpv_inverter_ac_voltage_3"
      unit_of_measurement: 'V'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Voltage_T/W/C') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_current_3
      unique_id: "solarmanpv_inverter_ac_current_3"
      unit_of_measurement: 'A'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Current_T/W/C') }}"
      state_class: measurement

  - sensor:
    - name: solarmanpv_inverter_ac_output_frequency
      unique_id: "solarmanpv_inverter_ac_output_frequency"
      unit_of_measurement: 'Hz'
      state: "{{ state_attr('sensor.solarmanpv_inverter', 'AC_Output_Frequency_R') }}"
      state_class: measurement
```

### Screenshot

![Screenshot](https://github.com/mpepping/solarman-mqtt/raw/main/doc/images/screenshot.png "Screenshot")
![Screenshot](https://github.com/mpepping/solarman-mqtt/raw/main/doc/images/screenshot_haenergy.png "Screenshot")

## Running

The easiest way to run is via a container. Current version is available at <https://github.com/mpepping/solarman-mqtt/pkgs/container/solarman-mqtt>

### Using Docker

Docker example to run this script every 5 minutes and providing a config file:

```lang=bash
cd /opt
git clone https://github.com/mpepping/solarman-mqtt
cd solarman-mqtt
mv config.sample.json config.json # setup your config
sudo docker run --name solarman-mqtt -d --restart unless-stopped -v /opt/solarman-mqtt:/opt/app-root/src ghcr.io/mpepping/solarman-mqtt:latest
```

### Using docker-compose

This `docker-compose.yml` example can be used with docker-compose or podman-compose

```lang=yaml
version: '3'

services:
  solarman-mqtt:
    image: ghcr.io/mpepping/solarman-mqtt:latest
    container_name: "solarman-mqtt"
    environment:
    - TZ=Europe/Berlin
    volumes:
      - /opt/solarman-mqtt:/opt/app-root/src # source dir must contain you config file
    restart: unless-stopped
```

### Using Python

Run `pip install -r requirements.txt` and start `python3 run.py`.
