import logging
import time
from pyModbusTCP.client import ModbusClient

from luxtronik.common import get_host_lock
from luxtronik.constants import (
    LUXTRONIK_WAIT_TIME_AFTER_PARAMETER_WRITE,
)
from luxtronik.shi.constants import (
    LUXTRONIK_DEFAULT_MODBUS_PORT,
    LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
)
from luxtronik.shi.common import (
    LuxtronikSmartHomeReadTelegram,
    LuxtronikSmartHomeWriteTelegram,
)

LOGGER = logging.getLogger("Luxtronik.SmartHomeInterface")

###############################################################################
# Modbus TCP interface
###############################################################################

class LuxtronikModbusTcpInterface:
    """
    Luxtronik read/write interface using Modbus-TCP.
    This class is designed to offer a simple addr/count/data interface.
    There are functions to read or write individual register blocks,
    or multiple blocks in a row using a list of telegrams.
    The connection is established only for reading and writing purposes.
    This class is implemented as thread-safe.
    """

    def __init__(
        self,
        host,
        port=LUXTRONIK_DEFAULT_MODBUS_PORT,
        timeout_in_s=LUXTRONIK_DEFAULT_MODBUS_TIMEOUT
    ):
        """
        Initialize the Modbus TCP interface for a Luxtronik host.

        Args:
            host (str): Hostname or IP address of the heat pump.
            port (int): TCP port for the Modbus connection
                  (default: LUXTRONIK_DEFAULT_MODBUS_PORT).
            timeout_in_s (float): Timeout in seconds for communication
                     (default: LUXTRONIK_DEFAULT_MODBUS_TIMEOUT).
        """
        # Acquire a lock object for this host to ensure thread safety
        self._lock = get_host_lock(host)

        # Create the Modbus client (connection is not opened/closed automatically)
        self._client = ModbusClient(
            host=host,
            port=port,
            timeout=timeout_in_s,
            auto_open=False,
            auto_close=False,
        )

    @property
    def lock(self):
        return self._lock

# Connection methods ##########################################################

    def _connect(self):
        """
        Establish a connection to the heat pump.

        Returns:
            bool: True if the connection was successfully established, False otherwise.
        """
        # Do nothing if client is already opened
        if self._client.is_open:
            return True

        self._client.open()

        if not self._client.is_open:
            LOGGER.error("Modbus connection failed (client did not open).")
            self._client.close()
            return False

        return True

    def _disconnect(self):
        """
        Close the connection to the heat pump.

        Returns:
            bool: True if the connection was successfully closed, False otherwise.
        """
        # Do nothing if already closed
        if not self._client.is_open:
            return True

        self._client.close()

        if self._client.is_open:
            LOGGER.error("Modbus disconnect failed (client still open).")
            return False

        return True

        from contextlib import contextmanager

    @contextmanager
    def _connection(self):
        """
        Context manager that acquires the host-lock,
        opens a Modbus connection and ensures
        it is closed afterwards.
        """
        with self._lock:
            if not self._connect():
                return
            try:
                yield
            finally:
                self._disconnect()


# Common read methods #########################################################

    def _read_register(self, read_reg_cb, telegrams):
        """
        Read Modbus registers for one or more telegrams.

        For each provided telegram, this method reads the specified number of
        16‑bit registers (`count`) starting at the given Modbus address (`addr`).
        The address is used directly without applying additional offsets.

        The callback function `read_reg_cb` determines whether input or holding
        registers are read. The retrieved data is stored in each telegram's
        `data` field. If an error occurs, the `data` field is filled with
        `LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE`.

        Args:
            read_reg_cb (Callable): Callback used to perform the actual register read.
            telegrams (list[LuxtronikSmartHomeReadTelegram] | LuxtronikSmartHomeReadTelegram):
                A single `LuxtronikSmartHomeReadTelegram` or a list of them.

        Returns:
            bool: True if all reads succeeded, False otherwise.
        """
        # Normalize to a list of telegrams
        _telegrams = telegrams
        if isinstance(_telegrams, LuxtronikSmartHomeReadTelegram):
            _telegrams = [_telegrams]

        # Validate input
        if not isinstance(_telegrams, list) or not all(isinstance(t, LuxtronikSmartHomeReadTelegram) for t in _telegrams):
            LOGGER.warning(f"Invalid argument '{telegrams}': expected a LuxtronikSmartHomeReadTelegram or a list of them.")
            return False

        # Prepare data arrays and count total registers
        total_count = 0
        for t in _telegrams:
            total_count += t.count
            t.data = []

        # Exit function if no data is requested
        if total_count <= 0:
            LOGGER.warning("Modbus read aborted: no data requested.")
            return False

        # Acquire lock, connect and read data. Disconnect afterwards.
        success = False
        with self._connection:
            success = True
            for t in _telegrams:
                if t.count <= 0:
                    continue
                # Read len(t.data) × 16‑bit registers from Modbus address t.addr
                t.data = read_reg_cb(t.addr, t.count)

        # Validate and post‑process results
        for t in _telegrams:
            if not t.normalize_data():
                success = False
                LOGGER.error(f"Modbus read failed: addr={t.addr}, count={t.count}, data={t.data}")

        if not success:
            LOGGER.error(f"Modbus read operation failed: {self._client.last_error_as_txt}", )

        return success


