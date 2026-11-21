"""Main components of the Luxtronik config interface."""

import logging
import socket
import struct
import time

from luxtronik.constants import LUXTRONIK_VERSION_IGNORE
from luxtronik.collections import integrate_data
from luxtronik.common import get_host_lock
from luxtronik.version import VER_IGNORE, resolve_version_input
from luxtronik.cfi.constants import (
    LUXTRONIK_DEFAULT_CFI_PORT,
    LUXTRONIK_PARAMETERS_WRITE,
    LUXTRONIK_PARAMETERS_READ,
    LUXTRONIK_CALCULATIONS_READ,
    LUXTRONIK_VISIBILITIES_READ,
    LUXTRONIK_SOCKET_READ_SIZE_INTEGER,
    LUXTRONIK_SOCKET_READ_SIZE_CHAR,
    WAIT_TIME_AFTER_PARAMETER_WRITE,
    LUXTRONIK_CFI_REGISTER_BIT_SIZE,
)
from luxtronik.cfi.calculations import Calculations
from luxtronik.cfi.parameters import Parameters
from luxtronik.cfi.visibilities import Visibilities


LOGGER = logging.getLogger(__name__)

###############################################################################
# Config interface data
###############################################################################

class LuxtronikData:
    """
    Collection of parameters, calculations and visiblities.
    Also provide some high level access functions to their data values.

    Note: This class is grouped with other classes in the Luxtronik section.
    Use only unique identifiers (e.g., using name mangling like `self.__version`;
    this is checked by pytest) for methods and fields and do not use public
    methods internally (e.g., `self.version`). Otherwise, the correct function
    might not be called.
    """

    def __init__(
        self,
        parameters=None,
        calculations=None,
        visibilities=None,
        version=LUXTRONIK_VERSION_IGNORE,
        safe=True
    ):
        """
        Initialize a LuxtronikData instance.

        Args:
            parameters (Parameters): Optional parameters data vector. If not provided,
                a new `Parameters` instance is created.
            calculations (Calculations): Optional calculations data vector. If not provided,
                a new `Calculations` instance is created.
            visibilities (Visibilities): Optional visibilities data vector. If not provided,
                a new `Visibilities` instance is created.
            version (tuple[int] | str | None): Version to be used for creating the data vectors.
                This ensures that the data vectors only contain valid fields.
                If None is passed, all available fields are added.
                (default: LUXTRONIK_VERSION_IGNORE)
            safe (bool): If true, prevent holding fields marked as
                not secure from being written to.
        """
        version, _ = resolve_version_input(version) # no auto-detect possible here
        self.parameters = Parameters(version, safe) if parameters is None else parameters
        self.calculations = Calculations(version) if calculations is None else calculations
        self.visibilities = Visibilities(version) if visibilities is None else visibilities

    @classmethod
    def empty(
        cls,
        version=LUXTRONIK_VERSION_IGNORE,
        safe=True
    ):
        """
        Initialize an empty LuxtronikData instance
        (= no fields are added to the data-vectors).

        Args:
            version (tuple[int] | str | None): The version is added to the data vectors
                so some checks can be performed later.
                (default: LUXTRONIK_VERSION_IGNORE)
            safe (bool): If true, prevent holding fields marked as
                not secure from being written to.
        """
        obj = cls.__new__(cls)
        version, _ = resolve_version_input(version) # no auto-detect possible here
        obj.parameters = Parameters.empty(version, safe)
        obj.calculations = Calculations.empty(version)
        obj.visibilities = Visibilities.empty(version)
        return obj

    def get_firmware_version(self):
        return self.calculations.get_firmware_version()


###############################################################################
# Config interface
###############################################################################

