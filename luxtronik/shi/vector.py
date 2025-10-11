
from luxtronik.datatypes import Unknown
from luxtronik.shi.common import ContiguousDataBlockList
from luxtronik.shi.versions import (
    LUXTRONIK_LATEST_SHI_VERSION,
)

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
        # Instead of re-create the block-list on every read, we just update it
        # on first time used or on next time used if some fields are added.
        self._read_blocks_updated = False
        self._read_blocks = ContiguousDataBlockList(self.name, True)

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
        obj = cls.__new__(cls) # this don't call __init__()
        obj.safe = safe
        obj._version = version
        obj._data = LuxtronikFieldDictionary.empty(cls.definitions, version)
        return obj

    def __getitem__(self, def_name_or_idx):
        return self.get(def_name_or_idx)

    def __len__(self):
        return len(self._data)

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
        self._read_blocks_updated = False
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

    def update_read_blocks(self):
        if not self._read_blocks_updated:
            self._read_blocks.clear()
            for definition, field in self._data:
                self._read_blocks.collect(definition, field)
        self._read_blocks_updated = True


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

    def get(self, def_name_or_idx, default=None):
        """
        Get entry by definition, name or index.

        Args:
            def_name_or_idx (LuxtronikFieldDefinition | str | int):
                Definition, name, or index to be used to search for the field.

        Returns:
            Base | None: The field found or none if not found.
        """
        return self._data.get(def_name_or_idx, default)

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