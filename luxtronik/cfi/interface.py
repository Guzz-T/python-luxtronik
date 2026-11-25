"""Main components of the Luxtronik config interface."""

import logging
import socket
import struct
import time

from luxtronik.constants import LUXTRONIK_VERSION_IGNORE
from luxtronik.collections import integrate_data, get_check_and_create_def_field_pair
from luxtronik.common import get_host_lock
from luxtronik.definitions import (
    resolve_name_or_idx_input,
    LuxtronikDefinitionsList
)
from luxtronik.interface import LuxtronikInterfaceInfo, LuxtronikBaseInterface
from luxtronik.version import VER_IGNORE, parse_version, resolve_version_input
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
from luxtronik.cfi.calculations import Calculations, CALCULATIONS_DEFINITIONS
from luxtronik.cfi.parameters import Parameters, PARAMETERS_DEFINITIONS
from luxtronik.cfi.visibilities import Visibilities, VISIBILITIES_DEFINITIONS

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

class LuxtronikSocketInterface(LuxtronikBaseInterface):
    """
    Luxtronik read/write interface via socket.

    Note: This class is grouped with other classes in the Luxtronik section.
    Use only unique identifiers (e.g., using name mangling like `self.__version`;
    this is checked by pytest) for methods and fields and do not use public
    methods internally (e.g., `self.version`). Otherwise, the correct function
    might not be called.
    """

    def __init_instance(self, host, port, version, parameters, calculations, visibilities):
        """Re-usable method to initialize all instance variables."""
        # Use name-mangling for unique field names. See class description.
        # Acquire a lock object for this host to ensure thread safety
        self.__lock = get_host_lock(host)
        self.__host = host
        self.__port = port
        self._socket = None
        self.__version = version # is never none
        self.__info = LuxtronikInterfaceInfo(
            'CFI',
            host,
            port,
            version
        )
        self._filtered_parameters = parameters
        self._filtered_calculations = calculations
        self._filtered_visibilities = visibilities

    def __init__(self, host, port=LUXTRONIK_DEFAULT_CFI_PORT, version=LUXTRONIK_VERSION_IGNORE):
        """
        Initialize the config interface.

        Args:
            host (str): IP-Address or name of the host.
            port (int): Port to use.
            version (tuple[int] | str | None): Version to be used for creating fields or data vectors.
                This ensures that the data vectors only contain valid fields.
                If None is passed, all available fields are added.
                Additionally, the version is used to performed some consistency checks.
                (default: LUXTRONIK_VERSION_IGNORE)
        """
        version, do_auto_detect = resolve_version_input(version)

        if do_auto_detect:
            version = LuxtronikSocketInterface.determine_version(host, port)
            LOGGER.info(f"Auto-detect version {version}")

        self.__init_instance(
            host,
            port,
            version,
            LuxtronikDefinitionsList.filtered(PARAMETERS_DEFINITIONS, version),
            LuxtronikDefinitionsList.filtered(CALCULATIONS_DEFINITIONS, version),
            LuxtronikDefinitionsList.filtered(VISIBILITIES_DEFINITIONS, version)
        )

    @classmethod
    def __temp(cls, host, port):
        """Constructor for a temporary interface used in determine_cfi_cfi_version"""
        obj = cls.__new__(cls) # this don't call __init__()
        obj.__init_instance(host, port, VER_IGNORE, PARAMETERS_DEFINITIONS,
            CALCULATIONS_DEFINITIONS, VISIBILITIES_DEFINITIONS)
        return obj

    @property
    def lock(self):
        return self.__lock

    @property
    def info(self):
        return self.__info

# Version methods ##############################################################

    @classmethod
    def determine_version(cls, host, port):
        """
        Determine the version of the luxtronik controller.

        This is a little bit ugly! The controller version is required
        to locate the version field. As workaround, probe each ever known
        version field until one yields a valid read and a parsable version.
        This approach works as long as the version-field has not changed.

        Returns:
            tuple[int] | None: The version of the controller on success,
                or None if no version could be determined.
        """
        # Create a temporary interface, that allows any field, to read out the version info
        cfi_interface = LuxtronikSocketInterface.__temp(host, port)
        return cfi_interface.read_version()

    @property
    def version(self):
        return self.__version

    def read_version(self):
        """
        Determine the version of the luxtronik controller, via one
        of the valid version fields.

        Returns:
            tuple[int] | None: The version of the controller on success,
                or None if no version could be determined.
        """
        definitions = CALCULATIONS_DEFINITIONS.get_version_definitions(self.__version)
        calcs = self.read_calculations()
        for definition in definitions:
            field = calcs.get(definition)
            if field is not None:
                parsed = parse_version(field.get_version_str())
                if parsed is not None:
                    return parsed
        LOGGER.warning("It was not possible to determine the controller version " \
            + "via the CFI.")
        return VER_IGNORE

# Helper methods ##############################################################

    def create_data(self, safe=True):
        """See LuxtronikBaseInterface.create_data description"""
        return LuxtronikData(None, None, None, self.__version, safe)

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

