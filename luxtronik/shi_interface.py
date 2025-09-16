import logging

from luxtronik.datatypes import Base
from luxtronik.holdings import Holdings
from luxtronik.inputs import Inputs
from luxtronik.constants import (
    LUXTRONIK_DEFAULT_MODBUS_PORT,
    LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
    LUXTRONIK_WAIT_TIME_AFTER_PARAMETER_WRITE,
)
from luxtronik.shi_common import (
    LuxtronikSmartHomeReadTelegram,
    LuxtronikSmartHomeWriteTelegram,
    ContiguousDataBlock,
)
from luxtronik.shi_modbus import LuxtronikModbusTcpInterface


LOGGER = logging.getLogger("Luxtronik.SmartHomeInterface")

class LuxtronikSmartHomeData:

    def __init__(self, holdings=None, inputs=None, safe=True):
        self.holdings = Holdings(safe) if holdings is None else holdings
        self.inputs = Inputs() if inputs is None else inputs


###############################################################################
# Smart home interface
###############################################################################

class LuxtronikSmartHomeInterface:
    """
    Luxtronik read/write interface for the smart home registers.
    """

    def __init__(self, interface):
        self._interface = interface

    @classmethod
    def ModbusTcp(cls, host, port=LUXTRONIK_DEFAULT_MODBUS_PORT, timeout=LUXTRONIK_DEFAULT_MODBUS_TIMEOUT):
        modbus_interface = LuxtronikModbusTcpInterface(host, port, timeout)
        return cls(modbus_interface)


# Helper methods ##############################################################

    def _get_index_from_name(self, name):
        """Extract the index of an 'unknown' identifier (e.g. Unknown_Input_105)."""
        name_parts = name.split("_")
        if len(name_parts) >= 3 and name_parts[2].isdigit():
            return int(name_parts[2])
        return None

# Common read methods #########################################################

    def _read_register_by_name(self, name, data_vector_class, read_cb):
        """
        Read a field (this may correspond to multiple registers) based on its name.
        If possible, return the field object along with the read data.
        The provided callback method determines whether input or holding registers are read.
        """
        definition = data_vector_class._get_definition(name)

        if definition:
            # Use the definition details to read the register
            index = definition.index
            count = definition.count
            field = definition.create_field()
        elif name.startswith("Unknown"):
            # Handle 'Unknown' names by extracting the index
            index = self._get_index_from_name(name)
            if index is None:
                self.LOGGER.warning(f"Abort SHI read. Cannot determine address by name: name={name}")
                return None
            count = 1
            field = data_vector_class.create_unknown(index)
        else:
            self.LOGGER.warning(f"Abort SHI read. Cannot determine address by name: name={name}")
            return None

        addr = index + data_vector_class.offset
        telegram = LuxtronikSmartHomeReadTelegram(addr, count)
        read_cb(telegram)
        field.raw = definition.extract_raw(telegram.data, 0)
        return field

    def _read_register_by_field(self, field, data_vector_class, read_cb):
        """
        Read a field (this may correspond to multiple registers) based on its field object.
        If possible, return the field object along with the read data.
        The provided callback method determines whether input or holding registers are read.
        """
        definition = data_vector_class._get_definition(field.name)

        if definition:
            # Use the definition details to read the register
            index = definition.index
            count = definition.count
        elif field.name.startswith("Unknown"):
            # Handle 'Unknown' fields by extracting the index
            index = self._get_index_from_name(field.name)
            if index is None:
                self.LOGGER.warning(f"Abort SHI read. Cannot determine address by field: name={field.name}")
                return None
            count = 1
            field = data_vector_class.create_unknown(index)
        else:
            self.LOGGER.warning(f"Abort SHI read. Cannot determine address by field: name={field.name}")
            return None

        addr = index + data_vector_class.offset
        telegram = LuxtronikSmartHomeReadTelegram(addr, count)
        read_cb(telegram)
        field.raw = definition.extract_raw(telegram.data, 0)
        return field

    def _read_register_by_index(self, index, data_vector_class, read_cb):
        """
        Read a field (this may correspond to multiple registers) based on its index.
        If possible, return the field object along with the read data.
        The provided callback method determines whether input or holding registers are read.
        """
        definition = data_vector_class._get_definition(index)

        if definition:
            # Use the definition details to read the register
            index = definition.index
            count = definition.count
            field = definition.create_field()
        else:
            # For unknown, we use the passed index
            # index = index
            count = 1
            field = data_vector_class.create_unknown(index)

        addr = index + data_vector_class.offset
        telegram = LuxtronikSmartHomeReadTelegram(addr, count)
        read_cb(telegram)
        field.raw = definition.extract_raw(telegram.data, 0)
        return field

    def _read_field(self, field_or_name_or_idx, data_vector_class, read_cb):
        """
        Read a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        If possible, return the field object along with the read data.
        The provided callback method determines whether input or holding registers are read.
        """
        if isinstance(field_or_name_or_idx, Base):
            return self._read_register_by_field(field_or_name_or_idx, data_vector_class, read_cb)
        elif isinstance(field_or_name_or_idx, str):
            return self._read_register_by_name(field_or_name_or_idx, data_vector_class, read_cb)
        elif isinstance(field_or_name_or_idx, int):
            return self._read_register_by_index(field_or_name_or_idx, data_vector_class, read_cb)
        else:
            self.LOGGER.warning(f"Abort SHI read. Invalid input: field_or_name_or_idx={field_or_name_or_idx}")
            return None

    def _read_fields(self, data_vector, read_cb):
        """Read all fields within the data_vector."""

        # Each register must be read individually to avoid transmission errors
        # caused by non-existent intervening registers.
        # Contiguous register groups to optimize reads
        contiguous = []
        next_index = -1
        # Organize data into contiguous blocks
        for index, field in data_vector:
            # Fetch the definition associated with the field
            definition = data_vector._get_definition_by_idx(index)
            # Determine field information
            if definition:
                index = definition.index
                count = definition.count
            else:
                # index = index
                count = 1
            # Create a new contiguous block if the current index doesn't follow the previous
            if index != next_index:
                contiguous.append(ContiguousDataBlock())
            # Add the current field's details to the contiguous block
            contiguous[-1].add(index, count, field, definition)
            next_index = index + count

        # Process each contiguous block and read the data
        telegrams = []
        items = []
        for entry in contiguous:
            index = entry.first_index
            count = entry.overall_count
            addr = index + data_vector.offset
            telegram = LuxtronikSmartHomeReadTelegram(addr, count)
            telegrams += [telegram]
            items += [(entry, telegram)]

        read_cb(telegrams)

        for item in items:
            # Integrate the read data into the entry
            item[0].integrate_data(item[1].data)

