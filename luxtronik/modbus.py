
import logging
from pyModbusTCP.client import ModbusClient

from luxtronik.common import *
from luxtronik.datatypes import Base
from luxtronik.holdings import Holdings
from luxtronik.inputs import Inputs
from luxtronik.constants import (
    LUXTRONIK_DEFAULT_MODBUS_PORT,
    LUXTRONIK_DEFAULT_MODBUS_TIMEOUT,
    LUXTRONIK_WAIT_TIME_AFTER_PARAMETER_WRITE,
)


LOGGER = logging.getLogger("Luxtronik.Modbus")


class LuxtronikSmartHomeData:

    def __init__(self, holdings=None, inputs=None, safe=True):
        self.holdings = Holdings(safe) if holdings is None else holdings
        self.inputs = Inputs() if inputs is None else inputs


###############################################################################
# Helper classes for contiguos data
###############################################################################

class ContiguousBlockData:

    def __init__(self, index, count, field, definition, data_arr):
        self.index = index
        self.count = count
        self.field = field
        self.definition = definition
        self.data_arr = data_arr

    def __str__(self):
        return f"({self.index}, {self.count})"

class ContiguousBlock:

    def __init__(self):
        self._contiguous_list = []

    def __iter__(self):
        return iter(self._contiguous_list)

    def __str__(self):
        list_str = ""
        for entry in self._contiguous_list:
            list_str += f" {entry},"
        list_str = "[" + list_str[1:-1] + "]"
        return f"index: {self.first_index}, count: {self.overall_count}, list: {list_str}"

    def add(self, index, count, field, definition, data_arr=[None]):
        entry = ContiguousBlockData(index, count, field, definition, data_arr)
        self._contiguous_list += [entry]

    @property
    def first_index(self):
        if len(self._contiguous_list) > 0:
            return self._contiguous_list[0].index
        else:
            return 0

    @property
    def overall_count(self):
        count = 0
        for entry in self._contiguous_list:
            count += entry.count
        return count

    def integrate_data(self, data_arr):
        first = self.first_index
        for entry in self._contiguous_list:
            offset = entry.index - first
            entry.field.raw = entry.definition.extract_raw(data_arr, offset)

    def get_data_arr(self):
        data_arr = []
        for entry in self._contiguous_list:
            data_arr += entry.data_arr
        return data_arr


###############################################################################
# Modbus interface
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

    def __del__(self):
        pass

    @property
    def _modbus_lock(self):
        return hosts_locks[self._host]


# Helper methods ##############################################################

    def _get_index_from_name(self, name):
        """Extract the index of an 'unknown' identifier (e.g. Unknown_Input_105)."""
        name_parts = name.split("_")
        if len(name_parts) >= 3 and name_parts[2].isdigit():
            return int(name_parts[2])
        return None


