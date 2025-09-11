"""Parse luxtronik Inputs."""

import logging
from typing import Final

from luxtronik.data_vector import DataVectorModbus, LuxtronikModbusField
from luxtronik.definitions.inputs import INPUTS_DEFINITIONS, INPUTS_IDX_TO_DEF

class Inputs(DataVectorModbus):
    """Class that holds all Inputs."""

    logger = logging.getLogger("Luxtronik.Inputs")
    name = "Inputs"
    offset = 10000

    @classmethod
    def _get_definitions(cls):
        return INPUTS_DEFINITIONS

    @classmethod
    def _get_definition_by_idx(cls, idx):
        return INPUTS_IDX_TO_DEF.get(idx, LuxtronikModbusField.invalid())
