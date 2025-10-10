import logging

from luxtronik.datatypes import Base, Unknown


LOGGER = logging.getLogger("Luxtronik.definitions")



class LuxtronikFieldDefinition:
    """
    Metadata container for a Luxtronik data field.

    Provides convenience methods to create fields, extract raw values,
    and validate data arrays.
    """

    DEFAULT_DATA = {
        "index": -1,
        "count": 1,
        "type": Unknown,
        "writeable": False,
        "names": [],
        "since": "",
        "until": "",
        "description": "",
    }

    def __init__(self, data_dict, type_name, offset=LUXTRONIK_DEFAULT_DEFINITION_OFFSET):
        """
        Initialize a field definition from a dictionary.

        Args:
            data_dict (dict): Definition values. Missing keys are filled with defaults.
            type_name (str): The type name e.g. 'holding', 'input', ... .
            offset (str): Offset of the address from the specified index.
                (Default: LUXTRONIK_DEFAULT_DEFINITION_OFFSET)

        Notes:
            - Only 'index' is strictly required within `the data_dict`.
        """
        self._type_name = type_name
        self._offset = offset
        try:
            data_dict = self.DEFAULT_DATA | data_dict
            index = int(data_dict["index"])
            self._valid = index >= 0
            self._index = index if self._valid else 0
            self._count = int(data_dict["count"])
            self._data_type = data_dict["type"]
            self._writeable = bool(data_dict["writeable"])
            names = data_dict["names"]
            if not isinstance(names, list):
                names = [str(names)]
            names = [str(name).strip() for name in names if str(name).strip()]
            if not names:
                names = ["_invalid_"]
            self._names = names
            self._aliases = {}
            since = str(data_dict["since"])
            self._since = parse_version(since)
            until = str(data_dict["until"])
            self._until = parse_version(until)
            self._description = str(data_dict["description"])
        except Exception:
            self._valid = False
            self._index = 0
        self._addr = self._offset + self._index

    @classmethod
    def invalid(cls):
        """
        Create an invalid field definition.

        Returns:
            LuxtronikFieldDefinition: An invalid field definition instance.
        """
        return cls({}, 'invalid', 0)

    @classmethod
    def unknown(cls, index, type_name, offset=LUXTRONIK_DEFAULT_DEFINITION_OFFSET):
        """
        Create an unknown field definition.

        Args:
            index (int): The register index of the unknown field.
            type_name (str): The type name e.g. 'holding', 'input', ... .
            offset (str): Offset of the address from the specified index.
                (Default: LUXTRONIK_DEFAULT_DEFINITION_OFFSET)

        Returns:
            LuxtronikFieldDefinition: A field definition marked as unknown.
        """
        return cls({
            "index": index,
            "names": [f"Unknown_{type_name}_{index}"]
        }, type_name, offset)

    # @classmethod
    # def from_field(cls, index, field, type_name):
    #     """
    #     Create a field definition from an existing field object.

    #     Args:
    #         index (int): The register index of the field.
    #         field (Base): The field object to derive metadata from.
    #         type_name (str): The type name e.g. 'holding', 'input', ... .

    #     Returns:
    #         LuxtronikFieldDefinition: A field definition based on the given field.
    #     """
    #     return cls({
    #         "index": index,
    #         "type": type(field),
    #         "writeable": field.writeable,
    #         "names": [field.name]
    #     }, type_name)

    def __bool__(self):
        """Return True if the definition is valid."""
        return self._valid

    @property
    def valid(self):
        "Returns the valid flag."
        return self._valid

    @property
    def type_name(self):
        "Returns the type name (e.g. 'holding', 'input', ...)."
        return self._type_name

    @property
    def index(self):
        return self._index

    @property
    def offset(self):
        return self._offset

    @property
    def addr(self):
        return self._addr

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
    def aliases(self):
        "Returns all assigned aliases."
        return self._aliases

    @property
    def name(self):
        "Returns the preferred name."
        return self._names[0]

    @property
    def since(self):
        return self._since

    @property
    def until(self):
        return self._until

    def create_field(self):
        """
        Create a data field instance from this definition.

        Returns:
            Base | None: Field instance or None if invalid.
        """
        return self.data_type(self.name, self.writeable) if self else None

    def extract_raw(self, raw_data, data_offset=-1):
        """
        Extract raw values from a data array.

        Args:
            raw_data (list): Source array of bytes/words.
            data_offset (int): Optional offset. Defaults to self.index.

        Returns:
            int | list[int]: Single value or list of values, or None if insufficient data.
        """
        data_offset = data_offset if data_offset >= 0 else self.index
        # Use the information of the definition to extract the raw-value
        if self.count == 1:
            return raw_data[data_offset]
        else:
            raw = raw_data[data_offset : data_offset + self.count]
            return raw if len(raw) == self.count else None

    def get_raw(self, field):
        """
        Return the field's raw value as a list of the correct size.

        Args:
            field (Base): Field object with a `.raw` attribute.

        Returns:
            list[int] | None: Normalized list of raw values, or None if insufficient.
        """
        return self.get_data_arr(field.raw)

    def get_data_arr(self, data):
        """
        Normalize input data to a list of the correct size.

        Args:
            data (int | list[int]): Single value or list of values.

        Returns:
            list[int] | None: List of length `count`, or None if insufficient.
        """
        if not isinstance(data, list):
            data = [data]
        data = data[:self.count]
        return data if len(data) == self.count else None

    def check_data(self, field):
        """
        Validate that the field contains sufficient raw data.

        Args:
            field (Base): Field object with a `.raw` attribute.

        Returns:
            bool: True if valid, False otherwise.
        """
        return self.get_raw(field) is not None