# Common write methods ########################################################

    def _write_register_by_name(self, name, data_vector_class, write_cb, data, safe):
        """
        Write all provided data (`data`) to a field (this may correspond to multiple registers) based on its name.
        The provided callback method determines whether input or holding registers are written.
        """

        definition = data_vector_class._get_definition(name)
        data_arr = definition.get_data_arr(data)

        if definition:
            # Use the definition details to write the register
            index = definition.index
            writeable = definition.writeable
        elif name.startswith('Unknown'):
            # Handle 'Unknown' fields by extracting the index
            index = self._get_index_from_name(name)
            if index is None:
                self.LOGGER.warning(f"Abort SHI write. Cannot determine address by name: name={name}")
                return
            writeable = False
        else:
            self.LOGGER.warning(f"Abort SHI write. Cannot determine address by name: name={name}")
            return

        addr = index + data_vector_class.offset
        if (not safe) or writeable:
            telegram = LuxtronikSmartHomeWriteTelegram(addr, data_arr)
            write_cb(telegram)
        else:
            self.LOGGER.warning(f"SHI write failure. Field marked as non-writeable: name={name}, data={data_arr}")

    def _write_register_by_field(self, field, data_vector_class, write_cb, data, safe):
        """
        Write all provided data (`data`) or the field-data to a field (this may correspond to multiple registers) based on its field object.
        The provided callback method determines whether input or holding registers are written.
        """
        definition = data_vector_class._get_definition(field.name)
        if data is None:
            data_arr = definition.get_raw(field)
        else:
            data_arr = definition.get_data_arr(data)

        if definition:
            # Use the definition details to write the register
            index = definition.index
            writeable = definition.writeable
        elif field.name.startswith('Unknown'):
            # Handle 'Unknown' fields by extracting the index
            index = self._get_index_from_name(field.name)
            if index is None:
                self.LOGGER.warning(f"Abort SHI write. Cannot determine address by name: name={field.name}")
                return
            writeable = False
        else:
            self.LOGGER.warning(f"Abort SHI write. Cannot determine address by name: name={field.name}")
            return

        addr = index + data_vector_class.offset
        if (not safe) or writeable:
            telegram = LuxtronikSmartHomeWriteTelegram(addr, data_arr)
            write_cb(telegram)
        else:
            self.LOGGER.warning(f"SHI write failure. Field marked as non-writeable: name={field.name}, data={data_arr}")

    def _write_register_by_index(self, index, data_vector_class, write_cb, data, safe):
        """
        Write all provided data (`data`) to a field (this may correspond to multiple registers) based on its index.
        The provided callback method determines whether input or holding registers are written.
        """
        definition = data_vector_class._get_definition(index)
        data_arr = definition.get_data_arr(data)

        if definition:
            # Use the definition details to write the register
            index = definition.index
            writeable = definition.writeable
        else:
            # Handle 'Unknown' fields by extracting the index
            # index = index
            writeable = False

        addr = index + data_vector_class.offset
        if (not safe) or writeable:
            telegram = LuxtronikSmartHomeWriteTelegram(addr, data_arr)
            write_cb(telegram)
        else:
            self.LOGGER.warning(f"SHI write failure. Field marked as non-writeable: idx={index}, data={data_arr}")

    def _write_field(self, field_or_name_or_idx, data_vector_class, write_cb, data, safe):
        """
        Write all provided data (`data`) or the field-data to a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        The provided callback method determines whether input or holding registers are read.
        """
        if isinstance(field_or_name_or_idx, Base):
            return self._write_register_by_field(field_or_name_or_idx, data_vector_class, write_cb, data, safe)
        elif isinstance(field_or_name_or_idx, str):
            return self._write_register_by_name(field_or_name_or_idx, data_vector_class, write_cb, data, safe)
        elif isinstance(field_or_name_or_idx, int):
            return self._write_register_by_index(field_or_name_or_idx, data_vector_class, write_cb, data, safe)
        else:
            self.LOGGER.warning(f"Abort SHI write. Passed data invalid: field_or_name_or_idx={field_or_name_or_idx}")
            return None

    def _write_fields(self, data_vector, write_cb):
        """Write all fields within the data_vector."""

        # Each register must be written individually to avoid transmission errors
        # caused by non-existent intervening registers.
        # Contiguous register groups to optimize writes
        contiguous = []
        next_index = -1
        # Organize data into contiguous blocks
        for index, field in data_vector:
            # Skip fields that do not carry user-data
            if not field.set_by_user:
                continue
            # Fetch the definition associated with the field
            definition = data_vector._get_definition_by_idx(index)
            # Determine field information
            if definition:
                index = definition.index
                count = definition.count
                writeable = definition.writeable
            else:
                # index = index
                count = 1
                writeable = False
            if data_vector.safe and not writeable:
                self.LOGGER.warning(f"Skip SHI write. Field marked as non-writeable: field={field.name}")
                continue
            data_arr = definition.get_raw(field)
            # Create a new contiguous block if the current index doesn't follow the previous
            if index != next_index:
                contiguous.append(ContiguousDataBlock())
            # Add the current field's details to the contiguous block
            contiguous[-1].add(index, count, field, definition, data_arr)
            next_index = index + count

        # Process each contiguous block and read the data
        telegrams = []
        for entry in contiguous:
            index = entry.first_index
            data_arr = entry.get_data_arr()
            addr = index + data_vector.offset
            telegram = LuxtronikSmartHomeWriteTelegram(addr, data_arr)
            telegrams += [telegram]

        write_cb(telegrams)


