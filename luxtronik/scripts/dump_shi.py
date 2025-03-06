#! /usr/bin/env python3

# pylint: disable=invalid-name

"""Script to dump all available Smart-Home-Interface values from Luxtronik controller"""
import argparse

from luxtronik.scripts import *
from luxtronik import LuxtronikModbusTcpInterface
from luxtronik.shi.constants import LUXTRONIK_DEFAULT_MODBUS_PORT


def dump_shi():
    # pylint: disable=duplicate-code
    """Dump all available Smart-Home-Interface data from the Luxtronik controller."""
    parser = argparse.ArgumentParser(description="Dumps all Smart-Home-Interface values from Luxtronik controller")
    parser.add_argument("ip", help="IP address of Luxtronik controller to connect to")
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=LUXTRONIK_DEFAULT_MODBUS_PORT,
        help="Port to use to connect to Luxtronik controller",
    )
    args = parser.parse_args()

    client = LuxtronikSmartHomeInterface(args.ip, args.port)
    # pylint: enable=duplicate-code#

    print(f"Dump SHI of {args.ip}:{args.port}")

    print_dump_header("Inputs")
    inputs = client.read_inputs()
    for number, field in inputs:
        print_dump_row(number, field)

    print_dump_header("Holdings")
    holdings = client.read_holdings()
    for number, field in holdings:
        print_dump_row(number, field)


if __name__ == "__main__":
    dump_shi()
