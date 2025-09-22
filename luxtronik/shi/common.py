
###############################################################################
# Smart home telegrams
###############################################################################

class LuxtronikSmartHomeReadTelegram:
    """
    Represents a single smart home data field(s) read operation.

    A telegram encapsulates both the request parameters (`addr`, `count`)
    and the response data (`data`). It is primarily used to support
    list-based read operations.
    """

    def __init__(self, addr, count):
        """
        Initialize a read telegram.

        Args:
            addr (int): Starting register address to read from.
            count (int): Number of 16-bit registers to read.
        """
        self.addr = addr
        self.count = count
        self.prepare()

    def prepare(self):
        "Prepare the telegram for a (repeat) read operation"
        self.data = []

class LuxtronikSmartHomeReadHoldingsTelegram(LuxtronikSmartHomeReadTelegram):
    pass

class LuxtronikSmartHomeReadInputsTelegram(LuxtronikSmartHomeReadTelegram):
    pass


class LuxtronikSmartHomeWriteTelegram:
    """
    Represents a smart home data field(s) write operation.

    A write telegram encapsulates the request parameters (`addr`, `count`)
    and the payload (`data`). It is primarily used to support list-based
    write operations.
    """

    def __init__(self, addr, data):
        """
        Initialize a write telegram.

        Args:
            addr (int): Starting register address to write to.
            data (list[int]): Values to be written. If None or not a list,
                the telegram will be initialized with an empty payload.
        """
        self.addr = addr
        self.data = data
        self.prepare()

    def prepare(self):
        "Prepare the telegram for a (repeat) read operation"
        self.data = self.data if isinstance(self.data, list) else []
        self.count = len(self.data)

class LuxtronikSmartHomeWriteHoldingsTelegram(LuxtronikSmartHomeWriteTelegram):
    pass

LuxtronikSmartHomeTelegrams = (
    LuxtronikSmartHomeReadHoldingsTelegram,
    LuxtronikSmartHomeReadInputsTelegram,
    LuxtronikSmartHomeWriteHoldingsTelegram,
)


###############################################################################
# Helper classes for contiguous data
###############################################################################

class ContiguousDataPart:
    """
    Represents a single element of a contiguous data block.

    Each part references a `field` and its associated `definition`.
    See `ContiguousDataBlock` for further details.
    """

    def __init__(self, field, definition):
        """
        Initialize a contiguous data part.

        Args:
            field (Base): The field object to read or write.
            definition (LuxtronikFieldDefinition): The definition for this field.
        """
        self.field = field
        self.definition = definition

    def __str__(self):
        return f"({self.index}, {self.count})"

    @property
    def index(self):
        return self.definition.index

    @property
    def count(self):
        return self.definition.count


class ContiguousDataBlock:
    """
    Represents a contiguous block of data for efficient read/write access.

    Contiguous data fields are grouped into a single block to minimize
    the number of read/write operations. Each block links the raw data
    with the corresponding fields and definitions.

    Note:
        An invalid address or a non-existent register within a block
        will result in a transmission error.
    """

    def __init__(self):
        self._parts = []
        self._last = -1

    def __iter__(self):
        return iter(self._parts)

    def __getitem__(self, index):
        return self._parts[index]

    def __str__(self):
        parts_str = ", ".join(str(part) for part in self._parts)
        return f"ContiguousDataBlock(index={self.first_index}, count={self.overall_count}, parts=[{parts_str}])"

    def add(self, field, definition):
        """
        Add a subsequent part to this contiguous data block.
        We assume that the parts are added in order. Therefore, some special cases can be disregarded.

        Args:
            field (Base): The field associated with this part.
            definition (LuxtronikFieldDefinition): The definition associated with this part.

        Returns:
            bool: True if the part would not lead to gaps and is added to the block, otherwise False.
        """
        add_part = (self._last == -1) or ((definition.index >= self.first_index)
            and (definition.index <= self._last + 1))
        if add_part:
            self._parts.append(ContiguousDataPart(field, definition))
            self._last = max(self._last, definition.index + definition.count - 1)
        return add_part

    @property
    def first_index(self):
        """
        Return the first index of the block, or 0 if empty.
        This should be sufficient since the parts are added in index-sorted order.
        """
        return self._parts[0].index if self._parts else 0

    @property
    def overall_count(self):
        """Return the total number of contiguous registers in this block."""
        return self._last - self.first_index + 1

    def integrate_data(self, data_arr):
        """
        Integrate an array of registers into the raw values of the corresponding fields.

        Args:
            data_arr (list[int]): A list of register values.

        Returns:
            bool: True if the provided data length match `overall_count`.
        """
        valid = len(data_arr) == self.overall_count
        first = self.first_index
        if valid:
            for part in self._parts:
                offset = part.index - first
                part.field.raw = part.definition.extract_raw(data_arr, offset)
        return valid

    def get_data_arr(self):
        """
        Extract an array of registers from the raw values of the corresponding fields.

        Returns:
            list[int] | None: A list of register values if valid.
                              If multiple fields attempt to write to the same registers or
                              no data was provided for one or more elements, return None.

        Raises:
            AssertionError: If no data was provided for one or more elements.
        """
        data_arr = [-1] * self.overall_count
        first = self.first_index
        valid = True
        for part in self._parts:
            offset = part.index - first
            data = part.definition.get_raw(part.field)
            # Integrate data only if not already done (first data wins)
            if data_arr[offset] == -1 and data is not None:
                data_arr[offset : offset +  part.count] = data
            else:
                valid = False
        valid &= -1 not in data_arr
        return data_arr if valid else None


