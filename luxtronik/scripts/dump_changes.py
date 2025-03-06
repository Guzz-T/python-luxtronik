#! /usr/bin/env python3

# pylint: disable=invalid-name, disable=too-many-locals

"""Script to dump all value changes from Luxtronik controller"""

import sys
import time
import argparse
import select
from collections import OrderedDict

from luxtronik import LuxtronikSocketInterface
from luxtronik.constants import LUXTRONIK_DEFAULT_PORT


def dump_changes():
    """Dump all value changes from Luxtronik controller"""
    # pylint: disable=duplicate-code
    parser = argparse.ArgumentParser(description="Dumps all value changes from Luxtronik controller")
    parser.add_argument("ip", help="IP address of Luxtronik controller to connect to")
    parser.add_argument(
        "port",
        nargs="?",
        type=int,
        default=LUXTRONIK_DEFAULT_PORT,
        help="Port to use to connect to Luxtronik controller",
    )
    args = parser.parse_args()

    client = LuxtronikSocketInterface(args.ip, args.port)
    prev_data = client.read()
    # pylint: enable=duplicate-code
    changes = {}

    print("\033[2J") # clear screen

    while True:
        # Get new data
        this_data = client.read()

        # Compare this values with the initial values
        # and add changes to dictionary
        for number, param in this_data.parameters:
            key = f"para_{str(number).zfill(5)}"
            prev_param = prev_data.parameters.get(number)
            if param.raw != prev_param.raw:
                changes[key] = (
                    f"para: Number: {number:<5} Name: {prev_param.name:<60} " + f"Value: {prev_param} -> {param}"
                )
            elif key in changes:
                changes[key] = (
                    f"para: Number: {number:<5} Name: {prev_param.name:<60} " + f"Value: {prev_param}"
                )

        for number, calc in this_data.calculations:
            key = f"calc_{str(number).zfill(5)}"
            prev_calc = prev_data.calculations.get(number)
            if calc.raw != prev_calc.raw:
                changes[key] = (
                    f"calc: Number: {number:<5} Name: {prev_calc.name:<60} " + f"Value: {prev_calc} -> {calc}"
                )
            elif key in changes:
                changes[key] = (
                    f"calc: Number: {number:<5} Name: {prev_calc.name:<60} " + f"Value: {prev_calc}"
                )

        for number, visi in this_data.visibilities:
            key = f"visi_{str(number).zfill(5)}"
            prev_visi = prev_data.visibilities.get(number)
            if visi.raw != prev_visi.raw:
                changes[key] = (
                    f"visi: Number: {number:<5} Name: {prev_visi.name:<60} " + f"Value: {prev_visi} -> {visi}"
                )
            elif key in changes:
                changes[key] = (
                    f"visi: Number: {number:<5} Name: {prev_visi.name:<60} " + f"Value: {prev_visi}"
                )

        # Print changes
        print("\033[H") # Go-to home, line 0
        print("=" * 80)
        print("Press a key and enter to: q = quit; r = reset")
        print("=" * 80)
        sorted_changes = OrderedDict(sorted(changes.items()))
        for key, values in sorted_changes.items():
            print(values + "\033[0K") # clear residual line
        print("\n")

        # Read stdin
        input, _, _ = select.select([sys.stdin], [], [], 0.1)
        if input:
            key = sys.stdin.read(1)
            if key == 'q':
                break
            elif key == 'r':
                prev_data = client.read()
                changes = {}
                print("\033[2J") # clear screen
        time.sleep(1)



if __name__ == "__main__":
    dump_changes()
