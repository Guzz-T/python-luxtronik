"""Constants used throughout the Luxtronik Smart Home Interface (SHI) module."""

from typing import Final

# Default TCP port for connecting to the Luxtronik controller
LUXTRONIK_DEFAULT_MODBUS_PORT = 502

# Default timeout (in seconds) for Modbus operations
LUXTRONIK_DEFAULT_MODBUS_TIMEOUT = 30

# Waiting time (in seconds) after writing the holdings
# to give the controller time to recalculate values, etc.
LUXTRONIK_WAIT_TIME_AFTER_HOLDING_WRITE = 1

# Since version 3.92.0, all unavailable data fields have been returning this value
LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE = 32767

# First Luxtronik firmware version that supports the Smart Home Interface (SHI)
LUXTRONIK_FIRST_VERSION_WITH_SHI = (3, 90, 1, 0) # parse_version("3.90.1")

# Latest supported Luxtronik firmware version
LUXTRONIK_LATEST_SHI_VERSION = (3, 92, 0, 0) # parse_version("3.92.0")




LUXTRONIK_DEFAULT_DEFINITION_OFFSET = 10000

HOLDINGS_FIELD_NAME: Final = "holding"


INPUTS_FIELD_NAME: Final = "input"
