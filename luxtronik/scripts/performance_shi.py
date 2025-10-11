#! /usr/bin/env python3

# pylint: disable=invalid-name

"""Script to dump all available Smart-Home-Interface values from Luxtronik controller"""
import argparse

from contextlib import contextmanager
import time

from luxtronik.scripts import *
from luxtronik.shi.modbus import LuxtronikModbusTcpInterface
from luxtronik.shi.constants import LUXTRONIK_DEFAULT_MODBUS_PORT
from luxtronik.shi.common import LuxtronikSmartHomeReadInputsTelegram


@contextmanager
def measure_performance(repeats=200):
    start = time.perf_counter()
    yield range(repeats)
    end = time.perf_counter()
    print(f"Runtime: {end - start:.6f} s")

def performance_shi():
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

    interface = LuxtronikModbusTcpInterface(args.ip, args.port)
    # pylint: enable=duplicate-code#

    print(f"Performance SHI of {args.ip}:{args.port}")



    with measure_performance(100) as loop:
        print("(A: Modbus) Read 100 single inputs with orig interface")
        interface._connect()
        for _ in loop:
            interface._client.read_input_registers(10002, 1)
        interface._disconnect()

    with measure_performance(100) as loop:
        print("(A: Modbus) Read 100 single inputs one after another")
        for _ in loop:
          data = interface.read_inputs(10002, 1)

    with measure_performance(100) as loop:
        print("(A: Modbus) Read 100 inputs within one telegram list")
        telegrams = []
        for _ in loop:
            telegrams.append(LuxtronikSmartHomeReadInputsTelegram(10002, 1))
        interface.send(telegrams)






if __name__ == "__main__":
    performance_shi()
