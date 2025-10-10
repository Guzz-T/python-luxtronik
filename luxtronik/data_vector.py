"""Provides a base class for parameters, calculations, visibilities."""

import logging

from luxtronik.datatypes import Unknown


class DataVector:
    """Class that holds a vector of data entries."""

    logger = logging.getLogger("Luxtronik.DataVector")
    name = "DataVector"

    def __init__(self):
        """Initialize DataVector class."""
        self._data = {}

    def __iter__(self):
        """Iterator for the data entries."""
        return iter(self._data.items())

    def parse(self, raw_data):
        """Parse raw data."""
        for index, data in enumerate(raw_data):
            entry = self._data.get(index, None)
            if entry is not None:
                entry.raw = data
            else:
                # self.logger.warning(f"Entry '%d' not in list of {self.name}", index)
                entry = Unknown(f"Unknown_{self.name}_{index}")
                entry.raw = data
                self._data[index] = entry

    def _lookup(self, target, with_index=False):
        """
        Lookup an entry

        "target" could either be its id or its name.

        In case "with_index" is set, also the index is returned.
        """
        if isinstance(target, str):
            try:
                # Try to get entry by id
                target_index = int(target)
            except ValueError:
                # Get entry by name
                target_index = None
                for index, entry in self._data.items():
                    if entry.name.lower() == target.lower():
                        target_index = index
        elif isinstance(target, int):
            # Get entry by id
            target_index = target
        else:
            target_index = None

        target_entry = self._data.get(target_index, None)
        if target_entry is None:
            self.logger.warning("entry '%s' not found", target)
        if with_index:
            return target_index, target_entry
        return target_entry

    def get(self, target):
        """Get entry by id or name."""
        entry = self._lookup(target)
        return entry

###############################################################################
# Smart home interface data-vector
###############################################################################
class DataVectorSmartHome(DataVector):
    """
    Specialized DataVector for Luxtronik Smart Home fields.

    Provides access to fields by name or index,
    supports parsing of raw data, and can create unknown fields.
    """

    definitions = None # override this


# Common class methods ########################################################

    @classmethod
    def create_unknown_field(cls, idx):
        """
        Create an unknown field object.
        Be careful! The field may not exist.

        Args:
            idx (int): Register index.

        Returns:
            Unknown: A placeholder field instance.
        """
        # Create an unknown field
        return Unknown(f"Unknown_{cls.name}_{idx}", False)

    @classmethod
    def create_any_field(cls, name_or_idx):
        """
        Create a field object.
        Be careful! The field may not exist.

        Args:
            name_or_idx (str | int): Field name or register index.

        Returns:
            Base | None: The created field, or None if not found or not valid.
        """
        # The definitions object hold all available fields
        definition = cls.definitions.get(name_or_idx)
        if definition is not None and definition.valid:
            return definition.create_field()
        return None


# Constructors and magic methods ##############################################

    def __init__(self, version=LUXTRONIK_LATEST_SHI_VERSION, safe=True):
        """
        Initialize the data-vector instance.
        Creates field objects for all desired definitions and stores them in the data vector.

        Args:
            version (tuple[int] | None): Version to be used for creating the field objects.
                This ensures that the data vector only contain valid fields.
                If None is passed, all available fields are added.
                (default: LUXTRONIK_LATEST_SHI_VERSION)
            safe (bool): If false, prevent fields marked as
                not secure from being written to.
        """
        self.safe = safe
        self._version = version
        self._data = LuxtronikFieldDictionary(cls.definitions, version)

    @classmethod
    def empty(cls, version=LUXTRONIK_LATEST_SHI_VERSION, safe=True):
        """
        Initialize an empty data-vector instance
        (= no fields are added to this data-vector).

        Args:
            version (tuple[int] | None): The version is added to the data vector
                so some checks can be performed later.
                (default: LUXTRONIK_LATEST_SHI_VERSION)
            safe (bool): If false, prevent fields marked as
                not secure from being written to.
        """
        obj = cls.__new__(cls)
        obj.safe = safe
        obj._version = version
        obj._data = LuxtronikFieldDictionary.empty(cls.definitions, version)
        return obj

    def __getitem__(self, def_name_or_idx):
        return self.get(def_name_or_idx)

    def __contains__(self, def_field_name_or_idx):
        return def_field_name_or_idx in self._data


# Add and alias methods #######################################################

    def add(self, def_field_name_or_idx, alias=None):
        """
        Adds an additional field to this data vector.
        Mainly used for vectors created with empty()
        to read/write individual fields.

        Args:
            def_field_name_or_idx (LuxtronikFieldDefinition | Base | str | int):
                Field to add. Either by definition, name or index, or the field itself.
            alias (any | None): Alias, which can be used to access the field again.

        Returns:
            Base | None: The added field object if this could be added.
        """
        return self._data.add(def_field_name_or_idx, alias)

    def register_alias(self, def_field_name_or_idx, alias):
        """
        Add an alternative name (or anything else) that can be used to access a specific field.

        Args:
            def_field_name_or_idx (LuxtronikFieldDefinition | Base | str | int):
                Field to which the alias is to be added.
                Either by definition, name or index, or the field itself.
            alias (any | None): Alias, which can be used to access the field again.

        Returns:
            Base | None: The field to which the alias was added, or None if not possible
        """
        return self._data.register_alias(def_field_name_or_idx, alias)


# Data and access methods #####################################################

    def parse(self, raw_data):
        """
        Parse raw data into the corresponding fields.

        Args:
            raw_data (list[int]): List of raw register values.
        """
        raw_len = len(raw_data)
        for definition, field in self._data.items():
            if definition.idx >= raw_len:
                continue
            field.raw = definition.extract_raw(raw_data)

    def get(self, def_name_or_idx):
        """
        Get entry by definition, name or index.

        Args:
            def_name_or_idx (LuxtronikFieldDefinition | str | int):
                Definition, name, or index to be used to search for the field.

        Returns:
            Base | None: The field found or none if not found.
        """
        return self._data.get(def_name_or_idx)

    def set(self, def_field_name_or_idx, value):
        """
        Set field to new value.

        Args:
            def_field_name_or_idx (LuxtronikFieldDefinition | Base | int | str):
                Definition, name, or index to be used to search for the field.
                It is also possible to pass the field itself.
            value (int | List[int]): Value to set
        """
        field = def_field_name_or_idx
        if not isinstance(field, Base):
            field = self._data.get(def_field_name_or_idx)
        if field is not None and field.writeable or not self.safe:
            field.value = value
        else:
            self.logger.warning(f"Field '{field.name}' not found or not safe for writing!")