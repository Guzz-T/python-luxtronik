#!/usr/bin/env python
import logging
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape

from luxtronik.cfi import (
    CALCULATIONS_DEFINITIONS,
    PARAMETERS_DEFINITIONS,
    VISIBILITIES_DEFINITIONS,
)
from luxtronik.shi import (
    INPUTS_DEFINITIONS,
    HOLDINGS_DEFINITIONS,
)

from luxtronik.datatypes import (
    SelectionBase,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("docs generator")


BASEPATH = Path(__file__).resolve().parent


def get_string(string):
    return f'"{str(string)}"'

def get_writeable(writeable):
    return get_string("y" if writeable else "")

def get_unit(unit):
    return get_string(unit if unit else "")

def get_version(version):
    return get_string("" if version is None else ".".join(map(str, version[:3])))

def get_desc(desc):
    return get_string(desc.replace('\n', '\\n'))

def get_items(definitions):
    items = []
    for d in definitions:
        desc = d.description
        if issubclass(d.field_type, SelectionBase) and d.writeable:
            desc += ("\n" if desc else "") + "\nUser-Options:\n" + "\n".join(d.field_type.options())
        items.append({
            "category": get_string(definitions.name),
            "index": d.index,
            "name": get_string(d.name),
            "lsb": 0 if d.bit_offset is None else d.bit_offset,
            "width": d.num_bits,
            "class": get_string(d.field_type.datatype_class),
            "writeable": get_writeable(d.writeable),
            "unit": get_unit(d.field_type.unit),
            "since": get_version(d.since),
            "until": get_version(d.until),
            "description": get_desc(desc),
        })
    return items

def gather_data():
    logger.info("gather docs data")
    defs = [
        PARAMETERS_DEFINITIONS,
        CALCULATIONS_DEFINITIONS,
        VISIBILITIES_DEFINITIONS,
        HOLDINGS_DEFINITIONS,
        INPUTS_DEFINITIONS
    ]
    data = {}
    for d in defs:
        data[d.name] = get_items(d)
    return data

def render_docs():
    logger.info("render docs")
    env = Environment(loader=FileSystemLoader(str(BASEPATH / "templates")), autoescape=select_autoescape())
    template = env.get_template("definitions.js")

    data = gather_data()
    (BASEPATH.parents[3] / "docs").mkdir(exist_ok=True)

    for name, items in data.items():
        with open(BASEPATH.parents[3] / f"docs/{name}.js", "w", encoding="UTF-8") as f:
            f.write(template.render(group=name.upper(), data=items, now=datetime.now()))

if __name__ == "__main__":
    render_docs()
