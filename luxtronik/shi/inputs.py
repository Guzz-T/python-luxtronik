"""Parse luxtronik Inputs."""

import logging
from typing import Final

from luxtronik.definitions import LuxtronikDefinitionsList
from luxtronik.definitions.inputs import (
    INPUTS_DEFINITIONS_LIST,
    INPUTS_OFFSET,
    INPUTS_DEFAULT_DATA_TYPE,
    INPUTS_OUTDATED,
)

from luxtronik.shi.constants import INPUTS_FIELD_NAME
from luxtronik.shi.vector import DataVectorSmartHome


LOGGER = logging.getLogger(__name__)

INPUTS_DEFINITIONS: Final = LuxtronikDefinitionsList(
    INPUTS_DEFINITIONS_LIST,
    INPUTS_FIELD_NAME,
    INPUTS_OFFSET,
    INPUTS_DEFAULT_DATA_TYPE,
)

class Inputs(DataVectorSmartHome):
    """Class that holds input fields."""

    name = INPUTS_FIELD_NAME
    definitions = INPUTS_DEFINITIONS
    _outdated = INPUTS_OUTDATED

    def get_firmware_version(self):
        """Get the firmware version as string. Behaves like the Calculations.get_firmware_version"""
        defs = self.definitions.get_version_definitions(self.version)
        if len(defs) == 0:
            return ""
        return "V" + self.get(defs[0]).get_version_str()
