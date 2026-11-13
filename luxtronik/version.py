"""Methods and classes for supporting different firmware versions"""

from dataclasses import dataclass
import operator
from luxtronik.constants import (
    LUXTRONIK_VERSION_DETECT,
    LUXTRONIK_VERSION_LATEST,
    LUXTRONIK_VERSION_IGNORE,
    LUXTRONIK_LATEST_VERSION,
)

# List of valid operators.
# The longer operators (2 characters) must come BEFORE the shorter ones (1 character)
VALID_OPERATORS = (">=", "<=", "==", "!=", ">", "<")

# Mapping from string to python operator
OPERATORS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}
OPERATOR_TO_STR = {func: string for string, func in OPERATORS.items()}
VERSION_DELIMITER = "."
REQUIREMENT_DELIMITERS = [";", ","]

class DummyObjekt:
    def __repr__(self):
        return type(self).__name__

# Object to define that all version requirements are ignored
# Note: "None" acts like VER_IGNORE
class VER_IGNORE(DummyObjekt):
    pass
# Object to define that no version requirement will match
class VER_NONE(DummyObjekt):
    pass

###############################################################################
# Version methods
###############################################################################

def parse_version(version):
    """
    Parse a version string into a tuple with exactly 4 integers.
    The individual numbers correspond to `major.minor.patch.build`.
    A given tuple of integers is expanded or reduced to 4 integers.

    Examples:
        "1"         -> (1, 0, 0, 0)
        "2.1"       -> (2, 1, 0, 0)
        "3.2.1"     -> (3, 2, 1, 0)
        "1.2.3.4"   -> (1, 2, 3, 4)
        "1.2.3.4.5" -> (1, 2, 3, 4)   # extra parts are ignored
        "a.b"       -> None

    Args:
        version (str | tuple[int, ...]): Version string or version as tuple.

    Returns:
        tuple[int, int, int, int] | None: Parsed version tuple, or None if invalid.
    """
    if isinstance(version, tuple) and all(type(p) is int for p in version):
        return (version + (0, 0, 0, 0))[:4]
    elif isinstance(version, str):
        parts = version.strip().split(VERSION_DELIMITER)
        if not parts or any(not p.isdigit() for p in parts):
            return None
        nums = [int(p) for p in parts]
        nums = (nums + [0, 0, 0, 0])[:4]
        return tuple(nums)
    else:
        return None


def parse_version_requirement(requirement_str):
    """
    Parse a version requirement string into an operator and a tuple
    with exactly 4 integers (see parse_version()).

    Args:
        requirement_str (str): Version requirement as string (e.g. ">= 1.1").

    Returns:
        tuple[operator, tuple[int, int, int, int]] | tuple[None, None]: Parsed version requirement, or None if invalid.
    """
    if not isinstance(requirement_str, str):
        return None, None

    requirement_str = requirement_str.strip()
    op_func = None
    for op in VALID_OPERATORS:
        if requirement_str.startswith(op):
            requirement_str = requirement_str.replace(op, "").strip()
            op_func = OPERATORS[op]

            version_requirement = parse_version(requirement_str)
            return op_func, version_requirement
    return None, None


def version_fulfill_requirement(current_version, op_func, version_requirement):
    """
    Check whether a version fulfill a version requirement.
    If any argument is None, the check is skipped.

    Args:
        version (tuple[int, ...] | None): The version to check.
            If None, returns True.
        op_func (operator | None): The operator function related to the version requirement.
            If None, returns True.
        version_requirement (tuple[int, ...] | None): The version requirement to fulfill.
            If None, returns True.

    Returns:
        bool: True if version is within the range, False otherwise.
    """
    if current_version is VER_NONE:
        return False
    if current_version is None or current_version is VER_IGNORE \
            or op_func is None or version_requirement is None:
        return True
    return op_func(current_version, version_requirement)


def version_in_range(version, since=None, until=None):
    """
    Check whether a version is within the specified range of `[since..until]`.
    If an argument is None, the corresponding check is skipped.

    Args:
        version (tuple[int, ...] | None): The version to check.
            If None, returns True.
        since (tuple[int, ...] | None): Lower bound (inclusive).
            If None, no lower bound is applied.
        until (tuple[int, ...] | None): Upper bound (inclusive).
            If None, no upper bound is applied.

    Returns:
        bool: True if version is within the range, False otherwise.
    """
    return (version_fulfill_requirement(version, operator.ge, since)
        and version_fulfill_requirement(version, operator.le, until))


