import logging

from luxtronik.datatypes import Unknown


LOGGER = logging.getLogger("Luxtronik.definitions")

LUXTRONIK_DEFAULT_DEFINITION_OFFSET = 10000


def parse_version(version):
    """
    Parse a version string into a tuple of exactly 4 integers.

    Examples:
        "1"         -> (1, 0, 0, 0)
        "2.1"       -> (2, 1, 0, 0)
        "3.2.1"     -> (3, 2, 1, 0)
        "1.2.3.4"   -> (1, 2, 3, 4)
        "1.2.3.4.5" -> (1, 2, 3, 4)   # extra parts are ignored
        "a.b"       -> None

    Args:
        version (str): Version string.

    Returns:
        tuple[int, int, int, int] | None: Parsed version tuple, or None if invalid.
    """
    try:
        parts = version.strip().split(".")
        if not parts or any(not p.isdigit() for p in parts):
            return None
        nums = [int(p) for p in parts]
        nums = (nums + [0, 0, 0, 0])[:4]
        return tuple(nums)
    except Exception:
        return None

def version_in_range(version, since=None, until=None):
    """
    Check if a version is within the given range.

    Args:
        version (tuple[int, ...]): The version to check.
        since (tuple[int, ...] | None): Lower bound (inclusive). If None, no lower bound is applied.
        until (tuple[int, ...] | None): Upper bound (inclusive). If None, no upper bound is applied.

    Returns:
        bool: True if version is within the range, False otherwise.
    """
    if version is None:
        return True
    if since is not None and version < since:
        return False
    if until is not None and version > until:
        return False
    return True


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


class LuxtronikFieldDefinitions:
    """
    Container for Luxtronik field definitions.

    Provides lookup by index or name.
    """

    def __init__(self, definitions_list, name, offset=LUXTRONIK_DEFAULT_DEFINITION_OFFSET, version=None):
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
        self._version = parse_version(version)
        self._list = definitions_list

        definitions = []
        # Create definition objects only for valid items
        for item in definitions_list:
            d = LuxtronikFieldDefinition(item, self._name, self._offset)
            if d.valid and version_in_range(version, d.since, d.until):
                definitions.append(d)
        self._definitions = sorted(definitions, key=lambda x: x.index)

        # Dictionary mapping indices to definitions (first occurrence wins)
        self._index_dict = {}
        for d in self._definitions:
            self._index_dict.setdefault(d.index, d)

        # Dictionary mapping names to definitions (first occurrence wins)
        self._name_dict = {}
        for d in self._definitions:
            for n in d.names:
                self._name_dict.setdefault(n.lower(), d)

    def refine(self, version):
        return cls(self._list, self._name, self._offset, version)

    def __getitem__(self, name_or_idx):
        return self.get(name_or_idx)

    # def __len__(self):
    #     return len(self._definitions)

    def __iter__(self):
        """Iterator for all definitions contained herein."""
        return iter(self._definitions)

    def create_unknown_field(self, index):
        return LuxtronikFieldDefinition.unknown(index, self._name, self._offset)

    @property
    def name(self):
        return self._name

    @property
    def offset(self):
        return self._offset

    @property
    def list(self):
        """
        Return the list of valid field definitions.

        Returns:
            list[LuxtronikFieldDefinition]: All valid definitions.
        """
        return self._definitions

    def get(self, name_or_idx):
        """
        Retrieve a field definition by name or index.

        Args:
            name_or_idx (str | int): Field name or register index.

        Returns:
            LuxtronikFieldDefinition: The matching definition, or an invalid one if not found.

        Note:
            If multiple definitions exist for the same index/name, the first one takes precedence.
        """
        if isinstance(name_or_idx, int):
            return self._get_definition_by_idx(name_or_idx)
        if isinstance(name_or_idx, str):
            try:
                idx_from_str = int(target)
                return self._get_definition_by_idx(name_or_idx)
            except ValueError:
                return self._get_definition_by_name(name_or_idx)
        return LuxtronikFieldDefinition.invalid()

    def _get_definition_by_idx(self, idx):
        """
        Retrieve a field definition by its index.

        Args:
            idx (int): Register index.

        Returns:
            LuxtronikFieldDefinition: The matching definition, or an invalid one if not found.

        Note:
            If multiple definitions exist for the same index, the first one takes precedence.
        """
        return self._index_dict.get(idx, LuxtronikFieldDefinition.invalid())

    def _get_definition_by_name(self, name):
        """
        Retrieve a field definition by its name (case-insensitive).

        Args:
            name (str): Field name.

        Returns:
            LuxtronikFieldDefinition: The matching definition, or an invalid one if not found.

        Note:
            If multiple definitions exist for the same name, the first one takes precedence.
        """
        definition = self._name_dict.get(name.lower(), LuxtronikFieldDefinition.invalid())
        if definition.valid and name.lower() != definition.name.lower():
            LOGGER.warning(f"'{name}' is outdated! Use '{definition.name}' instead.")
        return definition

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

    def create_field_dict(self):
        """
        Create a dictionary mapping definitions to newly created field objects.

        Returns:
            dict[LuxtronikFieldDefinition, Base]: Mapping of definitions to field instance.
        """
        return {d: d.create_field() for d in self._definitions}
