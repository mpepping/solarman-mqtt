"""
SolarmanPV - Collect PV data from the SolarmanPV API and send Power+Energy data (W+kWh) to MQTT
"""

import argparse
import sys

from .solarmanpv import SolarmanPV


def main():
    """
    Main
    """
    parser = argparse.ArgumentParser(
        description="Collect data from Trannergy / Solarman API"
    )
    parser.add_argument("-d", "--daemon", action="store_true", help="run as a service")
    parser.add_argument(
        "-s", "--single", action="store_true", help="single run and exit"
    )
    parser.add_argument(
        "-i",
        "--interval",
        default="300",
        help="run interval in seconds (default 300 sec.)",
    )
    parser.add_argument(
        "-f",
        "--file",
        default="config.json",
        help="config file (default ./config.json)",
    )
    parser.add_argument(
        "--validate", action="store_true", help="validate config file and exit"
    )
    parser.add_argument(
        "--create-passhash",
        default="",
        help="create passhash from provided password string and exit",
    )

    args = parser.parse_args()
    solarman = SolarmanPV(args.file)
    if args.single:
        solarman.single_run_loop(args.file)
    elif args.daemon:
        solarman.daemon(args.file, args.interval)
    elif args.validate:
        solarman.validate_config(args.file)
    elif args.create_passhash:
        solarman.create_passhash(args.create_passhash)
    else:
        parser.print_help(sys.stderr)


if __name__ == "__main__":
    main()
