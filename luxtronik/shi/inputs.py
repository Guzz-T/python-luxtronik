"""Parse luxtronik Inputs."""

import logging

from luxtronik.data_vector import DataVectorSmartHome
from luxtronik.definitions.inputs import INPUTS_OFFSET
from luxtronik.shi.constants import INPUTS_FIELD_NAME


INPUTS_DEFINITIONS: Final = LuxtronikFieldDefinitions.by_list(
    INPUTS_DEFINITIONS_LIST,
    INPUTS_FIELD_NAME,
    INPUTS_OFFSET
)

class Inputs(DataVectorSmartHome):
    """Class that holds all Inputs."""

    logger = logging.getLogger("Luxtronik.Inputs")
    name = INPUTS_FIELD_NAME
    definitions = INPUTS_DEFINITIONS