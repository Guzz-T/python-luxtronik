import logging

from luxtronik.datatypes import Base
from luxtronik.holdings import Holdings
from luxtronik.inputs import Inputs
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
    ContiguousDataBlock,
)
from luxtronik.shi.modbus import LuxtronikModbusTcpInterface


LOGGER = logging.getLogger("Luxtronik.SmartHomeInterface")

class LuxtronikSmartHomeData:
    """
    Collection of the inputs and holdings data vector.
    """

    def __init__(self, holdings=None, inputs=None, safe=True):
        """
        Create an luxtronik-smart-home-interface-data-object instance.
        Additionally, create the data vectors if they were not provided.
        """
        self.holdings = Holdings(safe) if holdings is None else holdings
        self.inputs = Inputs() if inputs is None else inputs


###############################################################################
# Smart home interface
###############################################################################

class LuxtronikSmartHomeInterface:
    """
    Luxtronik read/write interface for the smart home registers.
    This class builds on the simple addr/count/data interface and provides indexing and name resolution.
    """

    def __init__(self, interface):
        self._interface = interface

    @classmethod
    def ModbusTcp(cls, host, port=LUXTRONIK_DEFAULT_MODBUS_PORT, timeout=LUXTRONIK_DEFAULT_MODBUS_TIMEOUT):
        "Convenience function to directly create this interface using a Modbus read/write interface."
        modbus_interface = LuxtronikModbusTcpInterface(host, port, timeout)
        return cls(modbus_interface)


# Helper methods ##############################################################

    def _get_index_from_name(self, name):
        """
        Extract the index of an 'unknown' identifier (e.g. Unknown_Input_105).
        Return `None` if it was not possible to determine the index.
        """
        name_parts = name.split("_")
        if len(name_parts) >= 3 and name_parts[2].isdigit():
            return int(name_parts[2])
        return None

    def _get_definition(name_or_idx, data_vector_class):
        """
        Search for the appropriate definition of the provided name or index.
        If not found, attempt to generate a temporary definition out of the given data.
        If this also fails, return `None`.
        Note: A returned definition is always valid.
        """
        # Try to get the appropriate definition
        definition = data_vector_class._get_definition(name_or_idx)
        if definition is not None:
            LOGGER.warning("Definition for {name_or_idx} not found. Try to temporarily create one with default values.")

            # Attempt to extract the index and generate a temporary definition based on it
            if isinstance(name_or_idx, str) and name_or_idx.lower().startswith("unknown"):
                index = self._get_index_from_name(name_or_idx)
                if index is None:
                    LOGGER.warning(f"Cannot determine index by name: name={name}. Use Unknown_Input_INDEX for example.")
                    return None
                definition = LuxtronikFieldDefinition.unknown(index, data_vector_class.name)

            # Attempt to generate a temporary definition from the provided index
            if isinstance(name_or_idx, int)
                definition = LuxtronikFieldDefinition.unknown(name_or_idx, data_vector_class.name)

        if definition is None:
            Logger.warning(f"Could not find or generate a definition for {name_or_idx}.")
        return definition

