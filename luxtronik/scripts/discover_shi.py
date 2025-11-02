#! /usr/bin/env python3
# pylint: disable=invalid-name
"""
Script to scan all inputs/holdings of the Smart-Home-Interface.
Only undefined but existing fields will be dumped.
"""

import argparse
import logging

from luxtronik.scripts import *
from luxtronik.datatypes import Unknown
from luxtronik.shi.constants import LUXTRONIK_DEFAULT_MODBUS_PORT
from luxtronik.shi.modbus import LuxtronikModbusTcpInterface
from luxtronik.shi.inputs import INPUTS_DEFINITIONS
from luxtronik.shi.holdings import HOLDINGS_DEFINITIONS

logging.disable(logging.CRITICAL)

def get_undefined_fields(definitions, start, count):
    skip_count = 0
    undefined_fields = {}
    for i in range(start, start + count):
        # Skip addresses that belongs to a previous field
        if skip_count > 0:
            skip_count -= 1
            continue
        definition = definitions[i]
        # Add unknown
        if definition is None:
            undefined_fields[i] = Unknown(f"unknown_{definitions.name}_{i}", False)
            #print(f"Add unknown {i}")
        else:
            skip_count = definition.count - 1
            #print(f"Skip {definition}")
    return undefined_fields

def dump_fields(undefined_fields, offset, read_cb):
    for number, field in undefined_fields.items():
        print(f"Number: {number:<5}", end="\r")
        data = read_cb(number + offset, 1)
        if data is not None:
            field.raw = data[0]
            print_dump_row(number, field)

def discover_fields(definitions, start, count, read_cb):
    print_dump_header(f"Undefined but existing {definitions.name}s")
    undefined_fields = get_undefined_fields(definitions, start, count)
    dump_fields(undefined_fields, definitions.offset, read_cb)

def discover_shi():
    parser = create_default_args_parser(
        "Dumps all undefined but existing fields of the Smart-Home-Interface.",
        LUXTRONIK_DEFAULT_MODBUS_PORT
    )
    parser.add_argument(
        "count",
        nargs="?",
        type=int,
        default=1000,
        help="Total number of registers to check",
    )
    args = parser.parse_args()
    print(f"Discover SHI of {args.ip}:{args.port}")

    client = LuxtronikModbusTcpInterface(args.ip, args.port)

    discover_fields(INPUTS_DEFINITIONS, 0, args.count, client.read_inputs)
    discover_fields(HOLDINGS_DEFINITIONS, 0, args.count, client.read_holdings)


if __name__ == "__main__":
    discover_shi()
