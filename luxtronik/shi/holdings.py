"""Parse luxtronik Holdings."""

import logging

from luxtronik.data_vector import DataVectorSmartHome
from luxtronik.definitions.holdings import HOLDINGS_OFFSET
from luxtronik.shi.constants import HOLDINGS_FIELD_NAME


HOLDINGS_DEFINITIONS: Final = LuxtronikFieldDefinitions.by_list(
    HOLDINGS_DEFINITIONS_LIST,
    HOLDINGS_FIELD_NAME,
    HOLDINGS_OFFSET
)

class Holdings(DataVectorSmartHome):
    """Class that holds all Holdings."""

    logger = logging.getLogger("Luxtronik.Holdings")
    name = HOLDINGS_FIELD_NAME
    definitions = HOLDINGS_DEFINITIONS