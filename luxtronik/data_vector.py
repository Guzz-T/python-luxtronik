"""Provides a base class for parameters, calculations, visibilities."""

import logging

from luxtronik.collections import LuxtronikFieldsDictionary
from luxtronik.datatypes import Base, Unknown
from luxtronik.definitions import LuxtronikDefinition


LOGGER = logging.getLogger(__name__)


###############################################################################
# Base class for all luxtronik data vectors
###############################################################################

class DataVector:
    """
    Class that holds a vector of data entries.

    Provides access to fields by name, index or alias.
    To use aliases, they must first be registered here (locally = only valid
    for this vector) or directly in the `LuxtronikDefinitionsList`
    (globally = valid for all newly created vector).
    """

    name = "DataVector"

    # DataVector specific list of definitions as `LuxtronikDefinitionsList`
    definitions = None # override this

    _obsolete = {}


# Field construction methods ##################################################

    @classmethod
    def create_unknown_field(cls, idx):
        """
        Create an unknown field object.
        Be careful! The used controller firmware
        may not support this field.

        Args:
            idx (int): Register index.

        Returns:
            Unknown: A field instance of type 'Unknown'.
        """
        return Unknown(f"unknown_{cls.name}_{idx}", False)

    @classmethod
    def create_any_field(cls, name_or_idx):
        """
        Create a field object from an available definition
        (= included in class variable `cls.definitions`).
        Be careful! The used controller firmware
        may not support this field.

        Args:
            name_or_idx (str | int): Field name or register index.

        Returns:
            Base | None: The created field, or None if not found or not valid.
        """
        # The definitions object hold all available definitions
        definition = cls.definitions.get(name_or_idx)
        if definition is not None and definition.valid:
            return definition.create_field()
        return None

    def create_field(self, name_or_idx):
        """
        Create a field object from a version-dependent definition (= included in
        class variable `cls.definitions` and is valid for `self.version`).

        Args:
            name_or_idx (str | int): Field name or register index.

        Returns:
            Base | None: The created field, or None if not found or not valid.
        """
        definition, _ = self._get_definition(name_or_idx, False)
        if definition is not None and definition.valid:
            return definition.create_field()
        return None


# constructor, magic methods and iterators ####################################

    def _init_instance(self, safe):
        """Re-usable method to initialize all instance variables."""
        self.safe = safe

        # Dictionary that holds all fields
        self._data = LuxtronikFieldsDictionary()

    def __init__(self):
        """Initialize DataVector class."""
        self._init_instance(True)

    @property
    def data(self):
        return self._data

    def __getitem__(self, def_name_or_idx):
        return self.get(def_name_or_idx)

    def __setitem__(self, def_name_or_idx, value):
        return self.set(def_name_or_idx, value)

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, def_field_name_or_idx):
        """
        Check whether the data vector contains a name, index,
        or definition matching an added field, or the field itself.

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | str | int):
                Definition object, field object, field name or register index.

        Returns:
            True if the searched element was found, otherwise False.
        """
        return def_field_name_or_idx in self._data

    def values(self):
        return iter(self._data.values())

    def items(self):
        return iter(self._data.items())


# Alias methods ###############################################################

    def register_alias(self, def_field_name_or_idx, alias):
        """
        Add an alternative name (or anything hashable else)
        that can be used to access a specific field.

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | str | int):
                Field to which the alias is to be added.
                Either by definition, name, register index, or the field itself.
            alias (Hashable): Alias, which can be used to access the field again.

        Returns:
            Base | None: The field to which the alias was added,
                or None if not possible
        """
        return self._data.register_alias(def_field_name_or_idx, alias)


# Parse methods ###############################################################

    def parse(self, raw_data):
        """
        Parse raw data into the corresponding fields.

        Args:
            raw_data (list[int]): List of raw register values.
                The raw data must start at register index 0.
        """
        raw_len = len(raw_data)
        undefined = {i for i in range(0, raw_len)}
        for pair in self._data.pairs():
            definition, field = pair
            next_idx = definition.index + definition.count
            if next_idx >= raw_len:
                # not enough registers
                continue
            for index in range(definition.index, next_idx):
                undefined.discard(index)
            pair.integrate_data(raw_data)
        # create an unknown field for additional data
        for index in undefined:
            # LOGGER.warning(f"Entry '%d' not in list of {self.name}", index)
            definition = self.definitions.create_unknown_definition(index)
            field = definition.create_field()
            field.raw = raw_data[index]
            self._data.add_sorted(definition, field)


# Get and set methods #########################################################

    def _get_definition(self, def_field_name_or_idx, all_not_version_dependent):
        """
        Look-up a definition by name, index, a field instance or by the definition itself.

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | str | int):
                Definition object, field object, field name or register index.
            all_not_version_dependent (bool): If true, look up the definition
                within the `cls.definitions` otherwise within `self._data` (which
                contain all definitions related to all added fields)

        Returns:
            tuple[LuxtronikDefinition | None, Base | None]:
                A definition-field-pair tuple:
                Index 0: Return the found or given definitions, otherwise None
                Index 1: Return the given field, otherwise None
        """
        definition = def_field_name_or_idx
        field = None
        if isinstance(def_field_name_or_idx, Base):
            definition = def_field_name_or_idx.name
            field = def_field_name_or_idx
        if not isinstance(def_field_name_or_idx, LuxtronikDefinition):
            if all_not_version_dependent:
                definition = self.definitions.get(definition)
            else:
                # _data.definitions contains only valid and previously added definitions
                definition = self._data.definitions.get(definition)
        return definition, field

    def get(self, def_name_or_idx, default=None):
        """
        Retrieve a field by definition, name or register index.

        Args:
            def_name_or_idx (LuxtronikDefinition | str | int):
                Definition, name, or register index to be used to search for the field.

        Returns:
            Base | None: The field found or the provided default if not found.

        Note:
            If multiple fields added for the same index/name,
            the last added takes precedence.
        """
        obsolete_entry = self._obsolete.get(def_name_or_idx, None)
        if obsolete_entry:
            raise KeyError(f"The name '{def_name_or_idx}' is obsolete! Use '{obsolete_entry}' instead.")
        field = self._data.get(def_name_or_idx, default)
        if field is None:
            LOGGER.warning(f"entry '{def_name_or_idx}' not found")
        return field

    def set(self, def_field_name_or_idx, value):
        """
        Set field to new value.

        The value is set, even if the field marked as non-writeable.
        No data validation is performed either.

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | int | str):
                Definition, name, or register index to be used to search for the field.
                It is also possible to pass the field itself.
            value (int | List[int]): Value to set
        """
        field = def_field_name_or_idx
        print(field)
        if not isinstance(field, Base):
            field = self.get(def_field_name_or_idx)
        print(field)
        if field is not None:
            field.value = value