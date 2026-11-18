"""
Python module for controlling a Luxtronik heat pump controller
via the smart home interface. Powered by Guzz-T.
"""

import logging

from luxtronik.constants import LUXTRONIK_VERSION_DETECT
from luxtronik.shi.constants import (
    LUXTRONIK_DEFAULT_MODBUS_PORT,
    LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
)
from luxtronik.shi.inputs import INPUTS_DEFINITIONS, Inputs  # noqa: F401
from luxtronik.shi.holdings import HOLDINGS_DEFINITIONS, Holdings  # noqa: F401
from luxtronik.shi.modbus import LuxtronikModbusTcpInterface
from luxtronik.shi.interface import LuxtronikSmartHomeData, LuxtronikSmartHomeInterface  # noqa: F401


LOGGER = logging.getLogger(__name__)


###############################################################################
# Factory methods
###############################################################################

def create_modbus_tcp(
    host,
    port=LUXTRONIK_DEFAULT_MODBUS_PORT,
    timeout=LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
    version=LUXTRONIK_VERSION_DETECT
):
    """
    Create a LuxtronikSmartHomeInterface using a Modbus TCP connection.

    The function constructs a Modbus TCP low-level interface and resolves the
    controller version according to the supplied `version` argument:
      - If `version` equals LUXTRONIK_VERSION_DETECT, attempt to determine the version.
      - If `version` equals LUXTRONIK_VERSION_LATEST, use LUXTRONIK_LATEST_VERSION as version.
      - If `version` is a string, parse it into a version tuple.
      - If `version` equals LUXTRONIK_VERSION_IGNORE, the interface is initialized
          in trial-and-error mode (= ignore version requirements).
      - None behave like LUXTRONIK_VERSION_IGNORE.
      - Otherwise assume `version` is already a parsed version tuple.
      - For any other input, it behaves the same way as with LUXTRONIK_VERSION_IGNORE.

    Args:
        host (str): Hostname or IP address of the Luxtronik controller.
        port (int): TCP port for the Modbus connection.
        timeout (float): Timeout in seconds for the Modbus connection.
        version (tuple[int] | str | None): Version used to initialize the interface.
            For an explanation, see what's written above.

    Returns:
        LuxtronikSmartHomeInterface:
            Initialized interface instance bound to the Modbus TCP connection.
    """
    modbus_interface = LuxtronikModbusTcpInterface(host, port, timeout)
    LOGGER.info(f"Create smart home interface via modbus-TCP on {host}:{port}"
        + f" for version {version}")
    return LuxtronikSmartHomeInterface(modbus_interface, version)
