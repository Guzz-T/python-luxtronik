window.KEYS = {
  "index": {
      "key": "index",
      "requirement": "mandatory",
      "default_value": "-1",
      "description": "The underlying numerical index or offset of the data field in the Luxtronik data stream."
  },
  "count": {
      "key": "count",
      "requirement": "optional",
      "default_value": "1",
      "description": "The number of elements (currently 16 bits per element in inputs/holdings and 32 bits per element in calculations/parameters/visibilities) or data points associated with this entry."
  },
  "type": {
      "key": "type",
      "requirement": "optional",
      "default_value": "<class 'luxtronik.datatypes.Unknown'>",
      "description": "The data type to be used to interpret the corresponding raw value."
  },
  "writeable": {
      "key": "writeable",
      "requirement": "optional",
      "default_value": "False",
      "description": "Boolean flag indicating whether the field can be modified (True) or is read-only (False)."
  },
  "names": {
      "key": "names",
      "requirement": "optional",
      "default_value": "[]",
      "description": "A list of human-readable names. The first one on the list is the preferred name for this field, but all the others are also valid; however, they will trigger a warning. For simplicity, a simple string is also allowed instead of a list of names."
  },
  "successor": {
      "key": "successor",
      "requirement": "optional",
      "default_value": "None",
      "description": "Reference to a more recent definition for this entry. If this field is filled in with the preferred name of another field, a warning will be displayed if this field continues to be used."
  },
  "since": {
      "key": "since",
      "requirement": "optional",
      "default_value": "",
      "description": "The minimum firmware version (>=) required to support this field (deprecated). Use VERSION instead. This version requirement is AND-combined with the VERSION and UNTIL requirements. Example: 1.5"
  },
  "until": {
      "key": "until",
      "requirement": "optional",
      "default_value": "",
      "description": "The maximum firmware version (<=) required to support this field before removal (deprecated). Use VERSION instead. This version requirement is AND-combined with the VERSION and SINCE requirements.Example: 2.0"
  },
  "version": {
      "key": "version",
      "requirement": "optional",
      "default_value": "",
      "description": "The firmware version requirements to support this field. Multiple requirements, separated by a comma or semicolon, can be listed one after another. These version requirements are AND-combined with the SINCE and UNTIL requirements. Example: >=1.5,<2.0"
  },
  "datatype": {
      "key": "datatype",
      "requirement": "optional",
      "default_value": "",
      "description": "The target python data type or custom parser required to decode the raw bytes. Is mainly used to correctly interpret signed or unsigned data. Example: UINT32, INT16"
  },
  "bit_offset": {
      "key": "bit_offset",
      "requirement": "optional",
      "default_value": "None",
      "description": "The bit offset indicating the index from which the data for this field begins. Primarily used for elements that consist of multiple fields, such as the running-status bits grouped together in a single element."
  },
  "bit_count": {
      "key": "bit_count",
      "requirement": "optional",
      "default_value": "None",
      "description": "The number of bits that make up the data for this field. Primarily used for elements that consist of multiple fields, such as the running-status bits grouped together in a single element."
  },
  "unit": {
      "key": "unit",
      "requirement": "information",
      "default_value": "",
      "description": "For informational purposes only: The physical unit of measurement (e.g., °C, bar, kW, l/h) for the value."
  },
  "default": {
      "key": "default",
      "requirement": "information",
      "default_value": "",
      "description": "For informational purposes only: The fallback or default value applied if no specific configuration is retrieved."
  },
  "range": {
      "key": "range",
      "requirement": "information",
      "default_value": "",
      "description": "For informational purposes only: The allowed range of values, represented as a dict with MIN and MAX."
  },
  "min": {
      "key": "min",
      "requirement": "information",
      "default_value": "",
      "description": "For informational purposes only: This key is defined for the RANGE dictionary. The lower boundary or minimum valid numerical value for the raw value."
  },
  "max": {
      "key": "max",
      "requirement": "information",
      "default_value": "",
      "description": "For informational purposes only: This key is defined for the RANGE dictionary. The upper boundary or maximum valid numerical value for the raw value."
  },
  "description": {
      "key": "description",
      "requirement": "information",
      "default_value": "",
      "description": "For informational purposes only: A descriptive string explaining the purpose of this field."
  }
};
