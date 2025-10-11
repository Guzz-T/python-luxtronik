"""Parse luxtronik Holdings."""

import logging
from typing import Final

from luxtronik.shi.vector import DataVectorSmartHome
from luxtronik.shi.definitions import LuxtronikDefinitionsList
from luxtronik.definitions.holdings import HOLDINGS_DEFINITIONS_LIST, HOLDINGS_OFFSET
from luxtronik.shi.constants import HOLDINGS_FIELD_NAME


HOLDINGS_DEFINITIONS: Final = LuxtronikDefinitionsList.by_list(
    HOLDINGS_DEFINITIONS_LIST,
    HOLDINGS_FIELD_NAME,
    HOLDINGS_OFFSET
)

class Holdings(DataVectorSmartHome):
    """Class that holds all Holdings."""

    logger = logging.getLogger("Luxtronik.Holdings")
    name = HOLDINGS_FIELD_NAME
    definitions = HOLDINGS_DEFINITIONS