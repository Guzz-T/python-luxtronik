
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

    def add(self, def_field_name_or_idx):
        """
        Adds an additional version-dependent field (= included in class variable
        `cls.definitions` and is valid for `self.version`) to this data vector.
        Mainly used for data vectors created via `empty()`
        to read/write individual fields. Existing fields will not be overwritten.

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | str | int):
                Field to add. Either by definition, name or index, or the field itself.

        Returns:
            Base | None: The added field object if this could be added or
                the existing field, otherwise None. In case a field

        Note:
            It is not possible to add fields which are not defined.
            To add custom fields, add them to the used `LuxtronikDefinitionsList`
            (`cls.definitions`) first.
            If multiple fields added for the same index/name, the last added takes precedence.
        """
        # Look-up the related definition
        definition, field = self._get_definition(def_field_name_or_idx, True)
        if definition is None:
            return None

        # Check if the field already exists
        existing_field = self._data.get(definition, None)
        if existing_field is not None:
            return existing_field

        # Add a (new) field
        if definition.version.matches(self._version):
            if field is None:
                field = definition.create_field()
            self._read_blocks_up_to_date = False
            self._data.add_sorted(definition, field)
            return field
        return None

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
