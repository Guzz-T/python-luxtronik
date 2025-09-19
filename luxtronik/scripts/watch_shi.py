#! /usr/bin/env python3

# pylint: disable=invalid-name, disable=too-many-locals

"""Script to watch all value changes from the Smart-Home-Interface of the Luxtronik controller"""

import sys
import time
import argparse
import select
from collections import OrderedDict

from luxtronik.scripts import *
from luxtronik import LuxtronikModbusTcpInterface
from luxtronik.shi.constants import LUXTRONIK_DEFAULT_MODBUS_PORT


def watch_shi():
    # pylint: disable=duplicate-code
    """Watch all value changes from the Smart-Home-Interface of the Luxtronik controller"""
    parser = argparse.ArgumentParser(description="Watch all value changes from the Smart-Home-Interface of the Luxtronik controller")
    parser.add_argument("ip", help="IP address of Luxtronik controller to connect to")
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=LUXTRONIK_DEFAULT_MODBUS_PORT,
        help="Port to use to connect to Luxtronik controller",
    )
    args = parser.parse_args()

    client = LuxtronikModbusTcpInterface(args.ip, args.port)
    prev_inputs_data = client.read_inputs()
    prev_holdings_data = client.read_holdings()
    # pylint: enable=duplicate-code
    changes = {}

    print("\033[2J") # clear screen

    while True:
        # Get new data
        this_inputs_data = client.read_inputs()
        this_holdings_data = client.read_holdings()

        # Compare this values with the initial values
        # and add changes to dictionary
        for number, inpu in this_inputs_data:
            key = f"inpu_{str(number).zfill(5)}"
            prev_input = prev_inputs_data.get(number)
            if inpu.raw != prev_input.raw:
                changes[key] = (
                    f"inpu: Number: {number:<5} Name: {prev_input.name:<60} " + f"Value: {prev_input} -> {inpu}"
                )
            elif key in changes:
                changes[key] = (
                    f"inpu: Number: {number:<5} Name: {prev_input.name:<60} " + f"Value: {prev_input}"
                )

        for number, hold in this_holdings_data:
            key = f"hold_{str(number).zfill(5)}"
            prev_hold = prev_holdings_data.get(number)
            if hold.raw != prev_hold.raw:
                changes[key] = (
                    f"hold: Number: {number:<5} Name: {prev_hold.name:<60} " + f"Value: {prev_hold} -> {hold}"
                )
            elif key in changes:
                changes[key] = (
                    f"hold: Number: {number:<5} Name: {prev_hold.name:<60} " + f"Value: {prev_hold}"
                )

        # Print changes
        print("\033[H") # Go-to home, line 0
        print_watch_header("Watch Smart-Home-Interface: Press a key and enter to: q = quit; r = reset")
        sorted_changes = OrderedDict(sorted(changes.items()))
        for key, values in sorted_changes.items():
            print(values + "\033[0K") # clear residual line
        print("\n")

        # Read stdin
        # input, _, _ = select.select([sys.stdin], [], [], 0.1)
        # if input:
        #     key = sys.stdin.read(1)
        #     if key == 'q':
        #         break
        #     elif key == 'r':
        #         prev_data = client.read()
        #         changes = {}
        #         print("\033[2J") # clear screen


        time.sleep(1)


if __name__ == "__main__":
    watch_shi()