class LuxtronikSocketInterface:
    """
    Luxtronik read/write interface via socket.

    Note: This class is grouped with other classes in the Luxtronik section.
    Use only unique identifiers (e.g., using name mangling like `self.__version`;
    this is checked by pytest) for methods and fields and do not use public
    methods internally (e.g., `self.version`). Otherwise, the correct function
    might not be called.
    """

    def __init__(self, host, port=LUXTRONIK_DEFAULT_CFI_PORT):
        # Use name-mangling for unique field names. See class description.
        # Acquire a lock object for this host to ensure thread safety
        self.__lock = get_host_lock(host)
        self.__host = host
        self.__port = port
        self._socket = None

    @property
    def lock(self):
        return self.__lock

    def _with_lock_and_connect(self, func, *args, **kwargs):
        """
        Decorator around various read/write functions to connect first.

        This method is essentially a wrapper for the _read() and _write() methods.
        Locking is being used to ensure that only a single socket operation is
        performed at any point in time. This helps to avoid issues with the
        Luxtronik controller, which seems unstable otherwise.
        """
        with self.__lock:
            try:
                ret_val = None
                with socket.create_connection((self.__host, self.__port)) as sock:
                    self._socket = sock
                    LOGGER.info("Connected to CFI of Luxtronik heat pump %s:%s", self.__host, self.__port)
                    ret_val = func(*args, **kwargs)
            except socket.gaierror as e:
                LOGGER.error("Failed to connect to Luxtronik heat pump %s:%s. %s.",
                    self.__host, self.__port, f"Address-related error: {e}")
            except socket.timeout as e:
                LOGGER.error("Failed to connect to Luxtronik heat pump %s:%s. %s.",
                    self.__host, self.__port, f"Connection timed out: {e}")
            except ConnectionRefusedError as e:
                LOGGER.error("Failed to connect to Luxtronik heat pump %s:%s. %s.",
                    self.__host, self.__port, f"Connection refused: {e}")
            except OSError as e:
                LOGGER.error("Failed to connect to Luxtronik heat pump %s:%s. %s.",
                    self.__host, self.__port, f"OS error during connect: {e}")
            except Exception as e:
                LOGGER.error("Failed to connect to Luxtronik heat pump %s:%s. %s.",
                    self.__host, self.__port, f"Unknown exception: {e}")
        self._socket = None
        return ret_val

    def read(self, data=None):
        """
        All available data will be read from the heat pump
        and integrated to the passed data object.
        This data object is returned afterwards, mainly for access to a newly created.
        """
        if data is None:
            data = LuxtronikData(None, None, None, VER_IGNORE, True)
        return self._with_lock_and_connect(self._read, data)

    def read_parameters(self, parameters=None):
        """
        Read parameters from heat pump and integrate them to the passed dictionary.
        This dictionary is returned afterwards, mainly for access to a newly created.
        """
        if parameters is None:
            parameters = Parameters(VER_IGNORE)
        return self._with_lock_and_connect(self._read_parameters, parameters)

    def read_calculations(self, calculations=None):
        """
        Read calculations from heat pump and integrate them to the passed dictionary.
        This dictionary is returned afterwards, mainly for access to a newly created.
        """
        if calculations is None:
            calculations = Calculations(VER_IGNORE)
        return self._with_lock_and_connect(self._read_calculations, calculations)

    def read_visibilities(self, visibilities=None):
        """
        Read visibilities from heat pump and integrate them to the passed dictionary.
        This dictionary is returned afterwards, mainly for access to a newly created.
        """
        if visibilities is None:
            visibilities = Visibilities(VER_IGNORE)
        return self._with_lock_and_connect(self._read_visibilities, visibilities)

    def write(self, parameters):
        """
        Write all set parameters to the heat pump.
        :param Parameters() parameters  Parameter dictionary to be written
                          to the heatpump before reading all available data
                          from the heat pump.
        """
        self._with_lock_and_connect(self._write, parameters)

    def write_and_read(self, parameters, data=None):
        """
        Write all set parameter to the heat pump (see write())
        prior to reading back in all data from the heat pump (see read())
        after a short wait time
        """
        if data is None:
            data = LuxtronikData(None, None, None, VER_IGNORE, True)
        return self._with_lock_and_connect(self._write_and_read, parameters, data)

    def _read(self, data):
        self._read_parameters(data.parameters)
        self._read_calculations(data.calculations)
        self._read_visibilities(data.visibilities)
        return data

    def _write_and_read(self, parameters, data):
        self._write(parameters)
        return self._read(data)

    def _write(self, parameters):
        if not isinstance(parameters, Parameters):
            LOGGER.error("Only parameters are writable!")
            return
        count = 0
        for definition, field in parameters.items():
            if field.write_pending:
                field.write_pending = False
                value = field.raw
                if not isinstance(definition.index, int) or not field.check_for_write(parameters.safe):
                    LOGGER.warning(
                        "%s: Parameter id '%s' or value '%s' invalid!",
                        self.__host,
                        definition.index,
                        value,
                    )
                    continue
                LOGGER.debug("%s: Parameter '%d' set to '%s'", self.__host, definition.index, value)
                self._send_ints(LUXTRONIK_PARAMETERS_WRITE, definition.index, value)
                cmd = self._read_int()
                LOGGER.debug("%s: Command %s", self.__host, cmd)
                val = self._read_int()
                LOGGER.debug("%s: Value %s", self.__host, val)
                count += 1
        LOGGER.info("%s: Write %d parameters", self.__host, count)
        # Give the heatpump a short time to handle the value changes/calculations:
        time.sleep(WAIT_TIME_AFTER_PARAMETER_WRITE)

    def _read_parameters(self, parameters):
        data = []
        self._send_ints(LUXTRONIK_PARAMETERS_READ, 0)
        cmd = self._read_int()
        LOGGER.debug("%s: Command %s", self.__host, cmd)
        length = self._read_int()
        LOGGER.debug("%s: Length %s", self.__host, length)
        for _ in range(0, length):
            data.append(self._read_int())
        LOGGER.info("%s: Read %d parameters", self.__host, length)
        self._parse(parameters, data)
        return parameters

    def _read_calculations(self, calculations):
        data = []
        self._send_ints(LUXTRONIK_CALCULATIONS_READ, 0)
        cmd = self._read_int()
        LOGGER.debug("%s: Command %s", self.__host, cmd)
        stat = self._read_int()
        LOGGER.debug("%s: Stat %s", self.__host, stat)
        length = self._read_int()
        LOGGER.debug("%s: Length %s", self.__host, length)
        for _ in range(0, length):
            data.append(self._read_int())
        LOGGER.info("%s: Read %d calculations", self.__host, length)
        self._parse(calculations, data)
        return calculations

    def _read_visibilities(self, visibilities):
        data = []
        self._send_ints(LUXTRONIK_VISIBILITIES_READ, 0)
        cmd = self._read_int()
        LOGGER.debug("%s: Command %s", self.__host, cmd)
        length = self._read_int()
        LOGGER.debug("%s: Length %s", self.__host, length)
        for _ in range(0, length):
            data.append(self._read_char())
        LOGGER.info("%s: Read %d visibilities", self.__host, length)
        self._parse(visibilities, data)
        return visibilities

    def _send_ints(self, *ints):
        "Low-level helper to send a tuple of ints"
        data = struct.pack(">" + "i" * len(ints), *ints)
        LOGGER.debug("%s: sending %s", self.__host, data)
        self._socket.sendall(data)

    def _read_bytes(self, count):
        "Low-level helper to receive a precise number of bytes"
        total_reading = b""

        while len(total_reading) is not count:
            missing = count - len(total_reading)

            reading = self._socket.recv( missing )

            if len(reading) == 0:
                LOGGER.error("%s: Connection died.", self.__host)
                raise ConnectionError("Connection to %s died." % self.__host)

            total_reading += reading

            if len(reading) is not missing:
                LOGGER.debug("%s: received %s bytes out of %s bytes. Will read again.", self.__host, len(reading), missing)

        return total_reading

    def _read_int(self):
        "Low-level helper to receive an int"
        reading = self._read_bytes(LUXTRONIK_SOCKET_READ_SIZE_INTEGER)
        return struct.unpack(">i", reading)[0]

    def _read_char(self):
        "Low-level helper to receive a signed int"
        reading = self._read_bytes(LUXTRONIK_SOCKET_READ_SIZE_CHAR)
        return struct.unpack(">b", reading)[0]

    def _parse(self, data_vector, raw_data):
        """
        Parse raw data into the corresponding fields.

        Args:
            data_vector (DataVector): Data vector in which
                the raw data is to be integrated.
            raw_data (list[int]): List of raw register values.
                The raw data must start at register index 0.
        """
        raw_len = len(raw_data)
        # Prepare a list of undefined indices
        undefined = {i for i in range(0, raw_len)}

        # integrate the data into the fields
        for pair in data_vector.data.items():
            definition, field = pair
            # skip this field if there are not enough data
            next_idx = definition.index + definition.count
            if next_idx > raw_len:
                # not enough registers
                field.clear()
                continue
            # remove all used indices from the list of undefined indices
            for index in range(definition.index, next_idx):
                undefined.discard(index)
            # integrate_data() also resets the write_pending flag,
            # intentionally only for read fields
            pair.integrate_data(raw_data, LUXTRONIK_CFI_REGISTER_BIT_SIZE)

        # create an unknown field for additional data
        for index in undefined:
            # LOGGER.warning(f"Entry '%d' not in list of {self.name}", index)
            definition = data_vector.definitions.create_unknown_definition(index)
            field = definition.create_field()
            integrate_data(definition, field, raw_data, LUXTRONIK_CFI_REGISTER_BIT_SIZE, index)
            data_vector.data.add_sorted(definition, field)