def get_version_str(version_tuple):
    return VERSION_DELIMITER.join(map(str, version_tuple))


def get_op_func_str(op):
    return OPERATOR_TO_STR[op] + " "


def get_since_requirement_str(version_str):
    return get_op_func_str(operator.ge) + version_str


def get_until_requirement_str(version_str):
    return get_op_func_str(operator.le) + version_str


@dataclass(frozen=True)
class VersionRequirement:
    op_func: callable
    version_requirement: tuple[int, ...]

    @classmethod
    def from_string(cls, requirement_str):
        """"
        Create an version requirement object out of a version requirement string.

        Args:
            requirement_str (str): Version requirement string (e.g. ">= 1.1")

        Returns:
            VersionRequirement: The created requirement object
        """
        op_func, version_requirement = parse_version_requirement(requirement_str)
        return cls(op_func, version_requirement)

    def matches(self, current_version):
        """"
        Check if a version fulfills the requirement represented by this object.
        Calls version_fulfill_requirement().

        Args:
            current_version (tuple[int, ...] | None): The version to check.

        Returns:
            bool: True if version fulfills this requirement.
        """
        return version_fulfill_requirement(current_version, self.op_func, self.version_requirement)

    def __str__(self):
        return get_op_func_str(self.op_func) + get_version_str(self.version_requirement)

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.op_func == other.op_func and self.version_requirement == other.version_requirement


@dataclass(frozen=True)
class VersionRequirements:
    requirements: list[VersionRequirement]

    @classmethod
    def from_list(cls, requirements_list, since=None, until=None):
        """"
        Create an version requirements list out of a version requirements string or list.

        Args:
            requirements_list (str | list[str]): Version requirements string
                (e.g. ">= 1.1,< 2.0" or "[">= 1.1", "< 2.0"])
            since (str | None): Optional version requirement since a specific version.
            until (str | None): Optional version requirement until a specific version.

        Returns:
            VersionRequirements: The created requirements object
        """
        if isinstance(requirements_list, str):
          for d in REQUIREMENT_DELIMITERS:
              requirements_list = requirements_list.replace(d, "#")
          requirements_list = requirements_list.split("#")

        if requirements_list is None:
            requirements_list = []
        if isinstance(since, str) and since:
            requirements_list += [get_since_requirement_str(since)]
        if isinstance(until, str) and until:
            requirements_list += [get_until_requirement_str(until)]

        requirements_list = [r for r in requirements_list if r]
        requirements = [VersionRequirement.from_string(r) for r in requirements_list]
        return cls(requirements)

    def matches(self, current_version):
        if current_version is VER_NONE:
            return False
        # True if requirements is empty
        return all(req.matches(current_version) for req in self.requirements)

    def __str__(self):
        return REQUIREMENT_DELIMITERS[0].join(map(str, self.requirements))

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        len_this = len(self.requirements)
        len_other = len(other.requirements)
        return len_this == len_other and all(self.requirements[i] == other.requirements[i] for i in range(len_this))


def resolve_version_input(version_input=LUXTRONIK_VERSION_DETECT):
    """
    Resolve the version input.

    Args:
        version_input (tuple[int] | str | None): This parameter defines what is returned:
            - LUXTRONIK_VERSION_DETECT sets the auto-detect-flag to True
            - LUXTRONIK_VERSION_LATEST returns the version tuple of the latest supported version
            - LUXTRONIK_VERSION_IGNORE sets the returned version to None
            - a str is parsed into a version tuple
            - a tuple is parsed into a version tuple
            - None behaves like LUXTRONIK_VERSION_IGNORE

    Returns:
        tuple[tuple[int] | None, bool]: The version of the controller to use,
            or None if no version could be parsed and a flag if we must
            determine the version automatically
    """
    if version_input is None:
        return VER_IGNORE, False
    elif isinstance(version_input, str):
        version_lower = version_input.lower()
        if version_lower == LUXTRONIK_VERSION_DETECT:
            # Set the second output parameter to True to start auto-detect
            return VER_NONE, True
        if version_lower == LUXTRONIK_VERSION_IGNORE:
            # Set the first output parameter to None to ignore the version
            return VER_IGNORE, False
        elif version_lower == LUXTRONIK_VERSION_LATEST:
            return LUXTRONIK_LATEST_VERSION, False

    resolved_version = parse_version(version_input)
    if resolved_version is None:
        # return VER_IGNORE in case of an error -> trial-and-error mode
        return VER_IGNORE, False
    return resolved_version, False
