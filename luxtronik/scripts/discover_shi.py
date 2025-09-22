#! /usr/bin/env python3

# pylint: disable=invalid-name

"""Script to scan all inputs/holdings of the Smart-Home-Interface from 10000 to 19999. Only unknown fields will be dumped."""
import argparse
import logging

from luxtronik.scripts import *
from luxtronik import LuxtronikModbusTcpInterface
from luxtronik.shi.constants import LUXTRONIK_DEFAULT_MODBUS_PORT
from luxtronik.data_vector import LuxtronikFieldDefinition
from luxtronik.datatypes import Unknown
from luxtronik.inputs import Inputs
from luxtronik.holdings import Holdings

LOGGER = logging.getLogger("Luxtronik.Modbus")
logging.disable(logging.CRITICAL)

def fill_with_unknown(data_vector, start, count):
    skip_count = 0
    for i in range(start, start + count):
        # Skip addresses that belongs to a previous field
        if skip_count > 0:
            skip_count -= 1
            continue
        # Add unknown
        if not i in data_vector._data:
            data_vector._data[i] = data_vector.create_unknown(i)
        else:
            definition = data_vector._get_definition_by_idx(i)
            skip_count = definition.count - 1

def remove_known(data_vector):
    definitions = data_vector._definitions
    for definition in definitions:
        del data_vector._data[definition.index]

def dump_fields(data_vector, read_cb):
    for number, field in data_vector:
        print(f"Number: {number:<5}", end="\r")
        data = read_cb(number + data_vector.offset)
        field.raw = data[0]
        if field.raw is not None:
            print_dump_row(number, field)


def discover_shi():
    # pylint: disable=duplicate-code
    """Dump all unknown fields of the Smart-Home-Interface."""
    parser = argparse.ArgumentParser(description="Dumps all unknown fields of the Smart-Home-Interface.")
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
    # pylint: enable=duplicate-code

    print_dump_header("Inputs")
    inputs = Inputs()
    fill_with_unknown(inputs, 0, 10000)
    remove_known(inputs)
    dump_fields(inputs, client.read_input_raw)

    print_dump_header("Holdings")
    holdings = Holdings()
    fill_with_unknown(holdings, 0, 10000)
    remove_known(holdings)
    dump_fields(holdings, client.read_holding_raw)


if __name__ == "__main__":
    discover_shi()
