"""Provides a base class for parameters, calculations, visibilities."""

import logging

from luxtronik.constants import (
    LUXTRONIK_NAME_CHECK_PREFERRED,
    LUXTRONIK_NAME_CHECK_OBSOLETE,
    LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE,
)

from luxtronik.datatypes import Base
from luxtronik.definitions import LuxtronikDefinition, LuxtronikDefinitionsDictionary


LOGGER = logging.getLogger(__name__)


###############################################################################
# Common functions
###############################################################################

def pack_values(values, num_bits, reverse=True):
    """
    Packs a list of data chunks into one integer.

    Args:
        values (list[int]): raw data; distributed across multiple registers.
        num_bits (int): Number of bits per chunk.
        reverse (bool): Use big-endian/MSB-first if true,
            otherwise use little-endian/LSB-first order.

    Returns:
        int: Packed raw data as a single integer value.

    Note:
        The smart home interface uses a chunk size of 16 bits.
    """
    count = len(values)
    mask = (1 << num_bits) - 1

    result = 0
    for idx, value in enumerate(values):
        # normal: idx = 0..n-1
        # reversed index: highest chunk first
        bit_index = (count - 1 - idx) if reverse else idx

        result |= (value & mask) << (num_bits * bit_index)

    return result

def unpack_values(packed, count, num_bits, reverse=True):
    """
    Unpacks 'count' chunks from a packed integer.

    Args:
        packed (int): Packed raw data as a single integer value.
        count (int): Number of chunks to unpack.
        num_bits (int): Number of bits per chunk.
        reverse (bool): Use big-endian/MSB-first if true,
            otherwise use little-endian/LSB-first order.

    Returns:
        list[int]: List of unpacked raw data values.

    Note:
        The smart home interface uses a chunk size of 16 bits.
    """
    values = []
    mask = (1 << num_bits) - 1

    for idx in range(count):
        # normal: idx = 0..n-1
        # reversed: highest chunk first
        bit_index = (count - 1 - idx) if reverse else idx

        chunk = (packed >> (num_bits * bit_index)) & mask
        values.append(chunk)

    return values

def integrate_data(definition, field, raw_data, data_offset=-1):
    """
    Integrate raw values from a data array into the field.

    Args:
        definition (LuxtronikDefinition): Meta-data of the field.
        field (Base): Field object where to integrate the data.
        raw_data (list): Source array of bytes/words.
        data_offset (int): Optional offset. Defaults to `definition.index`.
    """
    # Use data_offset if provided, otherwise the index
    data_offset = data_offset if data_offset >= 0 else definition.index
    # Use the information of the definition to extract the raw-value
    if (data_offset + definition.count - 1) >= len(raw_data):
        raw = None
    elif definition.count == 1:
        raw = raw_data[data_offset]
    else:
        raw = raw_data[data_offset : data_offset + definition.count]
        raw = raw if len(raw) == definition.count else None
        if field.concatenate_multiple_data_chunks and raw is not None:
            # Usually big-endian (reverse=True) is used
            raw = pack_values(raw, definition.reg_bits)
    raw = raw if definition.check_raw_not_none(raw) else None
    field.raw = raw

def get_data_arr(definition, field):
    """
    Normalize the field's data to a list of the correct size.

    Args:
        definition (LuxtronikDefinition): Meta-data of the field.
        field (Base): Field object that contains data to get.

    Returns:
        list[int] | None: List of length `definition.count`,
            or None if the data size does not match.
    """
    data = field.raw
    if data is None:
        return None
    if not isinstance(data, list) and definition.count > 1 \
            and field.concatenate_multiple_data_chunks:
        # Usually big-endian (reverse=True) is used
        data = unpack_values(data, definition.count, definition.reg_bits)
    if not isinstance(data, list):
        data = [data]
    return data if len(data) == definition.count else None

###############################################################################
# Definition / field pair
###############################################################################

class LuxtronikDefFieldPair:
    """
    Combines a definition and a field into a single iterable object.
    """

    def __init__(self, definition, field):
        """
        Initialize a definition-field-pair.

        Args:
            field (Base): The field object.
            definition (LuxtronikDefinition): The definition for this field.
        """
        self.field = field
        self.definition = definition

    def __iter__(self):
        yield self.definition
        yield self.field

    @property
    def index(self):
        return self.definition.index

    @property
    def addr(self):
        return self.definition.addr

    @property
    def count(self):
        return self.definition.count

    def get_data_arr(self):
        """
        Normalize the field's data to a list of the correct size.

        Returns:
            list[int] | None: List of length `definition.count`, or None if insufficient.
        """
        return get_data_arr(self.definition, self.field)

    def integrate_data(self, raw_data, data_offset=-1):
        """
        Integrate the related parts of the `raw_data` into the field

        Args:
            raw_data (list): Source array of bytes/words.
            data_offset (int): Optional offset. Defaults to `definition.index`.
        """
        integrate_data(self.definition, self.field, raw_data, data_offset)

###############################################################################
# Field dictionary for data vectors
###############################################################################

