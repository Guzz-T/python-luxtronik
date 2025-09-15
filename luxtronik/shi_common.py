###############################################################################
# Smart home telegrams
###############################################################################

class LuxtronikSmartHomeReadTelegram:

    def __init__(self, addr, count):
        self.addr = addr
        self.count = count
        self.data = []

class LuxtronikSmartHomeWriteTelegram:

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

class ContiguousBlockData:

    def __init__(self, index, count, field, definition, data_arr):
        self.index = index
        self.count = count
        self.field = field
        self.definition = definition
        self.data_arr = data_arr

    def __str__(self):
        return f"({self.index}, {self.count})"

class ContiguousBlock:

    def __init__(self):
        self._contiguous_list = []

    def __iter__(self):
        return iter(self._contiguous_list)

    def __str__(self):
        list_str = ""
        for entry in self._contiguous_list:
            list_str += f" {entry},"
        list_str = "[" + list_str[1:-1] + "]"
        return f"index: {self.first_index}, count: {self.overall_count}, list: {list_str}"

    def add(self, index, count, field, definition, data_arr=[None]):
        entry = ContiguousBlockData(index, count, field, definition, data_arr)
        self._contiguous_list += [entry]

    @property
    def first_index(self):
        if len(self._contiguous_list) > 0:
            return self._contiguous_list[0].index
        else:
            return 0

    @property
    def overall_count(self):
        count = 0
        for entry in self._contiguous_list:
            count += entry.count
        return count

    def integrate_data(self, data_arr):
        first = self.first_index
        for entry in self._contiguous_list:
            offset = entry.index - first
            entry.field.raw = entry.definition.extract_raw(data_arr, offset)

    def get_data_arr(self):
        data_arr = []
        for entry in self._contiguous_list:
            data_arr += entry.data_arr
        return data_arr