class ContiguousDataBlocksHandler:
    """
    Manages a collection of contiguous data blocks.

    Contiguous data blocks group adjacent registers together
    to minimize the number of read/write operations.
    """

    def __init__(self):
        self._blocks = []
        self._start_idx = -1
        self._next_index = -1
        self._telegrams = []
        self._items = []

    def collect(self, field, definition):
        """
        Correctly add a field definition to the list of contiguous blocks.
        Assumes that definitions are sorted by index (see LuxtronikFieldDefinitions).

        Args:
            field (Base): The field associated with this part.
            definition (LuxtronikFieldDefinition): The definition associated with this part.
        """
        index = definition.index
        count = definition.count if definition.count > 0 else 1

        # Create a new contiguous block if the current index doesn't follow the previous
        # or is already covered by the current block. Since we assume a index-sorted order,
        # we can ignore special cases.
        if (index < self._start_idx) or (index > self._next_index):
            self._blocks.append(ContiguousDataBlock())
            self._start_idx = index

        # Add the field and definition to the current block.
        # Hint: The part should always be add-able. Therefor an assertion is be fine here.
        added = self._blocks[-1].add(field, definition)
        assert added, "Could not collect the field/definition pair as part"
        self._next_index = max(index + count, self._next_index)
        return added

    @property
    def get_block_list(self):
        return self._blocks

    def create_read_telegrams(self, offset):
        """
        Create read telegrams for all blocks.

        Args:
            offset (int): Address offset to apply to each block's index.

        Returns:
            list[LuxtronikSmartHomeReadTelegram]: A list of LuxtronikSmartHomeReadTelegram objects.
        """
        self._telegrams = []
        self._items = []
        for block in self._blocks:
            addr = block.first_index + offset
            count = block.overall_count
            telegram = LuxtronikSmartHomeReadTelegram(addr, count)
            self._telegrams.append(telegram)
            self._items.append((block, telegram))
        return self._telegrams

    def create_write_telegrams(self, offset):
        """
        Create write telegrams for all blocks.

        Args:
            offset (int): Address offset to apply to each block's index.

        Returns:
            list[LuxtronikSmartHomeWriteTelegram]: A list of LuxtronikSmartHomeWriteTelegram objects.
        """
        self._telegrams = []
        self._items = []
        for block in self._blocks:
            addr = block.first_index + offset
            data_arr = block.get_data_arr()
            # Skip block if the data to write is not valid
            if data_arr is not None:
                telegram = LuxtronikSmartHomeWriteTelegram(addr, data_arr)
                self._telegrams.append(telegram)
                self._items.append((block, telegram))
        return self._telegrams

    def integrate_data(self):
        """
        Integrate the read data from telegrams back into the corresponding blocks.
        'create_read_telegrams' must be called up beforehand

        Returns:
            bool: True if all data could be integrated.
        """
        valid = True
        for block, telegram in self._items:
            valid &= block.integrate_data(telegram.data)
        return valid