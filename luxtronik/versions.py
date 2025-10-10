
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


# First Luxtronik firmware version that supports the Smart Home Interface (SHI)
LUXTRONIK_FIRST_VERSION_WITH_SHI = parse_version("3.90.1")

LUXTRONIK_LATEST_SHI_VERSION = parse_version("3.92.0")