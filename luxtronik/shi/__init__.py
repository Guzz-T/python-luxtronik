
from luxtronik.datatypes import FullVersion, MajorMinorVersion
from luxtronik.shi.constants import (
    LUXTRONIK_DEFAULT_MODBUS_PORT,
    LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
    LUXTRONIK_LATEST_SHI_VERSION,
)
from luxtronik.shi.common import LOGGER, parse_version
from luxtronik.shi.inputs import INPUTS_DEFINITIONS
from luxtronik.shi.modbus import LuxtronikModbusTcpInterface
from luxtronik.shi.interface import LuxtronikSmartHomeInterface

VERSION_DETECT = "detect"
VERSION_LATEST = "latest"


###############################################################################
# Helper methods
###############################################################################

def get_version_definitions(definitions):
    """
    Retrieve all definitions that represent version fields.

    Args:
        definitions (LuxtronikDefinitionsList): List of definitions

    Returns:
        list[LuxtronikFieldDefinition]: List of definitions whose data_type
        is either FullVersion or MajorMinorVersion.
    """
    version_definitions = []
    for d in definitions:
        if d.data_type in (FullVersion, MajorMinorVersion):
            version_definitions.append(d)
    return version_definitions

def determine_version(interface):
    """
    Determine the version of the luxtronik controller.

    This is a little bit ugly! The controller version is required
    to locate the version field. As workaround, probe each known
    version field until one yields a valid read and a parsable version.
    This approach works as long as the version-field has not changed.

    Args:
        interface (LuxtronikModbusTcpInterface):
            Simple read/write interface to read out the version.

    Returns:
        tuple[int] | None: The version of the controller on success,
            or None if no version could be determined.
    """
    definitions = get_version_definitions(INPUTS_DEFINITIONS)
    for definition in definitions:
        data = interface.read_inputs(definition.addr, definition.count)
        if data is not None:
            field = definition.create_field()
            field.raw = data
            parsed = parse_version(field.value)
            if parsed is not None:
                return parsed
    LOGGER.warning("It was not possible to determine the controller version. Switch to trial-and-error mode.")
    return None


###############################################################################
# Factory methods
###############################################################################

def create_modbus_tcp(
    host,
    port=LUXTRONIK_DEFAULT_MODBUS_PORT,
    timeout_in_s=LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
    version=VERSION_DETECT
):
    """
    Create a LuxtronikSmartHomeInterface using a Modbus TCP connection.

    The function constructs a Modbus TCP low-level interface and resolves the
    controller version according to the supplied `version` argument:
      - If `version` equals VERSION_DETECT, attempt to determine the version by probing the controller.
      - If `version` equals VERSION_LATEST, use LUXTRONIK_LATEST_SHI_VERSION as version.
      - If `version` is a string, parse it into a version tuple.
      - If `version` is None, the interface is initialized in trial-and-error mode.
      - Otherwise assume `version` is already a parsed version tuple.

    Args:
        host (str): Hostname or IP address of the Luxtronik controller.
        port (int): TCP port for the Modbus connection.
        timeout_in_s (float): Timeout in seconds for the Modbus connection.
        version (tuple[int] | str | None): Version used to initialize the interface.
            If VERSION_DETECT is passed, the function will attempt to determine the version.
            If a str is passed, the string will be parsed into a version tuple.
            If None is passed, trial-and-error mode is activated.

    Returns:
        LuxtronikSmartHomeInterface: Initialized interface instance bound to the Modbus TCP connection.
    """
    modbus_interface = LuxtronikModbusTcpInterface(host, port, timeout_in_s)

    resolved_version = version
    if resolved_version == VERSION_DETECT:
        # return None in case of an error -> trial-and-error mode
        resolved_version = determine_version(modbus_interface)
    elif isinstance(resolved_version, str):
        if resolved_version.lower() == VERSION_LATEST:
            resolved_version = LUXTRONIK_LATEST_SHI_VERSION
        else:
            # return None in case of an error -> trial-and-error mode
            resolved_version = parse_version(resolved_version)

    LOGGER.info(f"Create smart-home-interface via modbus-TCP on {host}:{port} for version {resolved_version}")
    return LuxtronikSmartHomeInterface(modbus_interface, resolved_version)