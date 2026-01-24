"""Parse luxtronik visibilities."""

import logging
from typing import Final

from luxtronik.definitions import LuxtronikDefinitionsList
from luxtronik.definitions.visibilities import (
    VISIBILITIES_DEFINITIONS_LIST,
    VISIBILITIES_OFFSET,
    VISIBILITIES_DEFAULT_DATA_TYPE,
    VISIBILITIES_OUTDATED,
)

from luxtronik.cfi.constants import VISIBILITIES_FIELD_NAME
from luxtronik.cfi.vector import DataVectorConfig


LOGGER = logging.getLogger(__name__)

VISIBILITIES_DEFINITIONS: Final = LuxtronikDefinitionsList(
    VISIBILITIES_DEFINITIONS_LIST,
    VISIBILITIES_FIELD_NAME,
    VISIBILITIES_OFFSET,
    VISIBILITIES_DEFAULT_DATA_TYPE,
)

class Visibilities(DataVectorConfig):
    """Class that holds all visibilities."""

    name = VISIBILITIES_FIELD_NAME
    definitions = VISIBILITIES_DEFINITIONS
    _outdated = VISIBILITIES_OUTDATED