# Common read methods #########################################################

    def _read_register(self, read_reg_cb, addr, count=1):
        """
        Read the specified number of 16-bit registers ('count') from the given Modbus address ('addr').
        The address is used directly without applying additional offsets.
        The provided callback method determines whether input or holding registers are read.
        Returns a list of read register values.
        """
        if count <= 0:
            print(f"Modbus read operation aborted. No data requested: addr={addr}, count={count}")
            return [None]

        with self._modbus_lock:
            if not self._client.open():
                print(f"Modbus connection failed: addr={addr}, count={count}")
                self._client.close()
                return [None] * count

            data_arr = read_reg_cb(addr, count)
            self._client.close()

            # Return an array as the output if the read operation fails.
            if data_arr is None:
                print(f"Modbus read operation failed: addr={addr}, count={count}")
                return [None] * count

            if len(data_arr) < count:
                data_arr += [0] * (count - len(data_arr))
                print(f"Modbus read operation failed: addr={addr}, count={count}")
            elif len(data_arr) > count:
                data_arr = data_arr[:count]
                print(f"Modbus read operation failed: addr={addr}, count={count}")

            return data_arr

    def _read_register_by_name(self, name, data_vector_class, read_raw_cb):
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
                print(f"Abort modbus read. Cannot determine address by name: name={name}")
                return None
            count = 1
            field = data_vector_class.create_unknown(index)
        else:
            print(f"Abort modbus read. Cannot determine address by name: name={name}")
            return None

        addr = index + data_vector_class.offset
        data_arr = read_raw_cb(addr, count)
        field.raw = definition.extract_raw(data_arr, 0)
        return field

    def _read_register_by_field(self, field, data_vector_class, read_raw_cb):
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
                print(f"Abort modbus read. Cannot determine address by field: name={field.name}")
                return None
            count = 1
            field = data_vector_class.create_unknown(index)
        else:
            print(f"Abort modbus read. Cannot determine address by field: name={field.name}")
            return None

        addr = index + data_vector_class.offset
        data_arr = read_raw_cb(addr, count)
        field.raw = definition.extract_raw(data_arr, 0)
        return field

    def _read_register_by_index(self, index, data_vector_class, read_raw_cb):
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
        data_arr = read_raw_cb(addr, count)
        field.raw = definition.extract_raw(data_arr, 0)
        return field

    def _read_field(self, field_or_name_or_idx, data_vector_class, read_raw_cb):
        """
        Read a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        If possible, return the field object along with the read data.
        The provided callback method determines whether input or holding registers are read.
        """
        if isinstance(field_or_name_or_idx, Base):
            return self._read_register_by_field(field_or_name_or_idx, data_vector_class, read_raw_cb)
        elif isinstance(field_or_name_or_idx, str):
            return self._read_register_by_name(field_or_name_or_idx, data_vector_class, read_raw_cb)
        elif isinstance(field_or_name_or_idx, int):
            return self._read_register_by_index(field_or_name_or_idx, data_vector_class, read_raw_cb)
        else:
            print(f"Abort Modbus read. Invalid input: field_or_name_or_idx={field_or_name_or_idx}")
            return None

    def _read_fields(self, data_vector, read_raw_cb):
        """Read all fields within the data_vector."""

        # Each register must be read individually to avoid transmission errors
        # caused by non-existent intervening registers.
        # Contiguous register groups to optimize Modbus reads
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
                contiguous.append(ContiguousBlock())
            # Add the current field's details to the contiguous block
            contiguous[-1].add(index, count, field, definition)
            next_index = index + count

        with self._modbus_lock:
            if not self._client.open():
                print(f"Modbus connection failed.")
                self._client.close()
                return

            # Process each contiguous block and read the data
            for entry in contiguous:

                index = entry.first_index
                count = entry.overall_count
                addr = index + data_vector.offset
                data_arr = read_raw_cb(addr, count)

                if data_arr is None:
                    print(f"Modbus read operation failed: addr={addr}, count={count}")
                    data_arr = [None]
                # Integrate the read data into the entry
                entry.integrate_data(data_arr)

            self._client.close()


# Common write methods ########################################################

    def _write_register(self, write_reg_cb, addr, data_arr):
        """
        Write all provided data (`data_arr`) to 16-bit registers at the specified Modbus address (`addr`).
        The address is used directly without applying additional offsets.
        The provided callback method determines whether input or holding registers are written.
        """
        if isinstance(data_arr, int):
            data_arr = [data_arr]
        if data_arr is None or len(data_arr) <= 0:
            print(f"Modbus write operation aborted. No data to write: addr={addr}, data={data_arr}")
            return

        with self._modbus_lock:
            if not self._client.open():
                print(f"Modbus connection failed: addr={addr}, count={count}")
                self._client.close()
                return

            # Write len(data_arr) x 16 bits registers at modbus address "addr"
            success = write_reg_cb(addr, data_arr)
            if not success:
                print(f"Modbus write error: addr={addr}, data={data_arr}")
            self._client.close()
            # Give the heatpump a short time to handle the value changes:
            time.sleep(LUXTRONIK_WAIT_TIME_AFTER_PARAMETER_WRITE)

    def _write_register_by_name(self, name, data_vector_class, write_raw_cb, data, safe):
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
                print(f"Abort modbus write. Cannot determine address by name: name={name}")
                return
            writeable = False
        else:
            print(f"Abort modbus write. Cannot determine address by name: name={name}")
            return

        addr = index + data_vector_class.offset
        if (not safe) or writeable:
            self.write_holding_raw(addr, data_arr)
        else:
            print(f"Modbus write failure. Field marked as non-writeable: name={name}, data={data_arr}")

    def _write_register_by_field(self, field, data_vector_class, write_raw_cb, data, safe):
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
                print(f"Abort modbus write. Cannot determine address by name: name={field.name}")
                return
            writeable = False
        else:
            print(f"Abort modbus write. Cannot determine address by name: name={field.name}")
            return

        addr = index + data_vector_class.offset
        if (not safe) or writeable:
            self.write_holding_raw(addr, data_arr)
        else:
            print(f"Modbus write failure. Field marked as non-writeable: name={field.name}, data={data_arr}")

    def _write_register_by_index(self, index, data_vector_class, write_raw_cb, data, safe):
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
            self.write_holding_raw(addr, data_arr)
        else:
            print(f"Modbus write failure. Field marked as non-writeable: idx={index}, data={data_arr}")

    def _write_field(self, field_or_name_or_idx, data_vector_class, write_raw_cb, data, safe):
        """
        Write all provided data (`data`) or the field-data to a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        The provided callback method determines whether input or holding registers are read.
        """
        if isinstance(field_or_name_or_idx, Base):
            return self._write_register_by_field(field_or_name_or_idx, data_vector_class, write_raw_cb, data, safe)
        elif isinstance(field_or_name_or_idx, str):
            return self._write_register_by_name(field_or_name_or_idx, data_vector_class, write_raw_cb, data, safe)
        elif isinstance(field_or_name_or_idx, int):
            return self._write_register_by_index(field_or_name_or_idx, data_vector_class, write_raw_cb, data, safe)
        else:
            print(f"Abort modbus write. Passed data invalid: field_or_name_or_idx={field_or_name_or_idx}")
            return None

    def _write_fields(self, data_vector, write_raw_cb):
        """Write all fields within the data_vector."""

        # Each register must be written individually to avoid transmission errors
        # caused by non-existent intervening registers.
        # Contiguous register groups to optimize Modbus writes
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
                print(f"Skip modbus write. Field marked as non-writeable: field={field.name}")
                continue
            data_arr = definition.get_raw(field)
            # Create a new contiguous block if the current index doesn't follow the previous
            if index != next_index:
                contiguous.append(ContiguousBlock())
            # Add the current field's details to the contiguous block
            contiguous[-1].add(index, count, field, definition, data_arr)
            next_index = index + count

        with self._modbus_lock:
            if not self._client.open():
                print(f"Modbus connection failed.")
                self._client.close()
                return

            # Process each contiguous block and write the data
            for entry in contiguous:

                index = entry.first_index
                data_arr = entry.get_data_arr()
                addr = index + data_vector.offset
                if not write_raw_cb(addr, data_arr):
                    print(f"Modbus write failure: addr={addr}, data={data_arr}")
            self._client.close()
            # Give the heatpump a short time to handle the value changes:
            time.sleep(LUXTRONIK_WAIT_TIME_AFTER_PARAMETER_WRITE)