class LuxtronikDefinitionLookup:

    def __init__(self):
        self._index_dict = {}
        self._name_dict = {}
        self._alias_dict = {}

    def __getitem__(self, name_or_idx):
        return self.get(name_or_idx)

    def __contains__(self, def_name_or_idx):
        if isinstance(def_name_or_idx, LuxtronikFieldDefinition)
            # All names should be unique, so this check should be sufficient
            return def_name_or_idx in self._name_dict.values()
        else:
            return (
                def_name_or_idx in self._alias_dict
                or def_name_or_idx in self._index_dict
                or def_name_or_idx in self._name_dict
            )

    def _add_alias(self, definition, alias):
        alias = alias.lower() if isinstance(alias, str) else alias
        self._alias_dict.set(alias.lower(), definition)

    def register_alias(self, def_name_or_idx, alias):
        if isinstance(def_name_or_idx, LuxtronikFieldDefinition):
            definition = def_name_or_idx if def_name_or_idx in self else None
        else:
            definition = self.get(def_name_or_idx)
        if definition is not None and alias is not None:
            self._add_alias(definition, alias)
        return definition

    def add(self, definition, alias=None):
        # Add to indices-dictionary (first occurrence wins)
        self._index_dict.setdefault(definition.index, definition)

        # Add to name-dictionary (names are unique)
        # Unique names has already been ensured by the pytest
        for n in definition.names:
            self._name_dict.set(n.lower(), definition)

        # Add to alias-dictionary (last occurrence wins)
        for alias in definition.aliases:
            self._add_alias(definition, alias)
        if alias is not None:
            self._add_alias(definition, alias)

    def get(self, name_or_idx): # , version=None):
          """
        Retrieve a field definition by name or index.

        Args:
            name_or_idx (str | int): Field name or register index.

        Returns:
            LuxtronikFieldDefinition | None: The matching definition, or None if not found.

        Note:
            If multiple definitions exist for the same index/name, the first one takes precedence.
        """
        d = self._get_definition_by_alias(name_or_idx)
        if d is None:
            if isinstance(name_or_idx, int):
                d = self._get_definition_by_idx(name_or_idx)
            if isinstance(name_or_idx, str):
                try:
                    idx_from_str = int(name_or_idx)
                    d = self._get_definition_by_idx(name_or_idx)
                except ValueError:
                    d = self._get_definition_by_name(name_or_idx)
        if d is None:
            LOGGER.warning(f"Definition for '{name_or_idx}' not found", )
        return d
        #return d if d is not None and version_in_range(version, d.since, d.until) else None

    def _get_definition_by_idx(self, idx):
        """
        Retrieve a field definition by its index.

        Args:
            idx (int): Register index.

        Returns:
            LuxtronikFieldDefinition | None: The matching definition, or None if not found.

        Note:
            If multiple definitions exist for the same index, the first one takes precedence.
        """
        return self._index_dict.get(idx, None)

    def _get_definition_by_name(self, name):
        """
        Retrieve a field definition by its name (case-insensitive).

        Args:
            name (str): Field name.

        Returns:
            LuxtronikFieldDefinition | None: The matching definition, or None if not found.

        Note:
            If multiple definitions exist for the same name, the first one takes precedence.
        """
        definition = self._name_dict.get(name.lower(), None)
        if definition is not None and definition.valid and name.lower() != definition.name.lower():
            LOGGER.warning(f"'{name}' is outdated! Use '{definition.name}' instead.")
        return definition

    def _get_definition_by_alias(self, alias):
        """
        Retrieve a field definition by its alias (case-insensitive).

        Args:
            alias (str): Field alias.

        Returns:
            LuxtronikFieldDefinition | None: The matching definition, or None if not found.

        Note:
            If multiple definitions exist for the same name, the first one takes precedence.
        """
        alias = alias.lower() if isinstance(alias, str) else alias
        return self._alias_dict.get(alias, None)