# Read methods ################################################################

    def read(self, data=None):
        """
        All available data will be read from the heat pump
        and integrated to the passed data object.
        This data object is returned afterwards, mainly for access to a newly created.
        """
        if data is None:
            data = LuxtronikData(None, None, None, self.__version, True)
        return self._with_lock_and_connect(self._read, data)

    def read_parameters(self, parameters=None):
        """
        Read parameters from heat pump and integrate them to the passed dictionary.
        This dictionary is returned afterwards, mainly for access to a newly created.
        """
        if parameters is None:
            parameters = Parameters(self.__version)
        return self._with_lock_and_connect(self._read_parameters, parameters)

    def read_calculations(self, calculations=None):
        """
        Read calculations from heat pump and integrate them to the passed dictionary.
        This dictionary is returned afterwards, mainly for access to a newly created.
        """
        if calculations is None:
            calculations = Calculations(self.__version)
        return self._with_lock_and_connect(self._read_calculations, calculations)

    def read_visibilities(self, visibilities=None):
        """
        Read visibilities from heat pump and integrate them to the passed dictionary.
        This dictionary is returned afterwards, mainly for access to a newly created.
        """
        if visibilities is None:
            visibilities = Visibilities(self.__version)
        return self._with_lock_and_connect(self._read_visibilities, visibilities)

# Write methods ###############################################################

    def write_parameter(self, def_field_name_or_idx, value=None, safe=True):
        """Calls `_write_parameter` with the lock-and-connect decorator."""
        return self._with_lock_and_connect(self._write_parameter, def_field_name_or_idx, value, safe)

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
            data = LuxtronikData(None, None, None, self.__version, True)
        return self._with_lock_and_connect(self._write_and_read, parameters, data)

# Private methods ###############################################################

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
            if definition.version.matches(self.__version) and field.write_pending:
                if self._do_write_field(LUXTRONIK_PARAMETERS_WRITE, \
                        definition.index, field, parameters.safe):
                    count += 1
        LOGGER.info("%s: Write %d parameters", self.__host, count)
        # Give the heatpump a short time to handle the value changes/calculations:
        time.sleep(WAIT_TIME_AFTER_PARAMETER_WRITE)

    def _do_write_field(self, cmd, index, field, safe=True):
        """
        Write a single field to the Luxtronik controller.

        This method checks whether the field can be safely written,
        resets its write-pending flag, validates the raw value, and
        delegates the actual write operation to _do_write_raw().

        Args:
            cmd (int): Command specifying the type of write operation.
            index (int): Index of the field to write.
            field (Field): Field object containing the raw value and metadata.
            safe (bool): If True, perform safety checks before writing.

        Returns:
            bool: True if the write operation was executed, otherwise False.
        """
        # Reset the write_pending flag
        field.write_pending = False
        value = field.raw
        if not field.check_for_write(safe):
            LOGGER.warning(f"{self.__host} - Write: Parameter id '{index}'" \
                + f" or value '{value}' invalid!")
            return False
        return self._do_write_raw(cmd, index, value)

    def _do_write_raw(self, cmd, index, value):
        """
        Write a single raw value to the Luxtronik controller.

        Args:
            cmd (int): Command specifying the type of data to write.
                Currently only LUXTRONIK_PARAMETERS_WRITE is supported.
            index (int): Index of the field to write.
            value (int): Value to write.

        Returns:
            bool: True if the write operation was executed, otherwise False.
        """
        if not isinstance(cmd, int):
            LOGGER.error(f"{self.__host} - Write: Command '{cmd}' invalid! Must be an integer.")
            return False
        if not isinstance(index, int):
            LOGGER.error(f"{self.__host} - Write: Index '{index}' invalid! Must be an integer.")
            return False
        if not isinstance(value, int):
            LOGGER.error(f"{self.__host} - Write: Value '{value}' invalid! Must be an integer.")
            return False
        LOGGER.debug(f"{self.__host} - Write: Index '{index}' set to '{value}'")
        self._send_ints(cmd, index, value)
        command = self._read_int()
        LOGGER.debug(f"{self.__host} - Write: Command {command}")
        idx = self._read_int()
        LOGGER.debug(f"{self.__host} - Write: Index {idx}")
        return (command == cmd) and (index == idx)

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

    def _write_parameter(self, def_field_name_or_idx, value=None, safe=True):
        """
        Write a single parameter to the Luxtronik controller. Primarily used for debug purposes.

        Args:
            def_field_name_or_idx (LuxtronikDefinition | Base | str | int):
                Target to write to. May be a definition, a field, a name, or an index.
                Unknown indices can be written, but the safe flag must be set to false for that.
            value (int): Value to write. Overrides the field's value if a field is provided.
            safe (bool): If True, prevents writing if the field's writeable flag is not set.

        Returns:
            bool: True if the write operation was executed, otherwise False.
        """
        definition, field = get_check_and_create_def_field_pair(def_field_name_or_idx, PARAMETERS_DEFINITIONS, self.__version)

        if definition is None or field is None:
            name_or_idx = resolve_name_or_idx_input(def_field_name_or_idx)
            if isinstance(name_or_idx, int) and not safe:
                index = name_or_idx
                return self._do_write_raw(LUXTRONIK_PARAMETERS_WRITE, index, value)
            else:
                LOGGER.warning(f"{self.__host} - Write: Target '{def_field_name_or_idx}' invalid!")
                return False

        if value is not None:
            field.value = value

        result = self._do_write_field(LUXTRONIK_PARAMETERS_WRITE, definition.index, field, safe)

        # Give the heatpump a short time to handle the value changes/calculations:
        time.sleep(WAIT_TIME_AFTER_PARAMETER_WRITE)

        return result

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
            # skip this field if not supported by the controller
            if not definition.version.matches(self.__version):
                continue
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
        if self.__version == VER_IGNORE:
            for index in undefined:
                # LOGGER.warning(f"Entry '%d' not in list of {self.name}", index)
                definition = data_vector.definitions.create_unknown_definition(index)
                field = definition.create_field()
                integrate_data(definition, field, raw_data, LUXTRONIK_CFI_REGISTER_BIT_SIZE, index)
                data_vector.data.add_sorted(definition, field)
