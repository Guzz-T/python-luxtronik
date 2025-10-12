import logging

LOGGER = logging.getLogger("Luxtronik.SmartHomeInterface")

###############################################################################
# Version methods
###############################################################################
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

LuxtronikSmartHomeTelegrams = {
    LuxtronikSmartHomeReadHoldingsTelegram,
    LuxtronikSmartHomeReadInputsTelegram,
    LuxtronikSmartHomeWriteHoldingsTelegram,
}