# Holding methods #############################################################

    def read_holding_raw(self, index, count=1):
        """
        Read the specified number of 16-bit registers ('count') from the given index ('index').
        Returns a list of read register values.
        """
        telegram = LuxtronikSmartHomeReadTelegram(index + Holdings.offset, count)
        self._interface.read_holdings(telegram)
        return telegram.data

    def read_holding(self, field_or_name_or_idx):
        """
        Read a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        If possible, return the field object along with the read data.
        """
        return self._read_field(field_or_name_or_idx, Holdings, self._interface.read_holdings)

    def read_holdings(self, holdings=None):
        """
        Read all fields within the data_vector.
        Return the provided object, or if none is provided, return the newly created object.
        """
        if holdings is None:
            holdings = Holdings()
        self._read_fields(holdings, self._interface.read_holdings)
        return holdings

    def write_holding_raw(self, index, data_arr):
        """
        Write all provided data (`data_arr`) to 16-bit registers at the specified address (`index`).
        The address is used directly without applying additional offsets.
        """
        telegram = LuxtronikSmartHomeWriteTelegram(index + Holdings.offset, data_arr)
        self._interface.write_holdings(telegram)

    def write_holding(self, field_or_name_or_idx, data=None, safe=True):
        """
        Write all provided data (`data`) or the field-data to a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        """
        self._write_field(field_or_name_or_idx, Holdings, self._interface.write_holdings, data, safe)

    def write_holdings(self, holdings):
        """
        Write all fields within the data_vector.
        Return the provided object, or if none is provided, return the newly created object.
        """
        self._write_fields(holdings, self._interface.write_holdings)

# Inputs methods ##############################################################

    def read_input_raw(self, index, count=1):
        """
        Read the specified number of 16-bit registers ('count') from the given address ('index').
        The address is used directly without applying additional offsets.
        Returns a list of read register values.
        """
        telegram = LuxtronikSmartHomeReadTelegram(index + Inputs.offset, count)
        self._interface.read_inputs(telegram)
        return telegram.data

    def read_input(self, field_or_name_or_idx):
        """
        Read a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        If possible, return the field object along with the read data.
        """
        return self._read_field(field_or_name_or_idx, Inputs, self._interface.read_inputs)

    def read_inputs(self, inputs=None):
        """
        Read all fields within the data_vector.
        Return the provided object, or if none is provided, return the newly created object.
        """
        if inputs is None:
            inputs = Inputs()
        self._read_fields(inputs, self._interface.read_inputs)
        return inputs

# Full read/write methods #####################################################
# Be careful with method names!
# Identical named methods could be overridden in a derived class.

    def _shi_read(self, data):
        if data is None:
            data = LuxtronikSmartHomeData()
        self.read_holdings(data.holdings)
        self.read_inputs(data.inputs)
        return data

    def _shi_write(self, holdings):
        self.write_holdings(holdings)

    def read(self, data=None):
        return self._shi_read(data)

    def write(self, holdings):
        self._shi_write(holdings)

    def write_and_read(self, holdings, data=None):
        self._shi_write(holdings)
        return self._shi_read(data)