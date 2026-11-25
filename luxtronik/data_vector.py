"""Provides a base class for parameters, calculations, visibilities."""

import logging

from luxtronik.constants import LUXTRONIK_VERSION_IGNORE
from luxtronik.collections import (
    get_and_check_def_field_pair,
    get_check_and_create_def_field_pair,
    LuxtronikFieldsDictionary
)
from luxtronik.datatypes import Base, Unknown
from luxtronik.version import VER_IGNORE, resolve_version_input


LOGGER = logging.getLogger(__name__)


###############################################################################
# Base class for all luxtronik data vectors
###############################################################################

class DataVector:
    """
    Class that holds a vector of data fields.

    Provides access to fields by name or index.
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
            Unknown: A field instance of type `Unknown`.
        """
        return Unknown(f"unknown_{cls.name}_{idx}", False)

    @classmethod
    def create_any_field(cls, def_name_or_idx):
        """
        Create a field object from an available definition
        (= included in class variable `cls.definitions`).
        Be careful! The used controller firmware
        may not support this field.

        If `def_name_or_idx`
        - is a definition -> create the field from the provided definition
        - is a name -> lookup the definition by name and create the field
        - is a idx -> lookup definition by index and create the field

        Args:
            def_name_or_idx (LuxtronikDefinition | str | int): Definitions object,
                field name or register index.

        Returns:
            Base | None: The created field, or None if not found or not valid.
        """
        _, field = get_check_and_create_def_field_pair(def_name_or_idx, cls.definitions, VER_IGNORE)
        return field

    def create_field(self, def_name_or_idx):
        """
        Create a field object from a version-dependent definition (= included in
        class variable `cls.definitions` and is valid for `self.version`).

        If `def_name_or_idx`
        - is a definition -> create the field from the provided definition
        - is a name -> lookup the definition by name and create the field
        - is a idx -> lookup definition by index and create the field

        Args:
            def_name_or_idx (str | int): Definitions object,
                field name or register index.

        Returns:
            Base | None: The created field, or None if not found or not valid.
        """
        definition, _ = get_and_check_def_field_pair(def_name_or_idx, self._data.def_dict, VER_IGNORE)
        if definition is not None and definition.valid:
            return definition.create_field()
        return None


# constructor, magic methods and iterators ####################################

    def _init_instance(self, version, safe):
        """Re-usable method to initialize all instance variables."""
        self.safe = safe
        version, _ = resolve_version_input(version) # no auto-detect possible here
        self._version = version # is never None

        # Dictionary that holds all fields
        self._data = LuxtronikFieldsDictionary()

    def __init__(self, version=LUXTRONIK_VERSION_IGNORE, safe=True):
        """
        Initialize the data-vector instance.

        Creates field objects for all version-dependent definitions (= included
        in class variable `cls.definitions` and is valid for `self.version`)
        and stores them in the data vector.

        Args:
            version (tuple[int] | str | None):
                Version to be used for creating the field objects.
                This ensures that the data vector only contain valid fields.
                If None is passed, all available fields are added.
                (default: LUXTRONIK_VERSION_IGNORE)
            safe (bool): If true, prevent fields marked as
                not secure from being written to.
        """
        self._init_instance(version, safe)

        # Create fields depending on the given version
        for d in self.definitions:
            if d.version.matches(self._version):
                # The definitions are already sorted correctly.
                # So we can just add them one after the other.
                self._data.add(d, d.create_field())

    @classmethod
    def empty(cls, version=LUXTRONIK_VERSION_IGNORE, safe=True):
        """
        Initialize the data-vector instance without any fields.

        Args:
            version (tuple[int] | str | None):
                Version to be used for creating the field objects afterwards.
                This ensures that the data vector only contain valid fields.
                If None is passed, all available fields can be added.
                (default: LUXTRONIK_VERSION_IGNORE)
            safe (bool): If true, prevent fields marked as
                not secure from being written to.
        """
        obj = cls.__new__(cls) # this don't call __init__()
        obj._init_instance(version, safe)
        return obj

    @property
    def version(self):
        return self._version

    @property
    def data(self):
        """
        Return the internal `LuxtronikFieldsDictionary`.
        Please check its documentation.
        """
        return self._data

    def __getitem__(self, def_name_or_idx):
        """
        Array-style access to method `get`.
        Please check its documentation.
        """
        return self.get(def_name_or_idx)

    def __setitem__(self, def_name_or_idx, value):
        """
        Array-style access to method `set`.
        Please check its documentation.
        """
        return self.set(def_name_or_idx, value)

    def __len__(self):
        """
        Forward the `LuxtronikFieldsDictionary.__len__` method.
        Please check its documentation.
        """
        return len(self._data)

    def __iter__(self):
        """
        Forward the `LuxtronikFieldsDictionary.__iter__` method.
        Please check its documentation.
        """
        return iter(self._data)

    def __contains__(self, def_field_name_or_idx):
        """
        Forward the `LuxtronikFieldsDictionary.__contains__` method.
        Please check its documentation.
        """
        return def_field_name_or_idx in self._data

    def values(self):
        """
        Forward the `LuxtronikFieldsDictionary.values` method.
        Please check its documentation.
        """
        return self._data.values()

    def items(self):
        """
        Forward the `LuxtronikFieldsDictionary.items` method.
        Please check its documentation.
        """
        return iter(self._data.items())


# Add methods #################################################################

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
                the existing field, otherwise None.

        Note:
            It is not possible to add fields which are not defined.
            To add custom fields, add them to the used `LuxtronikDefinitionsList`
            (`cls.definitions`) first.
            If multiple fields added for the same index/name, the last added takes precedence.
        """
        # Look-up the related definition
        definition, field = get_and_check_def_field_pair(def_field_name_or_idx, self.definitions, VER_IGNORE)
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


# Get and set methods #########################################################

    def get(self, def_field_name_or_idx, default=None):
        """
        Retrieve an added field by definition, field, name or register index.
        Triggers a key error when we try to query obsolete fields.

        If `def_field_name_or_idx`
        - is a definition -> lookup the field by the definition
        - is a field -> lookup the field by the field's name
        - is a name -> lookup the field by the name
        - is a idx -> lookup the field by the index

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | str | int):
                Definition, name, or register index to be used to search for the field.

        Returns:
            Base | None: The field found or the provided default if not found.

        Note:
            If multiple fields added for the same index/name,
            the last added takes precedence.
        """
        # check for obsolete
        obsolete_entry = self._obsolete.get(def_field_name_or_idx, None)
        if obsolete_entry:
            raise KeyError(f"The name '{def_field_name_or_idx}' is obsolete! Use '{obsolete_entry}' instead.")
        # look-up the field
        field = self._data.get(def_field_name_or_idx, default)
        if field is None:
            LOGGER.warning(f"entry '{def_field_name_or_idx}' not found")
        return field

    def set(self, def_field_name_or_idx, value):
        """
        Set the data of a field to the given value.

        The value is set, even if the field marked as non-writeable.
        No data validation is performed either.

        If `def_field_name_or_idx`
        - is a definition -> lookup the field by the definition and set the value
        - is a field -> set the value of this field
        - is a name -> lookup the field by the name and set the value
        - is a idx -> lookup the field by the index and set the value

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | int | str):
                Definition, name, or register index to be used to search for the field.
                It is also possible to pass the field itself.
            value (int | List[int]): Value to set
        """
        field = def_field_name_or_idx
        if not isinstance(field, Base):
            field = self.get(def_field_name_or_idx)
        if field is not None:
            field.value = value