# Common write methods ########################################################

    def _write_register(self, write_reg_cb, telegrams):
        """
        Write Modbus registers for one or more telegrams.

        For each provided telegram, all values in `data` are written to 16‑bit
        registers starting at the specified Modbus address (`addr`). The address
        is used directly without applying additional offsets.

        The callback function `write_reg_cb` performs the actual write operation
        (currently only valid for holding registers).

        Args:
            write_reg_cb: Callback used to perform the register write.
            telegrams (list[LuxtronikSmartHomeWriteTelegram] | LuxtronikSmartHomeWriteTelegram):
                A single LuxtronikSmartHomeWriteTelegram or a list of them.

        Returns:
            bool: True if all writes succeeded, False otherwise.
        """
        # Normalize to a list
        _telegrams = telegrams
        if isinstance(_telegrams, LuxtronikSmartHomeWriteTelegram):
            _telegrams = [_telegrams]

        # Validate input
        if not isinstance(_telegrams, list) or not all(isinstance(t, LuxtronikSmartHomeWriteTelegram) for t in _telegrams):
            LOGGER.warning(f"Invalid argument '{telegrams}': expected a LuxtronikSmartHomeWriteTelegram or a list of them.")
            return False

        # Count total registers to write
        total_count = 0
        for telegram in _telegrams:
            total_count += telegram.count

        # Exit function if no data should be written
        if total_count <= 0:
            LOGGER.warning("Modbus write aborted: no data to write.")
            return False

        # Acquire lock, connect and write data. Disconnect afterwards.
        success = False
        with self._connection:
            success = True
            for t in _telegrams:
                if t.count <= 0:
                    continue
                # Write len(t.data) × 16‑bit registers at Modbus address t.addr
                write_ok = write_reg_cb(t.addr, t.data)
                if not write_ok:
                    LOGGER.error(f"Modbus write error: addr={t.addr}, data={t.data}")
                success &= write_ok

        # Allow the heat pump to process the changes
        time.sleep(LUXTRONIK_WAIT_TIME_AFTER_PARAMETER_WRITE)

        if not success:
            LOGGER.error(f"Modbus write operation failed: {self._client.last_error_as_txt}", )

        return success


# Holding methods #############################################################

    def read_holdings_raw(self, addr, count):
        """
        Read `count` holding 16‑bit registers starting at the given Modbus address `addr`.
        The address is used directly without additional offsets.

        Args:
            addr (int): The starting Modbus register address to read from.
            count (int): The number of 16‑bit registers to read.

        Returns:
            list[int] | None: On success, returns the read data as a list of integers.
                              On failure, returns None.
        """
        telegram = LuxtronikSmartHomeReadTelegram(addr, count)
        success = self.read_holdings(telegram)
        return telegram.data if success else None

    def read_holdings(self, telegrams):
        """
        Read holding registers for one or more telegrams.

        For each telegram, the specified number of 16‑bit registers (`count`)
        is read starting at the given Modbus address (`addr`).
        The address is used directly without additional offsets.
        The retrieved data is stored in the telegram's `data` field.
        On error, the field is filled with LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE.

        Args:
            telegrams (list[LuxtronikSmartHomeReadTelegram] | LuxtronikSmartHomeReadTelegram):
                A LuxtronikSmartHomeReadTelegram or a list of them.

        Returns:
            bool: True if all reads succeeded, False otherwise.
        """
        return self._read_register(self._client.read_holding_registers, telegrams)

    def write_holdings_raw(self, addr, data):
        """
        Write all values in `data` to 16‑bit holding registers starting at the given Modbus address `addr`.

        Args:
            addr (int): The starting Modbus register address to write to.
            count (int): The number of 16‑bit registers to write.

        The address is used directly without additional offsets.

        Returns:
            bool: True if the write succeeded, False otherwise.
        """
        telegram = LuxtronikSmartHomeWriteTelegram(addr, data)
        return self.write_holdings(telegram)

    def write_holdings(self, telegrams):
        """
        Write holding registers for one or more telegrams.

        For each telegram, all values in `data` are written to 16‑bit registers
        starting at the given Modbus address (`addr`).
        The address is used directly without additional offsets.

        Args:
            telegrams (list[LuxtronikSmartHomeWriteTelegram] | LuxtronikSmartHomeWriteTelegram):
                A LuxtronikSmartHomeWriteTelegram or a list of them.

        Returns:
            bool: True if all writes succeeded, False otherwise.
        """
        return self._write_register(self._client.write_multiple_registers, telegrams)


# Inputs methods ##############################################################

    def read_inputs_raw(self, addr, count):
        """
        Read `count` input 16‑bit registers starting at the given Modbus address `addr`.
        The address is used directly without additional offsets.

        Args:
            addr (int): The starting Modbus register address to read from.
            count (int): The number of 16‑bit registers to read.

        Returns:
            list[int] | None: On success, returns the read data as a list of integers.
                              On failure, returns None.
        """
        telegram = LuxtronikSmartHomeReadTelegram(addr, count)
        success = self.read_inputs(telegram)
        return telegram.data if success else None

    def read_inputs(self, telegrams):
        """
        Read input registers for one or more telegrams.

        For each telegram, the specified number of 16‑bit registers (`count`)
        is read starting at the given Modbus address (`addr`).
        The address is used directly without additional offsets.
        The retrieved data is stored in the telegram's `data` field.
        On error, the field is filled with LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE.

        Args:
            telegrams (list[LuxtronikSmartHomeReadTelegram] | LuxtronikSmartHomeReadTelegram):
                A LuxtronikSmartHomeReadTelegram or a list of them.

        Returns:
            bool: True if all reads succeeded, False otherwise.
        """
        return self._read_register(self._client.read_input_registers, telegrams)