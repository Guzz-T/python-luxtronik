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


class LuxtronikFieldDefinition:
    """
    Object that contains all metadata for a data field.
    Additionally, there are some convenience functions that utilize this data to,
    for example, extract relevant information from a data array.
    """

    def __init__(self, dict, type):
        """
        Create a field definition object from a definition entry.
        Use default values if values are not set. Only the 'index' is strictly required.
        Additionally, Unknown_xxx_yy is added as a possible name if the definition is valid.
        """
        try:
            self._index = dict.get('index', -1)
            self._valid = self._index >= 0
            self._count = dict.get('count', 1)
            self._data_type = dict.get('type', Unknown)
            self._writeable = dict.get('writeable', False)
            names = dict.get('names', [])
            if isinstance(names, str):
                names = [names]
            names = [name.strip() for name in names if name.strip()]
            if self._valid:
                names += [f"Unknown_{type}_{self._index}"]
            else:
                names = ['_invalid_']
            self._names = names
            self._since = dict.get('since', "")
            self._until = dict.get('until', "")
            self._description = dict.get('description', "")
        except:
            self._valid = False
            self._index = 0

    @classmethod
    def invalid(cls):
        "Create an invalid field definition."
        obj = cls({}, "Invalids")
        return obj

    def __bool__(self):
        "Returns the valid flag."
        return self._valid

    @property
    def index(self):
        "Returns the assigned index."
        return self._index

    @property
    def count(self):
        "Returns the assigned number of used bytes/words."
        return self._count

    @property
    def data_type(self):
        "Returns the assigned data type."
        return self._data_type

    @property
    def writeable(self):
        "Returns the assigned writeable flag."
        return self._writeable

    @property
    def names(self):
        "Returns all assigned names."
        return self._names

    @property
    def name(self):
        "Returns the preferred name."
        return self._names[0]

    def create_field(self):
        "Creates a data field from the assigned information."
        return self.data_type(self.name, self.writeable)

    def extract_raw(self, raw_data, offset):
        "Extract the number of bytes/words from an array of bytes/words."
        if self:
            # Use the information of the definition to extract the raw-value
            if self.count == 1:
                raw = raw_data[offset]
            else:
                raw = raw_data[offset : offset + self.count]
        else:
            # Return a scalar if the definition is not valid
            raw = raw_data[offset]
        return raw

    def get_raw(self, field):
        "Returns the field's raw value always as a list."
        if self and self.count == 1:
            return [field.raw]
        else:
            return field.raw

    def get_data_arr(self, data):
        "Returns data always as a list."
        if not self or self.count == 1:
            return [data]
        else:
            return data


class DataVectorModbus(DataVector):

    offset = 0

    @classmethod
    def _get_definitions(cls):
        """Override this to return the field definitions."""
        return [LuxtronikFieldDefinition.invalid()]

    @classmethod
    def _get_definition(cls, name_or_idx):
        if isinstance(name_or_idx, int):
            return cls._get_definition_by_idx(name_or_idx)
        else:
            return cls._get_definition_by_name(name_or_idx)

    @classmethod
    def _get_definition_by_name(cls, name):
        for definition in cls._get_definitions():
            if name.lower() == definition.name.lower():
                return definition
            for def_name in definition.names:
                if name.lower() == def_name.lower():
                    self.logger.warning(f"'{name}' is outdated! Use '{definition.name}' instead.")
                    return definition
        return LuxtronikFieldDefinition.invalid()

    @classmethod
    def _get_definition_by_idx(cls, idx):
        for definition in cls._get_definitions():
            if idx == definition.index:
                return definition
        return LuxtronikFieldDefinition.invalid()

    @classmethod
    def create_unknown(cls, idx):
        return Unknown(f"Unknown_{cls.name}_{idx}", False)


    def __init__(self):
        """Initialize DataVector class."""
        super().__init__()
        self.safe = False

        # Fill data vector
        for definition in self._get_definitions():
            self._data[definition.index] = definition.create_field()

    def parse(self, raw_data):
        """Parse raw data."""
        raw_len = len(raw_data)
        for idx, field in self._data.items():
            if idx >= raw_len:
                continue
            definition = self._get_definition_by_idx(idx)
            field.raw = definition.extract_raw(raw_data, idx)
