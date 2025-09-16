###############################################################################
# Smart home telegrams
###############################################################################

class LuxtronikSmartHomeReadTelegram:
    """
    Wrapper around all data of a smart home data field read operation.
    This includes the request data ('addr', 'count') as well as the response data (data).
    It is mainly used to implement a list-read function.
    """

    def __init__(self, addr, count):
        self.addr = addr
        self.count = count
        self.data = []

class LuxtronikSmartHomeWriteTelegram:
    """
    Wrapper around all data of a smart home data field write operation.
    This consists only of the request data ('addr', 'count', 'data').
    It is mainly used to implement a list-write function.
    """

    def __init__(self, addr, data):
        self.addr = addr
        if data is None or not isinstance(data, list):
            self.count = 0
            self.data = []
        else:
            self.count = len(data)
            self.data = data


###############################################################################
# Helper classes for contiguous data
###############################################################################

class ContiguousDataPart:
    """
    Single element of a contiguous data block.
    See 'ContiguousDataBlock' for further information.
    """

    def __init__(self, field, definition):
        self.field = field
        self.definition = definition

    def __str__(self):
        return f"({self.definition.index}, {self.definition.count})"

    @property
    def index(self):
        return self.definition.index

    @property
    def count(self):
        return self.definition.count

class ContiguousDataBlock:
    """
    To reduce the number of accesses, contiguous data are written/read together as a 'block'.
    This class is used to link the read/written data with the individual fields and definitions.
    Note: An invalid address or a non-existent register within a block leads to a transmission error.
    """

    def __init__(self):
        self._part_list = []

    def __iter__(self):
        return iter(self._part_list)

    def __getitem__(self, index):
        return self._part_list[index]

    def __str__(self):
        block_str = ""
        for part in self._part_list:
            block_str += f" {part},"
        block_str = "[" + block_str[1:-1] + "]"
        return f"index: {self.first_index}, count: {self.overall_count}, parts: {block_str}"

    def add(self, field, definition):
        """
        Add a subsequent part to this contiguous data block.
        """
        if len(self._part_list) > 0:
            assert self._part_list[-1].index + self._part_list[-1].count == definition.index, """
                Added data part is not contiguous!"""
        part = ContiguousDataPart(field, definition)
        self._part_list += [part]

    @property
    def first_index(self):
        """
        Returns the first index of the list. Returns '0' if empty.
        """
        if len(self._part_list) > 0:
            return self._part_list[0].index
        else:
            return 0

    @property
    def overall_count(self):
        """
        Returns the overall count of contiguous bytes/words.
        """
        count = 0
        for part in self._part_list:
            count += part.count
        return count

    def integrate_data(self, data_arr):
        assert len(data_arr) == self.overall_count, "Incorrect length of the provided data."
        first = self.first_index
        for part in self._part_list:
            offset = part.index - first
            part.field.raw = part.definition.extract_raw(data_arr, offset)

    def get_data_arr(self):
        data_arr = []
        for part in self._part_list:
            data_arr += part.definition.get_raw(part.field)
        assert len(data_arr) == self.overall_count, "Incorrect length of the assigned data."
        return data_arr