class LuxtronikFieldDefinitions:
    """
    Container for Luxtronik field definitions.

    Provides lookup by index, name or alias.
    """

    def __init__(self, name, offset=LUXTRONIK_DEFAULT_DEFINITION_OFFSET, version=None):
        """
        Initialize the (by index sorted) field definitions.

        Args:
            definitions_list (list[dict]): Raw definition entries.
            offset (int): Offset applied to register indices.
                (Default: LUXTRONIK_DEFAULT_DEFINITION_OFFSET)
            name (str): Name of a field related to this definition list (e.g. "Holding")
            version (str): Provide version information to remove incompatible elements.

        Notes on the definitions_list:
            - Must be sorted by ascending index
            - Each version may contain only one entry per register
            - The value of count must always be greater than or equal to 1
            - All names must be unique
        """
        self._name = name
        self._offset = offset
        self._version = version
        self._definitions = []
        self._lookup = LuxtronikDefinitionLookup()

    @classmethod
    def by_list(cls, definitions_list, name, offset=LUXTRONIK_DEFAULT_DEFINITION_OFFSET):
        obj = cls(name, offset)

        # Add definition objects only for valid items.
        # The correct sorting has already been ensured by the pytest
        for item in definitions_list:
            d = LuxtronikFieldDefinition(item, obj.name, obj.offset)
            if d.valid: # and version_in_range(version, d.since, d.until):
                obj._lookup.add(d)
        return obj

    @classmethod
    def empty(cls, definitions, version=None):
        obj = cls(definitions.name, definitions.offset)
        return obj

    @classmethod
    def versioned(cls, definitions, version=None):
        obj = cls(definitions.name, definitions.offset)

        # Add definition objects only for valid items.
        # The correct sorting has already been ensured by the pytest
        for d in definitions:
            if version_in_range(version, d.since, d.until):
                obj._lookup.add(d)
        return obj

    def __getitem__(self, name_or_idx):
        return self.get(name_or_idx)

    # def __len__(self):
    #     return len(self._definitions)

    def __iter__(self):
        """Iterator for all definitions contained herein."""
        return iter(self._definitions)

    def create_unknown_definition(self, index):
        return LuxtronikFieldDefinition.unknown(index, self._name, self._offset)

    def register_alias(self, def_name_or_idx, alias):
        definition = self._lookup.register_alias(def_name_or_idx, alias)
        definition.aliases.append(alias)

    @property
    def name(self):
        return self._name

    @property
    def offset(self):
        return self._offset

    # @property
    # def list(self):
    #     """
    #     Return the list of valid field definitions.

    #     Returns:
    #         list[LuxtronikFieldDefinition]: All valid definitions.
    #     """
    #     return self._definitions


    def get(self, name_or_idx): # , version=None):
        return self._lookup.get(name_or_idx)
        #return d if d is not None and version_in_range(version, d.since, d.until) else None

    def get_version_definitions(self):
        """
        Retrieve all definitions that represent version fields.

        Returns:
            list[LuxtronikFieldDefinition]: List of definitions whose data_type
            is either FullVersion or MajorMinorVersion.
        """
        version_definitions = []
        for d in self._definitions:
            if d.data_type in (FullVersion, MajorMinorVersion):
                version_definitions.append(d)
        return version_definitions



