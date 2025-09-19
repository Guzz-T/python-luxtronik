from luxtronik.constants import LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE

###############################################################################
# Smart home telegrams
###############################################################################

class LuxtronikSmartHomeReadTelegram:
    """
    Represents a single smart home data field read operation.

    A telegram encapsulates both the request parameters (`addr`, `count`)
    and the response data (`data`). It is primarily used to support
    list‑based read operations.
    """

    def __init__(self, addr, count):
        """
        Initialize a read telegram.

        Args:
            addr (int): Starting register address to read from.
            count (int): Number of 16‑bit registers to read.
        """
        self.addr = addr
        self.count = count
        self.data = []

    def normalize_data(self):
        """
        Ensure that `self.data` is a list of exactly `self.count` elements.
        Missing values are filled with `LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE`,
        and excess values are truncated.

        Returns:
            bool: True if the original data was valid (list of correct length),
                  False otherwise.
        """
        data = self.data if isinstance(self.data, list) else None
        length = len(data) if data is not None else 0
        valid = data is not None and length == self.count

        if data is None:
            self.data = [LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE] * self.count
        elif length < self.count:
            self.data += [LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE] * (self.count - length)
        elif length > self.count:
            self.data = data[:self.count]

        return valid


class LuxtronikSmartHomeWriteTelegram:
    """
    Represents a smart home data field write operation.

    A write telegram encapsulates the request parameters (`addr`, `count`)
    and the payload (`data`). It is primarily used to support list‑based
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
        self.data = data if isinstance(data, list) else []
        self.count = len(self.data)


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
        An invalid address or a non‑existent register within a block
        will result in a transmission error.
    """

    def __init__(self):
        self._parts = []

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

        Args:
            field (Base): The field associated with this part.
            definition (LuxtronikFieldDefinition): The definition associated with this part.
        """
        if self._parts:
            assert (
                self._parts[-1].index + self._parts[-1].count == definition.index
            ), "Added data part is not contiguous!"
        self._parts.append(ContiguousDataPart(field, definition))

    @property
    def first_index(self):
        """Return the first index of the block, or 0 if empty."""
        return self._parts[0].index if self._parts else 0

    @property
    def overall_count(self):
        """Return the total number of contiguous registers in this block."""
        return sum(part.count for part in self._parts)

    def integrate_data(self, data_arr):
        """
        Integrate an array of registers into the raw values of the corresponding fields.

        Args:
            data_arr (list[int]): A list of register values.

        Raises:
            AssertionError: If the provided data length does not match `overall_count`.
        """
        assert len(data_arr) == self.overall_count, "Incorrect length of the provided data."
        first = self.first_index
        for part in self._parts:
            offset = part.index - first
            part.field.raw = part.definition.extract_raw(data_arr, offset)

    def get_data_arr(self):
        """
        Extract an array of registers from the raw values of the corresponding fields.

        Returns:
            list[int]: A list of register values.

        Raises:
            AssertionError: If the generated data length does not match `overall_count`.
        """
        data_arr = []
        for part in self._parts:
            data_arr.extend(part.definition.get_raw(part.field))
        assert len(data_arr) == self.overall_count, "Incorrect length of the assigned data."
        return data_arr


class ContiguousDataBlocksHandler:
    """
    Manages a collection of contiguous data blocks.

    Contiguous data blocks group adjacent registers together
    to minimize the number of read/write operations.
    """

    def __init__(self):
        self._blocks = []
        self._next_index = -1
        self._telegrams = []
        self._items = []

    def collect(self, field, definition):
        """
        Correctly add a field definition to the list of contiguous blocks.

        Args:
            field (Base): The field associated with this part.
            definition (LuxtronikFieldDefinition): The definition associated with this part.
        """
        index = definition.index
        count = definition.count

        # Create a new contiguous block if the current index doesn't follow the previous
        if index != self._next_index:
            self._blocks.append(ContiguousDataBlock())

        # Warn if definitions are not in ascending order
        if index < self._next_index:
            LOGGER.warning(
                f"Field {definition.name} at index {index} is not inserted in ascending order."
            )

        # Add the field and definition to the current block
        self._blocks[-1].add(field, definition)
        self._next_index = index + count

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
        for block in self._blocks:
            addr = block.first_index + offset
            data_arr = block.get_data_arr()
            telegram = LuxtronikSmartHomeWriteTelegram(addr, data_arr)
            self._telegrams.append(telegram)
            self._items.append((block, telegram))
        return self._telegrams

    def integrate_data(self):
        """
        Integrate the read data from telegrams back into the corresponding blocks.
        """
        for block, telegram in self._items:
            block.integrate_data(telegram.data)