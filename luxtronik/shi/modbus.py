import logging
import time
from pyModbusTCP.client import ModbusClient

from luxtronik.common import *
from luxtronik.constants import (
    LUXTRONIK_DEFAULT_MODBUS_PORT,
    LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
    LUXTRONIK_WAIT_TIME_AFTER_PARAMETER_WRITE,
    LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE,
)
from luxtronik.shi.common import LuxtronikSmartHomeReadTelegram, LuxtronikSmartHomeWriteTelegram

LOGGER = logging.getLogger("Luxtronik.Modbus")

###############################################################################
# Modbus TCP interface
###############################################################################

class LuxtronikModbusTcpInterface:
    """
    Luxtronik read/write interface using Modbus-TCP.
    The connection is established only for reading and writing purposes.
    This class is implemented as thread-safe.
    """

    def __init__(self, host, port=LUXTRONIK_DEFAULT_MODBUS_PORT, timeout=LUXTRONIK_DEFAULT_MODBUS_TIMEOUT):
        add_host_to_locks(host)

        # Create modbus client
        self._host = host
        self._client = ModbusClient(
            host=host,
            port=port,
            timeout=timeout, # in seconds
            auto_open=False,
            auto_close=False
        )

    @property
    def _modbus_lock(self):
        return hosts_locks[self._host]

# Connection methods ##########################################################

    def _connect(self):
        if not self._client.is_open:
            self._client.open()
        if not self._client.is_open:
            LOGGER.error(f"Modbus connection failed!")
            self._client.close()
        return self._client.is_open

    def _disconnect(self):
        if self._client.is_open:
            self._client.close()
        if self._client.is_open:
            LOGGER.error(f"Modbus disconnect failed!")

# Common read methods #########################################################

    def _read_register(self, read_reg_cb, telegrams):
        """
        For each provided telegram read the specified number of 16-bit registers ('count')
        from the given Modbus address ('addr'). The address is used directly without applying additional offsets.
        The provided callback method determines whether input or holding registers are read.
        The read data is returned via the provided telegrams ('data'). In case of an error these arrays are
        filled with LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE.
        """
        # Convert a single telegram into a list
        _telegrams = telegrams
        if isinstance(_telegrams, LuxtronikSmartHomeReadTelegram):
            _telegrams = [_telegrams]
        if not isinstance(_telegrams, list) or not all(isinstance(telegram, LuxtronikSmartHomeReadTelegram) for telegram in _telegrams):
            LOGGER.warning(f"Wrong data type. Please provide a list of LuxtronikSmartHomeReadTelegram!")
            return False

        # Prepare data arrays and count the total number of bytes to read
        total_count = 0
        for telegram in _telegrams:
            total_count += telegram.count
            telegram.data = []

        # Exit function if no data is requested
        if total_count <= 0:
            LOGGER.warning(f"Modbus read operation aborted. No data requested.")
            return False

        # Acquire lock for this host
        success = False
        with self._modbus_lock:
            if self._connect():

                success = True
                # Read all requested data
                for telegram in _telegrams:
                    if telegram.count >= 0:
                        telegram.data = read_reg_cb(telegram.addr, telegram.count)

            self._disconnect()

        # Post-process read data
        if success:
            for telegram in _telegrams:
                data_len = len(telegram.data) if telegram.data and isinstance(telegram.data, list) else 0
                data_valid = data_len == telegram.count
                if telegram.data is None:
                    telegram.data = [LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE] * telegram.count
                elif data_len < telegram.count:
                    telegram.data += [LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE] * (telegram.count - data_len)
                elif data_len > telegram.count:
                    telegram.data = telegram.data[:telegram.count]
                if not data_valid:
                    success = False
                    LOGGER.error(f"Modbus read operation failed: addr={telegram.addr}, count={telegram.count}")

        if not success:
            LOGGER.error(f"Modbus read operation failed. {self._client.last_error_as_txt}")
        return success

