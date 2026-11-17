"""Information about all available keys for the definition entries"""

from enum import Enum
from luxtronik.datatypes import Unknown


class Keys(str, Enum):
    """
    Enum that holds all available definition keys and their descriptions.

    Use e.g. Keys.IDX to access the index value within a dictionary
    or Keys.IDX.description to query the description of the related key.
    """

    # KEY = (
    #    key_value
    #    requirement
    #    default_value
    #    description
    # )

    IDX = (
        "index",
        "mandatory",
        -1,
        "The underlying numerical index or offset of the data field in the Luxtronik data stream."
    )

    COUNT = (
        "count",
        "optional",
        1,
        "The number of elements (currently 16 bits per element in inputs/holdings and 32 bits "
        "per element in calculations/parameters/visibilities) or data points associated with this entry."
    )

    TYPE = (
        "type",
        "optional",
        Unknown,
        "The data type to be used to interpret the corresponding raw value.")

    WRT = (
        "writeable",
        "optional",
        False,
        "Boolean flag indicating whether the field can be modified (True) or is read-only (False)."
    )

    NAMES = (
        "names",
        "optional",
        [],
        "A list of human-readable names. The first one on the list is the preferred name for this field, "
        "but all the others are also valid; however, they will trigger a warning. "
        "For simplicity, a simple string is also allowed instead of a list of names."
    )

    SUCCESSOR = (
        "successor",
        "optional",
        None,
        "Reference to a more recent definition for this entry. If this field is filled in with the preferred name "
        "of another field, a warning will be displayed if this field continues to be used."
    )

    SINCE = (
        "since",
        "optional",
        "",
        "The minimum firmware version (>=) required to support this field (deprecated). "
        "Use VERSION instead. This version requirement is AND-combined with the "
        "VERSION and UNTIL requirements. "
        "Example: 1.5"
    )

    UNTIL = (
        "until",
        "optional",
        "",
        "The maximum firmware version (<=) required to support this field before removal (deprecated). "
        "Use VERSION instead. This version requirement is AND-combined with the "
        "VERSION and SINCE requirements."
        "Example: 2.0"
    )

    VERSION = (
        "version",
        "optional",
        "",
        "The firmware version requirements to support this field. "
        "Multiple requirements, separated by a comma or semicolon, can be listed one after another. "
        "These version requirements are AND-combined with the SINCE and UNTIL requirements. "
        "Example: >=1.5,<2.0"
    )

    DATATYPE = (
        "datatype",
        "optional",
        "",
        "The target python data type or custom parser required to decode the raw bytes. "
        "Is mainly used to correctly interpret signed or unsigned data. "
        "Example: UINT32, INT16"
    )

    BIT_OFFS = (
        "bit_offset",
        "optional",
        None,
        "The bit offset indicating the index from which the data for this field begins. "
        "Primarily used for elements that consist of multiple fields, such as the running-status "
        "bits grouped together in a single element."
    )

    BIT_CNT = (
        "bit_count",
        "optional",
        None,
        "The number of bits that make up the data for this field. "
        "Primarily used for elements that consist of multiple fields, such as the running-status "
        "bits grouped together in a single element."
    )

    UNIT = (
        "unit",
        "information",
        "",
        "For informational purposes only: "
        "The physical unit of measurement (e.g., °C, bar, kW, l/h) for the value."
    )

    DEFAULT = (
        "default",
        "information",
        "",
        "For informational purposes only: "
        "The fallback or default value applied if no specific configuration is retrieved."
    )

    RANGE = (
        "range",
        "information",
        "",
        "For informational purposes only: "
        "The allowed range of values, represented as a dict with MIN and MAX."
    )

    MIN = (
        "min",
        "information",
        "",
        "For informational purposes only: "
        "This key is defined for the RANGE dictionary. "
        "The lower boundary or minimum valid numerical value for the raw value."
    )

    MAX = (
        "max",
        "information",
        "",
        "For informational purposes only: "
        "This key is defined for the RANGE dictionary. "
        "The upper boundary or maximum valid numerical value for the raw value."
    )

    DESC = (
        "description",
        "information",
        "",
        "For informational purposes only: "
        "A descriptive string explaining the purpose of this field."
    )


    def __new__(cls, key_value: str, requirement: str, default_value, description: str):
        # Create a string object to provide a keys.XXX access to key_value
        obj = str.__new__(cls, key_value)
        obj._value_ = key_value

        # Afterwards add all properties
        obj.key_value = key_value
        obj.requirement = requirement
        obj.default_value = default_value
        obj.description = description
        return obj