# Holding methods #############################################################

    def read_holding_raw(self, addr, count=1):
        """
        Read the specified number of 16-bit registers ('count') from the given Modbus address ('addr').
        The address is used directly without applying additional offsets.
        Returns a list of read register values.
        """
        return self._read_register(self._client.read_holding_registers, addr, count)

    def read_holding(self, field_or_name_or_idx):
        """
        Read a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        If possible, return the field object along with the read data.
        """
        return self._read_field(field_or_name_or_idx, Holdings, self.read_holding_raw)

    def read_holdings(self, holdings=None):
        """
        Read all fields within the data_vector.
        Return the provided object, or if none is provided, return the newly created object.
        """
        if holdings is None:
            holdings = Holdings()
        self._read_fields(holdings, self._client.read_holding_registers)
        return holdings

    def write_holding_raw(self, addr, data_arr):
        """
        Write all provided data (`data_arr`) to 16-bit registers at the specified Modbus address (`addr`).
        The address is used directly without applying additional offsets.
        """
        self._write_register(self._client.write_multiple_registers, addr, data_arr)

    def write_holding(self, field_or_name_or_idx, data=None, safe=True):
        """
        Write all provided data (`data`) or the field-data to a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        """
        self._write_field(field_or_name_or_idx, Holdings, self.write_holding_raw, data, safe)

    def write_holdings(self, holdings):
        """
        Write all fields within the data_vector.
        Return the provided object, or if none is provided, return the newly created object.
        """
        self._write_fields(holdings, self._client.write_multiple_registers)


# Inputs methods ##############################################################

    def read_input_raw(self, register, count=1):
        """
        Read the specified number of 16-bit registers ('count') from the given Modbus address ('addr').
        The address is used directly without applying additional offsets.
        Returns a list of read register values.
        """
        return self._read_register(self._client.read_input_registers, register, count)

    def read_input(self, field_or_name_or_idx):
        """
        Read a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        If possible, return the field object along with the read data.
        """
        return self._read_field(field_or_name_or_idx, Inputs, self.read_input_raw)

    def read_inputs(self, inputs=None):
        """
        Read all fields within the data_vector.
        Return the provided object, or if none is provided, return the newly created object.
        """
        if inputs is None:
            inputs = Inputs()
        self._read_fields(inputs, self._client.read_input_registers)
        return inputs


# Full read/write methods #####################################################

    def read(self, data=None):
        if data is None:
            data = LuxtronikSmartHomeData()
        with self._modbus_lock:
            self.read_holdings(data.holdings)
            self.read_inputs(data.inputs)
        return data

    def write(self, holdings):
        with self._modbus_lock:
            self.write_holdings(holdings)

    def write_and_read(self, holdings, data=None):
        with self._modbus_lock:
            self.write(holdings)
            return self.read(data)