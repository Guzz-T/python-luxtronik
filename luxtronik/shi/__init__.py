

from luxtronik.shi.constants import (
    LUXTRONIK_DEFAULT_MODBUS_PORT,
    LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
)
from luxtronik.shi.versions import (
    LUXTRONIK_LATEST_SHI_VERSION,
)
from luxtronik.shi.modbus import LuxtronikModbusTcpInterface
from luxtronik.shi.interface import LuxtronikSmartHomeInterface
from luxtronik.shi.versions import parse_version
from luxtronik.shi.inputs import INPUTS_DEFINITIONS


def determine_version(interface):

        # This is a little bit ugly, but we need the information of the definitions
        # to read out the version of the luxtronik controller.
        # Afterwards we can build a version-dependent-variant of the definitions,
        # that should be used within the smart-home-interface.
        # This works as long as the version-field has not changed.

        # Try to read the version of the luxtronik controller
        version_field = None
        version_defs = INPUTS_DEFINITIONS.get_version_definitions()
        for version_def in version_defs:
            data = modbus_interface.read_inputs(version_def.addr, version_def.count)
            if data is not None:
                version_field = version_def.create_field()
                version_field.raw = data
                return parse_version(version_field.value())
        return None


VERSION_DUMMY = "dummy"


def create_modbus_tcp(
    host,
    port = LUXTRONIK_DEFAULT_MODBUS_PORT,
    timeout_in_s = LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
    version = VERSION_DUMMY
):
    """
    Create a LuxtronikSmartHomeInterface using a Modbus TCP connection.

    Args:
        host (str): Hostname or IP address of the Luxtronik controller.
        port (int): TCP port for the Modbus connection.
        timeout_in_s (float): Timeout in seconds for the Modbus connection.
        version (tuple[int] | str | None): Version with which the interface should be initialized.
            If VERSION_DUMMY is used, an attempt is made to determine the version.
            If a string is passed, an attempt is made to use it as a version.
            If None is passed, one-after-another mode is activated.

    Returns:
        LuxtronikSmartHomeInterface: An initialized interface instance.
    """
    modbus_interface = LuxtronikModbusTcpInterface(host, port, timeout_in_s)
    if version == VERSION_DUMMY:
        version = determine_version(modbus_interface)
    elif isinstance(version, str):
        version = parse_version(version)
    return LuxtronikSmartHomeInterface(modbus_interface, version)


def create_modbus_tcp_latest(
    host,
    port = LUXTRONIK_DEFAULT_MODBUS_PORT,
    timeout_in_s = LUXTRONIK_DEFAULT_MODBUS_TIMEOUT
):
    return create_modbus_tcp(host, port, timeout_in_s, LUXTRONIK_LATEST_SHI_VERSION)