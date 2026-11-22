
import logging

from luxtronik.data_vector import DataVector

from luxtronik.shi.contiguous import ContiguousDataBlockList


LOGGER = logging.getLogger(__name__)

###############################################################################
# Smart home interface data-vector
###############################################################################

class DataVectorSmartHome(DataVector):
    """Specialized DataVector for Luxtronik smart home fields."""

    def _init_instance(self, version, safe):
        """Re-usable method to initialize all instance variables."""
        super()._init_instance(version, safe)

        # Instead of re-create the block-list on every read, we just update it
        # on first time used or on next time used if some fields are added.
        self._read_blocks_up_to_date = False
        self._read_blocks = ContiguousDataBlockList(self.name, True)

    def update_read_blocks(self):
        """
        (Re-)Create the data block list (`ContiguousDataBlockList`) for read-operations.

        Since the data blocks do not change as long as no new fields are added,
        it is sufficient to regenerate them only when a change occurs.
        """
        if not self._read_blocks_up_to_date:
            self._read_blocks.clear()
            for definition, field in self._data.pairs:
                self._read_blocks.collect(definition, field)
        self._read_blocks_up_to_date = True
