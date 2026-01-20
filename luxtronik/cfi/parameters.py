"""Parse luxtronik parameters."""

import logging
from typing import Final

from luxtronik.definitions import LuxtronikDefinitionsList
from luxtronik.definitions.parameters import (
    PARAMETERS_DEFINITIONS_LIST,
    PARAMETERS_OFFSET,
    PARAMETERS_DEFAULT_DATA_TYPE,
)

from luxtronik.cfi.constants import PARAMETERS_FIELD_NAME
from luxtronik.cfi.vector import DataVectorConfig


LOGGER = logging.getLogger(__name__)

PARAMETERS_DEFINITIONS: Final = LuxtronikDefinitionsList(
    PARAMETERS_DEFINITIONS_LIST,
    PARAMETERS_FIELD_NAME,
    PARAMETERS_OFFSET,
    PARAMETERS_DEFAULT_DATA_TYPE
)

class Parameters(DataVectorConfig):
    """Class that holds all parameters."""

    logger = LOGGER
    name = PARAMETERS_FIELD_NAME
    definitions = PARAMETERS_DEFINITIONS

    @property
    def parameters(self):
        return self._data