class LuxtronikFieldDictionary:
    """
    Container for Luxtronik field definitions.

    Provides lookup by index, name or alias.
    """

    def __init__(self, definitions, version=None):
        """
        Initialize the (by index sorted) field definitions.

        Args:
            definitions_list (list[dict]): Raw definition entries.
            offset (int): Offset applied to register indices.
                (Default: LUXTRONIK_DEFAULT_DEFINITION_OFFSET)
            name (str): Name of a field related to this definition list (e.g. "Holding")
            version (str): Provide version information to remove incompatible elements.

        Notes on the definitions_list:
            - Must be sorted by ascending index
            - Each version may contain only one entry per register
            - The value of count must always be greater than or equal to 1
            - All names must be unique
        """
        self._definitions = definitions
        self._version = version
        self._data = {}
        self._lookup = LuxtronikDefinitionLookup()

    @classmethod
    def empty(cls, definitions, version=None):
        obj = cls(definitions, version)
        return obj

    @classmethod
    def full(cls, definitions):
        obj = cls(definitions, None)
        for d in definitions:
            obj._add(d)
        return obj

    @classmethod
    def versioned(cls, definitions, version):
        obj = cls(definitions, version)
        for d in definitions:
            if version_in_range(version, d.since, d.until):
                obj.add(d)
        return obj

    def _add(definition, field, alias):
        self._lookup.add(definition, alias)
        self._data.set(definition, field)
        return field

    def _get_definition(self, def_field_name_or_idx):
        definition = def_field_name_or_idx
        field = None
        if isinstance(definition, Base):
            definition = def_field_name_or_idx.name
            field = def_field_name_or_idx
        if not isinstance(definition, LuxtronikFieldDefinition):
            definition = self._definitions.get(definition)
        return definition, field

    def add(self, def_field_name_or_idx, alias=None):
        definition, field = self._get_definition(def_field_name_or_idx)
        if (
            definition is not None
            and definition not in self._data
            and parse_version(self._version, definition.since, definition.until)
        ):
            if field is None:
                field = definition.create_field()
            return self._add(definition, field, alias)
        return None

    def __getitem__(self, def_name_or_idx):
        return self.get(def_name_or_idx)

    def __iter__(self):
        """Iterator for all definitions contained herein."""
        return iter(self._data)

    def __contains__(self, def_field_name_or_idx):
        if isinstance(def_field_name_or_idx, Base)
            return def_field_name_or_idx in self._data.values()
        else:
            return def_field_name_or_idx in self._lookup

    def register_alias(self, def_field_name_or_idx, alias):
        # Resolve a field input
        def_name_or_idx = def_field_name_or_idx
        if isinstance(def_name_or_idx, Base):
            def_name_or_idx = def_name_or_idx.name
        # register alias
        self._lookup.register_alias(def_name_or_idx, alias)

    def get(self, def_name_or_idx): # , version=None):
        """
        Retrieve a field definition by name or index.

        Args:
            name_or_idx (str | int): Field name or register index.

        Returns:
            Base | None: The matching definition, or None if not found.

        Note:
            If multiple definitions exist for the same index/name, the first one takes precedence.
        """
        if isinstance(def_name_or_idx, LuxtronikFieldDefinition):
            definition = def_name_or_idx
        else:
            definition = self._lookup.get(def_name_or_idx)
        if definition is not None:
            return self._data.get(definition, None)
        return None