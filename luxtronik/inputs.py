"""Parse luxtronik Inputs."""

import logging

from luxtronik.data_vector import DataVectorSmartHome
from luxtronik.definitions.inputs import INPUTS_DEFINITIONS, INPUTS_FIELD_NAME

class Inputs(DataVectorSmartHome):
    """Class that holds all Inputs."""

    logger = logging.getLogger("Luxtronik.Inputs")
    name = INPUTS_FIELD_NAME

    def __init__(self):
        """Initialize Inputs class."""
        super().__init__(INPUTS_DEFINITIONS)