# Common read methods #########################################################

    def _read_fields_via_handler(self, blocks_handler, data_vector_class, read_cb):
        """
        Read the data for multiple fields (a single field may correspond to multiple registers)
        using the contiguous-data-blocks-handler.
        The provided callback method determines whether input or holding registers are read.
        Subsequently, the retrieved data is integrated into the provided fields.
        """
        # Convert the list of contiguous blocks to read telegrams
        telegrams = blocks_handler.create_read_telegrams(data_vector.offset)
        # Read all data. The retrieved data is returned within the telegrams
        read_cb(telegrams)
        # Transfer the data from the telegrams into the fields
        blocks_handler.integrate_data()

    def _read_field(self, field_or_name_or_idx, data_vector_class, read_cb):
        """
        Read the data of a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        If possible, return the field object that contains the read data.
        The provided callback method determines whether input or holding registers are read.
        """
        # Process the different input parameter variants
        if isinstance(field_or_name_or_idx, Base):
            name_or_idx = field_or_name_or_idx.name
            field = field_or_name_or_idx
        elif isinstance(field_or_name_or_idx, str):
            name_or_idx = field_or_name_or_idx
            field = None
        elif isinstance(field_or_name_or_idx, int):
            name_or_idx = field_or_name_or_idx
            field = None
        else:
            self.LOGGER.warning(f"Abort SHI read. Invalid input: field_or_name_or_idx={field_or_name_or_idx}")
            return None

        # Fetch the definition associated with the field, index or name
        definition = self._get_definition(name_or_idx, data_vector_class)
        if definition is None or not definition.valid:
            LOGGER.warning(f"Abort SHI read. Cannot determine definition by {name_or_idx}.")
            return None

        # If the definition is valid, it is always possible to create a field
        if field is None:
            field = definition.create_field()

        # Create a blocks handler to be able to use the same function as _read_fields
        blocks_handler = ContiguousDataBlocksHandler()
        blocks_handler.collect(field, definition)

        self._read_fields_via_handler(blocks_handler, data_vector, read_cb)
        return field

    def _read_fields(self, data_vector, read_cb):
        """
        Read the data of all fields within the data_vector.
        The provided callback method determines whether input or holding registers are read.
        The retrieved data is integrated into the data-vector fields.
        """
        # Each register must be read individually to avoid transmission errors
        # caused by non-existent intervening registers.
        # Combine contiguous registers to optimize read access.
        blocks_handler = ContiguousDataBlocksHandler()

        # Organize data into contiguous blocks
        for field in data_vector:
            # Fetch the definition associated with the field
            definition = self._get_definition(field.name, data_vector_class)
            if definition is None or not definition.valid:
                LOGGER.warning(f"Skip reading SHI field {field.name}. Cannot determine definition.")
                continue
            blocks_handler.collect(field, definition)

        self._read_fields_via_handler(blocks_handler, data_vector, read_cb)

# Common write methods ########################################################

    def _write_fields_via_handler(self, blocks_handler, data_vector_class, write_cb):
        """
        Write multiple fields (a single field may correspond to multiple registers)
        using the contiguous-data-blocks-handler.
        """
        # Convert the list of contiguous blocks to write telegrams
        telegrams = blocks_handler.create_write_telegrams(data_vector.offset)
        # Write down all data
        write_cb(telegrams)

    def _write_field(self, field_or_name_or_idx, data_vector_class, write_cb, data, safe):
        """
        Write all provided data (`data`) or the field-data to a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        """
        # Process the different input parameter variants
        if isinstance(field_or_name_or_idx, Base):
            name_or_idx = field_or_name_or_idx.name
            field = field_or_name_or_idx
        elif isinstance(field_or_name_or_idx, str):
            name_or_idx = field_or_name_or_idx
            field = None
        elif isinstance(field_or_name_or_idx, int):
            name_or_idx = field_or_name_or_idx
            field = None
        else:
            self.LOGGER.warning(f"Abort SHI write. Passed data invalid: field_or_name_or_idx={field_or_name_or_idx}")
            return None

        # Fetch the definition associated with the field, index or name
        definition = self._get_definition(name_or_idx, data_vector_class)
        if definition is None or not definition.valid:
            LOGGER.warning(f"Abort SHI write. Cannot determine definition by {name_or_idx}.")
            return None

        # If the definition is valid, it is always possible to create a field
        if field is None:
            field = definition.create_field()

        # Override the field's data with the provided data
        if data is not None:
            field.raw = data

        # Abort if field is not writeable
        if safe and not definition.writeable:
            self.LOGGER.warning(f"SHI write failure. Field marked as non-writeable: name={definition.name}, data={field.raw}")
            return None

        # Abort if insufficient data is provided
        if not definition.check_data(field):
            self.LOGGER.warning(f"SHI write failure. Data error / insufficient data is provided: name={definition.name}, data={field.raw}")
            return None

        # Create a blocks handler to be able to use the same function as _write_fields
        blocks_handler = ContiguousDataBlocksHandler()
        blocks_handler.collect(field, definition)

        self._write_fields_via_handler(blocks_handler, data_vector_class, write_cb)

    def _write_fields(self, data_vector, write_cb):
        """
        Write the data of all fields within the data_vector.
        """
        # Each register must be written individually to avoid transmission errors
        # caused by non-existent intervening registers.
        # Combine contiguous registers to optimize write access.
        blocks_handler = ContiguousDataBlocksHandler()

        # Organize data into contiguous blocks
        for  field in data_vector:
            # Skip fields that do not carry user-data
            if not field.set_by_user:
                continue
            # Fetch the definition associated with the field
            definition = self._get_definition(field.name, data_vector_class)
            if definition is None or not definition.valid:
                LOGGER.warning(f"Skip SHI write. Cannot determine definition by {field.name}.")
                continue
            # Skip if field is not writeable
            if data_vector.safe and not writeable:
                self.LOGGER.warning(f"Skip SHI write. Field marked as non-writeable: field={field.name}")
                continue
            # Abort if insufficient data is provided
            if not definition.check_data(field):
                self.LOGGER.warning(f"SHI write failure. Data error / insufficient data is provided: name={definition.name}, data={field.raw}")
                continue
            blocks_handler.collect(field, definition)

        self._write_fields_via_handler(blocks_handler, data_vector_class, write_cb)

