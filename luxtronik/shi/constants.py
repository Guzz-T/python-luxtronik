"""Constants used throughout the luxtronik shi module"""

# Default port to be used to connect to Luxtronik controller.
LUXTRONIK_DEFAULT_MODBUS_PORT = 502

# Default timeout for modbus operations
LUXTRONIK_DEFAULT_MODBUS_TIMEOUT = 30 # 30s

# First luxtronik version that implements the smart-home-interface
LUXTRONIK_FIRST_VERSION_WITH_SHI = "3.90.1"

# Since version 3.92.0, all unavailable data fields have been returning this value
LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE = 32767