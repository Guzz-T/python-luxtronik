from luxtronik.shi.constants import (
    HOLDINGS_FIELD_NAME,
    INPUTS_FIELD_NAME,
)
from luxtronik.shi.common import (
    LOGGER,
    parse_version,
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

    def __init__(self, definition, field):
        """
        Initialize a contiguous data part.

        Args:
            field (Base): The field object to read or write.
            definition (LuxtronikFieldDefinition): The definition for this field.
        """
        self.field = field
        self.definition = definition

    def __repr__(self):
        return f"({self.index}, {self.count})"

    @property
    def index(self):
        return self.definition.index

    @property
    def addr(self):
        return self.definition.addr

    @property
    def count(self):
        return self.definition.count


class ContiguousDataBlock:
    """
    Represents a contiguous block of fields for efficient read/write access.

    Contiguous fields of same type are grouped into a single block to minimize
    the number of read/write operations. Each block links the raw data
    with the corresponding fields and definitions.

    Note:
        An invalid address or a non-existent register within a block
        will result in a transmission error.
    """

    def __init__(self):
        self._parts = []
        self._last_idx = -1

    @classmethod
    def create_and_add(cls, definition, field):
        obj = cls()
        obj.add(definition, field)
        return obj

    def clear(self):
        self._parts = []
        self._last_idx = -1

    def __iter__(self):
        return iter(self._parts)

    def __getitem__(self, index):
        return self._parts[index]

    def __str__(self):
        parts_str = ", ".join(str(part) for part in self._parts)
        return f"(index={self.first_index}, count={self.overall_count}, " \
            + f"parts=[{parts_str}])"

    def can_add(self, definition):
        """
        Check if the next part can be added to this contiguous data block.

        Returns:
            bool: True if the part would not lead to gaps and can be added to this block, otherwise False.
        """
        return (
            self._last_idx == -1
            or (
                definition.index >= self.first_index
                and definition.index <= self._last_idx + 1
            )
        )

    def add(self, definition, field):
        """
        Add a subsequent part to this contiguous data block.
        We assume that the (valid) parts are added in order.
        Therefore, some special cases can be disregarded.
        Call `can_add` previously.

        Args:
            field (Base): The field associated with this part.
            definition (LuxtronikFieldDefinition): The definition associated with this part.
        """
        self._parts.append(ContiguousDataPart(definition, field))
        self._last_idx = max(self._last_idx, definition.index + definition.count - 1)

    @property
    def first_index(self):
        """
        Return the first index of the block, or 0 if empty.
        This should be sufficient since the (valid) parts are added in index-sorted order.
        """
        return self._parts[0].index if self._parts else 0

    @property
    def first_addr(self):
        """
        Return the first addr of the block, or 0 if empty.
        This should be sufficient since the (valid) parts are added in index-sorted order.
        """
        return self._parts[0].addr if self._parts else 0

    @property
    def overall_count(self):
        """Return the total number of contiguous registers in this block."""
        return self._last_idx - self.first_index + 1 if self._parts else 0

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
                data_offset = part.index - first
                part.field.raw = part.definition.extract_raw(data_arr, data_offset)
        else:
            LOGGER.error(
                f"Data to integrate not valid! Expected a length of '{self.overall_count}'",
                f" but got '{len(data_arr)}': data = {data_arr}, block = {self}"
            )
        return valid

    def get_data_arr(self):
        """
        Extract an array of registers from the raw values of the corresponding fields.

        Returns:
            list[int] | None: A list of register values if valid.
                              If multiple fields attempt to write to the same registers or
                              no data was provided for one or more elements, return None.
        """
        data_arr = [-1] * self.overall_count
        first = self.first_index
        valid = True
        for part in self._parts:
            data_offset = part.index - first
            data = part.definition.get_raw(part.field)
            # Integrate data only if not already done (first data wins)
            if data_arr[data_offset] == -1 and data is not None:
                data_arr[data_offset : data_offset +  part.count] = data
            else:
                valid = False
                LOGGER.error(
                    f"Got multiple or invalid data to write for a single register! part = {part},",
                    f" first data = {data_arr[data_offset]}, second data = {data}"
                )
        valid &= -1 not in data_arr
        return data_arr if valid else None

    def _create_read_telegram(self, telegram_type):
        """
        Create a read-telegram of type `telegram_type` out of this `ContiguousDataBlock`.

        Args:
            telegram_type (class of LuxtronikSmartHomeReadTelegram):
                Type of the telegram to create.

        Returns:
            LuxtronikSmartHomeReadTelegram:
                The created telegram.
        """
        return telegram_type(self.first_addr, self.overall_count)

    def _create_write_telegram(self, telegram_type):
        """
        Create a write-telegram of type `telegram_type` out of this `ContiguousDataBlock`.

        Args:
            telegram_type (class of LuxtronikSmartHomeWriteTelegram):
                Type of the telegram to create.

        Returns:
            LuxtronikSmartHomeWriteTelegram | None:
                The created telegram or None in case of an error.
        """
        data_arr = self.get_data_arr()
        if data_arr is None:
            LOGGER.error(f"Failed to create a {telegram_type} telegram! The provided data is not valid.")
            return None
        return telegram_type(self.first_addr, data_arr)

    def create_telegram(self, type_name, read_not_write):
        """
        Create a read or write-telegram out of this `ContiguousDataBlock`.

        Returns:
            LuxtronikSmartHomeReadTelegram | LuxtronikSmartHomeWriteTelegram | None:
                The created telegram or None in case of an error.
        """
        if type_name == HOLDINGS_FIELD_NAME and read_not_write:
            return self._create_read_telegram(LuxtronikSmartHomeReadHoldingsTelegram)
        if type_name == INPUTS_FIELD_NAME and read_not_write:
            return self._create_read_telegram(LuxtronikSmartHomeReadInputsTelegram)
        if type_name == HOLDINGS_FIELD_NAME and not read_not_write:
            return self._create_write_telegram(LuxtronikSmartHomeWriteHoldingsTelegram)
        LOGGER.error(f"Could not create a telegram for {self}. Skip this operation.")
        return None


class ContiguousDataBlockList:

    def __init__(self, type_name, read_not_write):
        self._blocks = []
        self._type_name = type_name
        self._read_not_write = read_not_write

    def clear(self):
        self._blocks = []

    def __iter__(self):
        return iter(self._blocks)

    def __getitem__(self, index):
        return self._blocks[index]

    def __str__(self):
        blocks_str = ", ".join(str(block) for block in self._blocks)
        return f"(type_name={self._type_name}, read_not_write={self._read_not_write}, " \
            + f"blocks=[{blocks_str}])"

    @property
    def type_name(self):
        return self._type_name

    @property
    def read_not_write(self):
        return self._read_not_write

    def collect(self, definition, field):
        """
        Correctly add a part to the list of contiguous blocks.
        Assumes that definitions are sorted by index (see LuxtronikDefinitionsList).

        Args:
            field (Base): The field associated with this part.
            definition (LuxtronikFieldDefinition): The definition associated with this part.
        """
        index = definition.index
        count = definition.count if definition.count > 0 else 1

        # Create a new contiguous block if the current part cannot be added to the last one.
        if len(self._blocks) == 0 or not self._blocks[-1].can_add(definition):
            self._blocks.append(ContiguousDataBlock())

        # Add the field and definition to the (newly created) last data block.
        self._blocks[-1].add(definition, field)

    def append(self, block):
        self._block.append(block)

    def append_single(self, definition, field):
        self._block.append(ContiguousDataBlock.create_and_add(definition, field))

    def create_telegrams(self, type_name, read_not_write):
        """
        Create a read or write-telegram out of this `ContiguousDataBlock`.

        Returns:
            LuxtronikSmartHomeReadTelegram | LuxtronikSmartHomeWriteTelegram | None:
                The created telegram or None in case of an error.
        """
        return [block.create_telegram(type_name, read_not_write) for block in self._blocks]


class ContiguousDataBlocksHandler:
    """
    Manages a collection of contiguous data blocks.

    Contiguous data blocks group adjacent registers together
    to minimize the number of read/write operations.
    """

    def __init__(self):
        self._blocks_list = []
        self._next_idx = -1
        self._telegrams = []
        self._read_list = []
        self._write_list = []

    def clear(self):
        self._blocks_list = []
        self._next_idx = -1
        self._telegrams = []
        self._read_list = []
        self._write_list = []

    @property
    def get_blocks_list(self):
        return self._blocks_list

    def append(self, blocks):
        self._blocks_list.append(blocks)

    def create_telegrams(self):
        """
        Create telegrams for all blocks.

        Returns:
            list[LuxtronikSmartHomeReadTelegram | LuxtronikSmartHomeWriteTelegram]:
                A list of read and/or write telegrams.
        """
        self._telegrams = []
        self._read_list = []
        self._write_list = []
        for blocks in self._blocks_list:
            for block in blocks:
                telegram = block.create_telegram(blocks.type_name, blocks.read_not_write)
                if telegram is not None:
                    self._telegrams.append(telegram)
                    if blocks.read_not_write:
                        self._read_list.append((block, telegram))
                    else:
                        self._write_list.append((block, telegram))
        return self._telegrams

    def integrate_data(self):
        """
        Integrate the read data from telegrams back into the corresponding blocks.
        'create_read_telegrams' must be called up beforehand

        Returns:
            bool: True if all data could be integrated.
        """
        success = True
        for block, telegram in self._read_list:
            valid = block.integrate_data(telegram.data)
            if not valid:
                LOGGER.error('Failed to integrate read data into {block}')
            success &= valid
        return success