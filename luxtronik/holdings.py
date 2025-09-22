"""Parse luxtronik Holdings."""

import logging

from luxtronik.data_vector import DataVectorSmartHome
from luxtronik.definitions.holdings import HOLDINGS_DEFINITIONS, HOLDINGS_FIELD_NAME


class Holdings(DataVectorSmartHome):
    """Class that holds all Holdings."""

    logger = logging.getLogger("Luxtronik.Holdings")
    name = HOLDINGS_FIELD_NAME

    def __init__(self, safe=True):
        """Initialize Holdings class."""
        super().__init__(HOLDINGS_DEFINITIONS)
        self.safe = safe