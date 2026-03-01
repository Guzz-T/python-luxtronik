
import logging

from luxtronik.data_vector import DataVector


LOGGER = logging.getLogger(__name__)

###############################################################################
# Configuration interface data-vector
###############################################################################

class DataVectorConfig(DataVector):
    """Specialized DataVector for Luxtronik configuration fields."""

    def __init__(self, safe=True):
        super().__init__()
        self.safe = safe
        for d in self.definitions:
            self._data.add(d, d.create_field())