# Holding methods #############################################################

    def read_holding_raw(self, index, count=1):
        """
        Read the specified number of 16-bit registers ('count') from the given index ('index').
        The required offset is added automatically.
        Returns a list of read register values.
        """
        telegram = LuxtronikSmartHomeReadTelegram(index + Holdings.offset, count)
        self._interface.read_holdings(telegram)
        return telegram.data

    def read_holding(self, field_or_name_or_idx):
        """
        Read the data of a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        The required offset is added automatically.
        If possible, return the field object that contains the read data.
        """
        return self._read_field(field_or_name_or_idx, Holdings, self._interface.read_holdings)

    def read_holdings(self, holdings=None):
        """
        Read the data of all fields within the data_vector.
        Return the provided data-vector, or if None is provided, return the newly created data-vector
        that contains the read data.
        """
        if holdings is None:
            holdings = Holdings()
        self._read_fields(holdings, self._interface.read_holdings)
        return holdings

    def write_holding_raw(self, index, data_arr):
        """
        Write all provided data (`data_arr`) to 16-bit registers at the specified index (`index`).
        The required offset is added automatically.
        """
        telegram = LuxtronikSmartHomeWriteTelegram(index + Holdings.offset, data_arr)
        self._interface.write_holdings(telegram)

    def write_holding(self, field_or_name_or_idx, data=None, safe=True):
        """
        Write all provided data (`data`) or the field-data to a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        The required offset is added automatically.
        """
        self._write_field(field_or_name_or_idx, Holdings, self._interface.write_holdings, data, safe)

    def write_holdings(self, holdings):
        """
        Write the data of all fields within the data_vector.
        """
        if holdings is None:
            LOGGER.warning('Abort SHI write! No data to write provided.')
            return
        self._write_fields(holdings, self._interface.write_holdings)

# Inputs methods ##############################################################

    def read_input_raw(self, index, count=1):
        """
        Read the specified number of 16-bit registers ('count') from the given index ('index').
        The required offset is added automatically.
        Returns a list of read register values.
        """
        telegram = LuxtronikSmartHomeReadTelegram(index + Inputs.offset, count)
        self._interface.read_inputs(telegram)
        return telegram.data

    def read_input(self, field_or_name_or_idx):
        """
        Read the data of a field (this may correspond to multiple registers) by name, index, or directly as a field object.
        Supports str (name), int (index), or field objects.
        The required offset is added automatically.
        If possible, return the field object that contains the read data.
        """
        return self._read_field(field_or_name_or_idx, Inputs, self._interface.read_inputs)

    def read_inputs(self, inputs=None):
        """
        Read the data of all fields within the data_vector.
        Return the provided data_vector, or if None is provided, return the newly created data_vector
        that contains the read data.
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