class LuxtronikFieldsDictionary:
    """
    Dictionary that behaves like the earlier data vector dictionaries (index-field-dictionary),
    with the addition that obsolete fields are also supported and can be addressed by name.
    Aliases are also supported.
    """

    def __init__(self):
        # There may be several names or alias that points to one definition.
        # So in order to spare memory we split the name/index-to-field-lookup
        # into a name/index-to-definition-lookup and a definition-to-field-lookup
        self._def_lookup = LuxtronikDefinitionsDictionary()
        self._field_lookup = {}
        # Furthermore stores the definition-to-field-lookup separate from the
        # field-definition pairs to keep the index-sorted order when adding new entries
        self._pairs = [] # list of LuxtronikDefFieldPair

    def __getitem__(self, def_field_name_or_idx):
        return self.get(def_field_name_or_idx)

    def __setitem__(self, def_name_or_idx, value):
        assert False, "__setitem__ not implemented."

    def __len__(self):
        return len(self._def_lookup._index_dict)

    def __iter__(self):
        """
        Iterate over all non-obsolete indices. If an index is assigned multiple times,
        only the index of the preferred definition will be output.
        """
        all_related_defs = self._def_lookup._index_dict.values()
        return iter([d.index for d in self._pairs if d in all_related_defs])

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
        if isinstance(def_field_name_or_idx, Base):
            return any(def_field_name_or_idx is field for field in self._field_lookup.values())
        elif isinstance(def_field_name_or_idx, LuxtronikDefinition):
            # speed-up the look-up by search only the name-dict
            return def_field_name_or_idx.name in self._def_lookup._name_dict
        else:
            return def_field_name_or_idx in self._def_lookup

    def values(self):
        """
        Iterator for all added non-obsolete fields. If an index is assigned multiple times,
        only the field of the preferred definition will be output.
        """
        all_related_defs = self._def_lookup._index_dict.values()
        return iter([f for d, f in self._pairs if d in all_related_defs])

    def items(self):
        """
        Iterator for all non-obsolete index-field-pairs (list of tuples with
        0: index, 1: field) contained herein. If an index is assigned multiple times,
        only the index-field-pair of the preferred definition will be output.
        """
        all_related_defs = self._def_lookup._index_dict.values()
        return iter([(d.index, f) for d, f in self._pairs if d in all_related_defs])

    def pairs(self):
        """
        Return all definition-field-pairs contained herein.
        """
        return self._pairs

    @property
    def def_dict(self):
        """Return the internal definition dictionary"""
        return self._def_lookup

    def add(self, definition, field, alias=None):
        """
        Add a definition-field-pair to the internal dictionaries.

        Args:
            definition (LuxtronikDefinition): Definition related to the field.
            field (Base): Field to add.
            alias (Hashable | None): Alias, which can be used to access the field again.
        """
        if definition.valid:
            self._def_lookup.add(definition, alias)
            self._field_lookup[definition] = field
            self._pairs.append(LuxtronikDefFieldPair(definition, field))

    def add_sorted(self, definition, field, alias=None):
        if definition.valid:
            self.add(definition, field, alias)
            # sort _pairs by definition.index
            self._pairs.sort(key=lambda pair: pair.definition.index)

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
        # Resolve a field input
        def_name_or_idx = def_field_name_or_idx
        if isinstance(def_name_or_idx, Base):
            def_name_or_idx = def_name_or_idx.name
        # register alias
        definition = self._def_lookup.register_alias(def_name_or_idx, alias)
        if definition is None:
            return None
        return self._field_lookup.get(definition, None)

    def get(self, def_field_name_or_idx, default=None):
        """
        Retrieve a field by definition, name or register index.

        Args:
            def_field_name_or_idx (LuxtronikDefinition | str | int):
                Definition, name, or register index to be used to search for the field.

        Returns:
            Base | None: The field found or the provided default if not found.

        Note:
            If multiple fields added for the same index/name,
            the last added takes precedence.
        """
        def_name_or_idx = def_field_name_or_idx
        if isinstance(def_name_or_idx, Base):
            def_name_or_idx = def_name_or_idx.name
        if isinstance(def_name_or_idx, LuxtronikDefinition):
            definition = def_name_or_idx
        else:
            definition = self._def_lookup.get(def_name_or_idx)
        if definition is not None:
            return self._field_lookup.get(definition, default)
        return default

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

    logger = LOGGER
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

    def __init__(self):
        """Initialize DataVector class."""
        self._data = LuxtronikFieldsDictionary()

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
        for definition, field in self._data.pairs():
            next_idx = definition.index + definition.count
            if next_idx >= raw_len:
                # not enough registers
                continue
            for index in range(definition.index, next_idx):
                undefined.discard(index)
            integrate_data(definition, field, raw_data)
            field.write_pending = False
        # create an unknown field for additional data
        for index in undefined:
            # self.logger.warning(f"Entry '%d' not in list of {self.name}", index)
            definition = LuxtronikDefinition.unknown(index, self.name, self.definitions.offset)
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
                # def_dict contains only valid and addable definitions
                definition = self._data.def_dict.get(definition)
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
            self.logger.warning(f"entry '{def_name_or_idx}' not found")
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
        if not isinstance(field, Base):
            field = self.get(def_field_name_or_idx)
        if field is not None:
            field.value = value