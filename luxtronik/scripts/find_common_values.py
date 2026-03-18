#! /usr/bin/env python3

# pylint: disable=invalid-name
"""
Get all available values and check for common raw values.
"""

import logging

from luxtronik import LuxtronikInterface
from luxtronik.scripts import create_default_args_parser


def find_common_values(data_list, shift=3):
    matches = []

    for i1, d1 in enumerate(data_list):
        for i2, d2 in enumerate(data_list):
            if d1 is d2:
                continue
            print(f'Compare {d1.name} with {d2.name}')
            for k1, v1 in d1.items():
                r1 = v1.raw
                if not isinstance(r1, int) or r1 in [0, 1, 0x7FFF, 0x7FFFFFFF]:
                    continue
                for k2, v2 in d2.items():
                    r1 = v1.raw
                    r2 = v2.raw
                    if not isinstance(r2, int) or r2 in [0, 1, 0x7FFF, 0x7FFFFFFF]:
                        continue
                    if 'unknown' not in k1.name.lower() and 'unknown' not in k2.name.lower():
                        continue
                    #print(f'Compare {k1.name} with {k2.name}')
                    p = False
                    start = 0
                    if i2 < i1:
                        r1 = r1 >> 1
                        start += 1
                    for s in range(start, shift):
                        if r1 == r2:
                            print(f'Found possible match {k1.name} : {v1.raw} == {k2.name} : {v2.raw} ({s})')
                            matches.append((k1.name, v1.raw, k2.name, v2.raw))
                            break
                        r1 = r1 >> 1
    return matches

def do_find_values(ip):
    print(f"Check values of {ip}")
    client = LuxtronikInterface(ip)
    data = client.read()
    matches = find_common_values([
        data.parameters,
        data.calculations,
        data.visibilities,
        data.holdings,
        data.inputs,
    ], 1)
    # for match in matches:
    #     print('Found possible match {match[0]}:{match[1]} == {match[2]}{match[3]}')


def find_values():
    parser = create_default_args_parser(
        "Get all available values and check for common raw values",
        None
    )
    args = parser.parse_args()
    do_find_values(args.ip)


if __name__ == "__main__":
    find_values()