
import logging

from luxtronik.data_vector import DataVector

LOGGER = logging.getLogger(__name__)

###############################################################################
# Configuration interface data-vector
###############################################################################

class DataVectorConfig(DataVector):
    """Specialized DataVector for Luxtronik configuration fields."""

    def __init__(self, safe=True):
        """Initialize config interface data-vector class."""
        super()._init_instance(safe)

        # Add all available fields
        for d in self.definitions:
            self._data.add(d, d.create_field())

    def add(self, def_field_name_or_idx, alias=None):
        """
        Adds an additional field to this data vector.

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | str | int):
                Field to add. Either by definition, name or index, or the field itself.
            alias (Hashable | None): Alias, which can be used to access the field again.

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
        if field is None:
            field = definition.create_field()
        self._data.add_sorted(definition, field, alias)
        return field