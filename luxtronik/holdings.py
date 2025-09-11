"""Parse luxtronik Holdings."""

import logging
from typing import Final

from luxtronik.data_vector import DataVectorModbus, LuxtronikModbusField
from luxtronik.definitions.holdings import HOLDINGS_DEFINITIONS, HOLDINGS_IDX_TO_DEF

class Holdings(DataVectorModbus):
    """Class that holds all Holdings."""

    logger = logging.getLogger("Luxtronik.Holdings")
    name = "Holdings"
    offset = 10000

    @classmethod
    def _get_definitions(cls):
        return HOLDINGS_DEFINITIONS

    @classmethod
    def _get_definition_by_idx(cls, idx):
        return HOLDINGS_IDX_TO_DEF.get(idx, LuxtronikModbusField.invalid())

    def __init__(self, safe=True):
        """Initialize Holdings class."""
        super().__init__()
        self.safe = safe

    def set(self, target, value):
        """Set holding to new value."""
        index, holding = self._lookup(target, with_index=True)
        if index is not None:
            if holding.writeable or not self.safe:
                holding.value = value
            else:
                self.logger.warning("Holding '%s' not safe for writing!", holding.name)
        else:
            self.logger.warning("Holding '%s' not found", target)
