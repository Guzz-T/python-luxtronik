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


class DataVectorSmartHome(DataVector):
    """
    Specialized DataVector for Luxtronik Smart Home fields.

    Provides access to field definitions by name or index,
    supports parsing of raw data, and can create unknown fields.
    """

    definitions = None # override this

    @classmethod
    def create_unknown(cls, idx):
        """
        Create an unknown field object.

        Args:
            idx (int): Register index.

        Returns:
            Unknown: A placeholder field instance.
        """
        return Unknown(f"Unknown_{cls.name}_{idx}", False)


    def __init__(self, version=None, safe=True):
        """
        Initialize the DataVectorSmartHome instance.

        Creates field objects for all definitions and stores them in the data vector.

        Args:
            definitions (LuxtronikFieldDefinitions): List of definitions
        """
        super().__init__()
        self.version = version
        self.safe = safe

    @classmethod
    def empty(cls, version=None, safe=True):
        obj = cls(version, safe)
        obj._data = LuxtronikFieldDictionary.empty(cls.definitions, version)
        return obj

    @classmethod
    def full(cls, safe=True):
        obj = cls(None, safe)
        obj._data = LuxtronikFieldDictionary.full(cls.definitions, None)
        return obj

    @classmethod
    def versioned(cls, version, safe=True):
        obj = cls(version, safe)
        obj._data = LuxtronikFieldDictionary.versioned(cls.definitions, version)
        return obj

    def add(self, target):
        self._data.add(target)

    def register_alias(self, target, alias):
        self._data.register_alias(target, alias)

    def parse(self, raw_data):
        """
        Parse raw data into the corresponding fields.

        Args:
            raw_data (list[int]): List of raw register values.
        """
        raw_len = len(raw_data)
        for d, f in self._data.items():
            if d.idx >= raw_len:
                continue
            f.raw = d.extract_raw(raw_data)

    def get(self, target):
        """Get entry by id or name."""
        return self._data.get(target)

    def set(self, target, value):
        """
        Set field to new value.

        Args:
            target (int | str): Target could either be its id or its name.
            value (int | List[int]): Value to set
        """
        field = self._data.get(target)
        if field is not None and field.writeable or not self.safe:
            field.value = value
        else:
            self.logger.warning(f"Field '{field.name}' not safe for writing!")