# Common write methods ########################################################

    def _write_register(self, write_reg_cb, telegrams):
        """
        For each provided telegram write all provided data (`data`) to 16-bit registers at the
        specified Modbus address (`addr`). The address is used directly without applying additional offsets.
        The provided callback method determines whether input or holding registers are written.
        """
        # Convert a single telegram into a list
        _telegrams = telegrams
        if isinstance(_telegrams, LuxtronikSmartHomeWriteTelegram):
            _telegrams = [_telegrams]
        if not isinstance(_telegrams, list) or not all(isinstance(telegram, LuxtronikSmartHomeWriteTelegram) for telegram in _telegrams):
            LOGGER.warning(f"Wrong data type. Please provide a list of LuxtronikSmartHomeWriteTelegram!")
            return False

        # Check data arrays and count the total number of bytes to read
        total_count = 0
        for telegram in _telegrams:
            total_count += telegram.count

        # Exit function if no data should be written
        if total_count <= 0:
            LOGGER.warning(f"Modbus write operation aborted. No data to write.")
            return False

        # Acquire lock for this host
        success = False
        with self._modbus_lock:
            if self._connect():

                success = True
                # Write all provided data
                for telegram in _telegrams:
                    if telegram.count >= 0:
                        # Write len(telegram.data) x 16 bits registers at modbus address "telegram.addr"
                        write_ok = write_reg_cb(telegram.addr, telegram.data)
                        if not write_ok:
                            LOGGER.error(f"Modbus write error: addr={telegram.addr}, data={telegram.data}")
                        success &= write_ok

            self._disconnect()

        # Give the heatpump a short time to handle the value changes:
        time.sleep(LUXTRONIK_WAIT_TIME_AFTER_PARAMETER_WRITE)

        if not success:
            LOGGER.error(f"Modbus write operation failed. {self._client.last_error_as_txt}")
        return success

# Holding methods #############################################################

    def read_holdings_raw(self, addr, count):
        """
        Read the specified number of 16-bit registers ('count') from the given Modbus address ('addr').
        The address is used directly without applying additional offsets.
        In case of an error these arrays are filled with LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE.
        """
        telegram = LuxtronikSmartHomeReadTelegram(addr, count)
        result = self.read_holdings(telegram)
        return telegram.data if result else None

    def read_holdings(self, telegrams):
        """
        For each provided telegram read the specified number of 16-bit registers ('count')
        from the given Modbus address ('addr'). The address is used directly without applying additional offsets.
        The read data is returned via the provided telegrams ('data'). In case of an error these arrays are
        filled with LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE.
        """
        return self._read_register(self._client.read_holding_registers, telegrams)

    def write_holdings_raw(self, addr, data):
        """
        Write all provided data (`data`) to 16-bit registers at the
        specified Modbus address (`addr`). The address is used directly without applying additional offsets.
        """
        telegram = LuxtronikSmartHomeWriteTelegram(addr, data)
        result = self.write_holdings(telegram)
        return True if result else None

    def write_holdings(self, telegrams):
        """
        For each provided telegram write all provided data (`data`) to 16-bit registers at the
        specified Modbus address (`addr`). The address is used directly without applying additional offsets.
        """
        return self._write_register(self._client.write_multiple_registers, telegrams)

# Inputs methods ##############################################################

    def read_inputs_raw(self, addr, count):
        """
        Read the specified number of 16-bit registers ('count') from the given Modbus address ('addr').
        The address is used directly without applying additional offsets.
        In case of an error these arrays are filled with LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE.
        """
        telegram = LuxtronikSmartHomeReadTelegram(addr, count)
        result = self.read_inputs(telegram)
        return telegram.data if result else None

    def read_inputs(self, telegrams):
        """
        For each provided telegram read the specified number of 16-bit registers ('count')
        from the given Modbus address ('addr'). The address is used directly without applying additional offsets.
        The read data is returned via the provided telegrams ('data'). In case of an error these arrays are
        filled with LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE.
        """
        return self._read_register(self._client.read_input_registers, telegrams)