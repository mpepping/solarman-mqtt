"""
Collect PV data from the SolarmanPV API and send Power+Energy data (W+kWh) to MQTT
"""

import solarman


def main():
    """Main"""
    solarman.main()


if __name__ == "__main__":
    main()
