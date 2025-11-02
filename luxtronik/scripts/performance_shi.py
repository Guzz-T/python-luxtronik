#! /usr/bin/env python3
# pylint: disable=invalid-name
"""
Script to measure different access methods of the Smart-Home-Interface.
"""

import argparse
from contextlib import contextmanager
import time

from luxtronik.scripts import *
from luxtronik.shi import create_modbus_tcp
from luxtronik.shi.constants import LUXTRONIK_DEFAULT_MODBUS_PORT
from luxtronik.shi.common import LuxtronikSmartHomeReadInputsTelegram
from luxtronik.shi.modbus import LuxtronikModbusTcpInterface

@contextmanager
def measure_performance(repeats=200):
    start = time.perf_counter()
    yield range(repeats)
    end = time.perf_counter()
    print(f"Runtime: {end - start:.6f} s")

def performance_shi():
    parser = create_default_args_parser(
        "Measure different access methods of the Smart-Home-Interface.",
        LUXTRONIK_DEFAULT_MODBUS_PORT
    )
    args = parser.parse_args()
    print(f"Measure SHI performance of {args.ip}:{args.port}")

    shi = create_modbus_tcp(args.ip, args.port)
    client = shi._interface

    # with measure_performance(100) as loop:
    #     print("(A: Modbus) Read 100 single inputs with bare modbus interface")
    #     client._connect()
    #     for _ in loop:
    #         client._client.read_input_registers(10002, 1)
    #     client._disconnect()

    # with measure_performance(100) as loop:
    #     print("(A: Modbus) Read 100 single inputs one after another with re-connect every time")
    #     for _ in loop:
    #         client.read_inputs(10002, 1)

    # with measure_performance(100) as loop:
    #     print("(A: Modbus) Read 100 single holdings one after another with re-connect every time")
    #     for _ in loop:
    #         client.read_holdings(10000, 1)

    # with measure_performance(100) as loop:
    #     print("(A: Modbus) Read 100 inputs within one telegram list")
    #     telegrams = []
    #     for _ in loop:
    #         telegrams.append(LuxtronikSmartHomeReadInputsTelegram(10002, 1))
    #     client.send(telegrams)

    # with measure_performance(100) as loop:
    #     print(f"(B: Contiguous blocks) Read 100x the whole inputs vector ({len(shi.inputs)} inputs) field by field")
    #     telegrams = []
    #     for definition in shi.inputs:
    #         telegrams.append(LuxtronikSmartHomeReadInputsTelegram(definition.addr, definition.count))
    #     for _ in loop:
    #         client.send(telegrams)

    # with measure_performance(100) as loop:
    #     print(f"(B: Contiguous blocks) Read 100x the whole inputs vector ({len(shi.inputs)} inputs) with data blocks")
    #     inputs = shi.create_inputs()
    #     for _ in loop:
    #         shi.read_inputs(inputs)

    # with measure_performance(100) as loop:
    #     print("(C: Vector) Read 100x the whole inputs vector with new data vectors")
    #     for _ in loop:
    #         shi.read_inputs()

    # with measure_performance(100) as loop:
    #     print("(C: Vector) Read 100x the whole inputs vector with the same data vector")
    #     inputs = shi.create_inputs()
    #     for _ in loop:
    #         shi.read_inputs(inputs)

    with measure_performance(10) as loop:
        print("(D: Collect) Read 10x10 whole inputs vectors with re-connect every time")
        inputs = shi.create_inputs()
        for _ in loop:
            for _ in loop:
                shi.read_inputs(inputs)

    with measure_performance(10) as loop:
        print("(D: Collect) Read 10x10 whole inputs vectors via collect with only one connection each")
        inputs = shi.create_inputs()
        for _ in loop:
            for _ in loop:
                shi.collect_inputs(inputs)
            shi.send()






if __name__ == "__main__":
    performance_shi()
