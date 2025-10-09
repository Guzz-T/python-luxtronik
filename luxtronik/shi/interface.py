import logging

from luxtronik.datatypes import Base
from luxtronik.shi.holdings import Holdings
from luxtronik.shi.inputs import Inputs
from luxtronik.shi.common import (
    LuxtronikSmartHomeReadTelegram,
    LuxtronikSmartHomeWriteTelegram,
    ContiguousDataBlock,
)


LOGGER = logging.getLogger("Luxtronik.SmartHomeInterface")

class LuxtronikSmartHomeData:
    """
    Container for the smart home interface data vectors.

    Holds both the `holdings` and `inputs` data structures that represent
    the smart-home data exposed by the Luxtronik controller.
    """

    def __init__(self, holdings=None, inputs=None, safe=True):
        """
        Initialize a LuxtronikSmartHomeData instance.

        Args:
            holdings (Holdings): Optional holdings data vector. If not provided,
                a new `Holdings` instance is created.
            inputs (Inputs): Optional inputs data vector. If not provided,
                a new `Inputs` instance is created.
            safe (bool): Flag passed to the `Holdings` constructor when creating
                a new instance. Defaults to True.
        """
        self.holdings = holdings if holdings is not None else Holdings(safe)
        self.inputs = inputs if inputs is not None else Inputs()

    @classmethod
    def empty(cls, safe=True):
        self.holdings = Holdings.empty(safe)
        self.inputs = Inputs.empty()

    def versioned(cls, version):
        self.holdings = Holdings.empty(version, safe)
        self.inputs = Inputs.empty(version)


###############################################################################
# Smart home interface
###############################################################################

class LuxtronikSmartHomeInterface:
    """
    Read/write interface for Luxtronik smart home registers.

    This class builds on the simple addr/count/data interface and
    provides indexing and name resolution for easier access.

    Each register must be read individually to avoid transmission errors
    caused by non-existent intervening registers.
    Combine contiguous registers to optimize read/write access.
    """

    def __init__(self, interface, version):
        """
        Initialize the smart home interface.

        Args:
            interface: The underlying read/write interface.
            holdings_definitions: Definitions for holding indexing and name resolution
            inputs_definitions: Definitions for input indexing and name resolution
        """
        self._interface = interface
        self._version = version

        #self._holdings_definitions = holdings_definitions
        #self._inputs_definitions = inputs_definitions


# Helper methods ##############################################################

    def version(self):
        return self._version

    def _get_index_from_name(self, name):
        """
        Extract the index from an 'unknown' identifier (e.g. 'Unknown_Input_105').

        Args:
            name (str): The identifier string.

        Returns:
            int | None: The extracted index, or None if it cannot be determined.
        """
        parts = name.split("_")
        if len(parts) >= 3 and parts[2].isdigit():
            return int(parts[2])
        return None

    def _get_definition(self, name_or_idx, definitions):
        """
        Retrieve the definition for the given name or index.

        If no definition is found, attempt to generate a temporary one.
        If this also fails, return None.

        Args:
            name_or_idx (str | int): The field name or the register index.
            definitions (LuxtronikFieldDefinitions): Field definition list to look-up the desired definition

        Returns:
            LuxtronikFieldDefinition | None: A valid definition, or None if not found.
        """
        # Try to get the definition directly
        definition = definitions.get(name_or_idx)
        if definition is not None:
            return definition

        LOGGER.warning(
            f"Definition for {name_or_idx} not found. Attempting to create a temporary one."
        )

        # Handle unknown names like 'Unknown_Input_105'
        if isinstance(name_or_idx, str) and name_or_idx.lower().startswith("unknown"):
            index = self._get_index_from_name(name_or_idx)
            if index is None:
                LOGGER.warning(
                    "Cannot determine index from name '{name_or_idx}'. Use format 'Unknown_Input_INDEX'."
                )
                return None
            return definitions.create_unknown_definition(index)

        # Handle integer indices
        if isinstance(name_or_idx, int):
            return definitions.create_unknown_definition(name_or_idx)

        LOGGER.warning(f"Could not find or generate a definition for {name_or_idx}.")
        return None


# Common methods ##############################################################

    def _send_and_integrate(self, blocks_handler):
        """
        Read or write the data for multiple fields (a single field may correspond to multiple registers)
        using the contiguous-data-blocks-handler. Subsequently, the retrieved data
        is integrated into the provided fields.

        Args:
            blocks_handler (ContiguousDataBlocksHandler): Handler that groups fields into contiguous blocks.
        """
        # Convert the list of contiguous blocks to telegrams
        telegrams = blocks_handler.create_telegrams()
        # Send all telegrams. The retrieved data is returned within the telegrams
        success = self._interface.send(telegrams)
        # Transfer the data from the telegrams into the fields
        success &= blocks_handler.integrate_data()
        return success

    def _collect_field(self, field_or_name_or_idx, definitions, read_not_write, data, safe):
        """
        Add a field (this may correspond to multiple registers) by name, index, or directly as a field object
        to the contiguous-data-blocks-handler

        Supports str (name), int (index), or field objects.
        If possible, return the field object that contains the read data.

        Args:
            field_or_name_or_idx (Base | str | int): Field object, field name, or register index.
            definitions (DataVectorSmartHome): List of definitions that contains the desired field.
            data (list[int] | None): Optional raw data to override the field's data.
            safe (bool): If True, aborts when the field is marked as non-writeable.

        Returns:
            Base | None: The field object with integrated data, or None if the read failed.
        """
        # Process the different input parameter variants
        if isinstance(field_or_name_or_idx, Base):
            name_or_idx = field_or_name_or_idx.name
            field = field_or_name_or_idx
        elif isinstance(field_or_name_or_idx, (str, int)):
            name_or_idx = field_or_name_or_idx
            field = None
        else:
            LOGGER.warning(f"Invalid input: field_or_name_or_idx={field_or_name_or_idx}")
            return None

        # Fetch the definition associated with the field, index or name
        definition = self._get_definition(name_or_idx, definitions)
        if definition is None or not definition.valid:
            LOGGER.warning(f"Cannot determine definition by {name_or_idx}.")
            return None

        # If the definition is valid, it is always possible to create a field
        if field is None:
            field = definition.create_field()

        # Abort if field is not writeable
        if not read_not_write and safe and not definition.writeable:
            LOGGER.warning(f"Field marked as non-writeable: name={definition.name}, data={field.raw}")
            return None

        # Override the field's data with the provided data
        if not read_not_write and data is not None:
            field.raw = data

        # Abort if insufficient data is provided
        if not read_not_write not definition.check_data(field):
            LOGGER.warning(f"SHI write failure. Data error / insufficient data provided: name={definition.name}, data={field.raw}")
            return None

        blocks_handler.collect(field, definition, read_not_write)

        return field


    def _collect_fields(self, data_vector, definitions, read_not_write, data):
        """
        Read the data of all fields within the given data vector.

        The provided callback method determines whether input or holding registers are read.
        The retrieved data is integrated into the data-vector fields.

        Args:
            data_vector (DataVectorSmartHome): The data vector class providing fields.
        """

        # Organize data into contiguous blocks
        for field, definition in data_vector:
            # Skip fields that do not carry user-data
            if not read_not_write and not field.set_by_user:
                continue
            # we ignore the returned fields
            !!!
            self._collect_field(field, definitions, read_not_write, None, data_vector.safe)


# Holding methods #############################################################

    def read_holding_raw(self, index, count=1):
        """
        Read a specified number of 16-bit registers starting at the given index.

        The required offset is added automatically.

        Args:
            index (int): The starting register index (without offset).
            count (int): Number of 16-bit registers to read. Defaults to 1.

        Returns:
            list[int] | None: On success the list of read register values.
        """
        telegram = LuxtronikSmartHomeReadTelegram(index + Holdings.offset, count)
        success = self._interface.send(telegram)
        return telegram.data if success else None

    def read_holding(self, field_or_name_or_idx):
        """
        Read the data of a single field (may correspond to multiple registers).

        The field can be specified by name (str), index (int), or directly as a field object.
        The required offset is added automatically.

        Args:
            field_or_name_or_idx (Base | str | int): Field name, register index,
                or field object.

        Returns:
            Base | None: The field object containing the read data, or None if the read failed.
        """
        blocks_handler = ContiguousDataBlocksHandler()
        field = self._collect_field(field_or_name_or_idx, Holdings, True, None, True)
        success = self._send_and_integrate(blocks_handler)
        return field if success else None

    def read_holdings(self, holdings=None):
        """
        Read the data of all fields within the holdings data vector.

        Args:
            holdings (Holdings | None): Optional existing holdings object to populate.
                If None is provided, a new instance is created.

        Returns:
            Holdings: The populated holdings data vector.
        """
        if holdings is None:
            holdings = Holdings()

        blocks_handler = ContiguousDataBlocksHandler()
        self._collect_fields(holdings, Holdings, True, None, True)
        self._send_and_integrate(blocks_handler)
        return holdings

    def write_holding_raw(self, index, data_arr):
        """
        Write all provided data to 16-bit registers at the specified index.

        The required offset is added automatically.

        Args:
            index (int): Starting register index (without offset).
            data_arr (list[int]): Values to be written to the registers.
        """
        telegram = LuxtronikSmartHomeWriteTelegram(index + Holdings.offset, data_arr)
        self._interface.send(telegram)

    def write_holding(self, field_or_name_or_idx, data=None, safe=True):
        """
        Write all provided data or the field's own data to a field.

        The field may correspond to multiple registers and can be specified by
        name (str), index (int), or directly as a field object.
        The required offset is added automatically.

        Args:
            field_or_name_or_idx (Base | str | int): Field name, register index, or field object.
            data (list[int] | None): Optional raw data to override the field's data.
            safe (bool): If True, aborts when the field is marked as non-writeable.

        Returns:
            Base | None: The written field object, or None if the write failed.
        """
        blocks_handler = ContiguousDataBlocksHandler()
        field = self._collect_field(field_or_name_or_idx, Holdings, False, data, safe)
        success = self._send_and_integrate(blocks_handler)
        return field if success else None

    def write_holdings(self, holdings):
        """
        Write the data of all fields within the holdings data vector.

        Args:
            holdings (Holdings): The holdings object containing field data.
                If None is provided, the write is aborted.
        """
        if holdings is None:
            LOGGER.warning("Abort SHI write! No data to write provided.")
            return

        blocks_handler = ContiguousDataBlocksHandler()
        self._collect_fields(holdings, Holdings, False, None, holdings.safe)
        self._send_and_integrate(blocks_handler)

# Inputs methods ##############################################################

    def read_input_raw(self, index, count=1):
        """
        Read a specified number of 16-bit registers starting at the given index.

        The required offset is added automatically.

        Args:
            index (int): The starting register index (without offset).
            count (int): Number of 16-bit registers to read. Defaults to 1.

        Returns:
            list[int] | None: On success the list of read register values.
        """
        telegram = LuxtronikSmartHomeReadTelegram(index + Inputs.offset, count)
        success = self._interface.send(telegram)
        return telegram.data if success else None

    def read_input(self, field_or_name_or_idx):
        """
        Read the data of a single field (may correspond to multiple registers).

        The field can be specified by name (str), index (int), or directly as a field object.
        The required offset is added automatically.

        Args:
            field_or_name_or_idx (Base | str | int): Field name, register index,
                or field object.

        Returns:
            Base | None: The field object containing the read data, or None if the read failed.
        """
        blocks_handler = ContiguousDataBlocksHandler()
        field = self._collect_field(field_or_name_or_idx, Inputs, True, None, True)
        success = self._send_and_integrate(blocks_handler)
        return field if success else None

    def read_inputs(self, inputs=None):
        """
        Read the data of all fields within the inputs data vector.

        Args:
            inputs (Inputs | None): Optional existing inputs object to populate.
                If None is provided, a new instance is created.

        Returns:
            Inputs: The populated inputs data vector.
        """
        if inputs is None:
            inputs = Inputs()

        blocks_handler = ContiguousDataBlocksHandler()
        self._collect_fields(inputs, Inputs, True, None, True)
        self._send_and_integrate(blocks_handler)
        return inputs

# Full read/write methods #####################################################
# Be careful with method names!
# Identical named methods could be overridden in a derived class.

    def _shi_read(self, data):
        if data is None:
            data = LuxtronikSmartHomeData()

        blocks_handler = ContiguousDataBlocksHandler()
        self._collect_fields(data.holdings, Holdings, True, None, True)
        self._collect_fields(data.inputs, Inputs, True, None, True)
        self._send_and_integrate(blocks_handler)
        return data

    def _shi_write(self, holdings):
        self.write_holdings(holdings)

    def _shi_write_and_read(self, holdings, data=None):
        if holdings is None:
            LOGGER.warning("Abort SHI write and read! No data to write provided.")
            return
        if data is None:
            data = LuxtronikSmartHomeData()

        blocks_handler = ContiguousDataBlocksHandler()
        self._collect_fields(holdings, Holdings, False, None, holdings.safe)
        self._collect_fields(data.holdings, Holdings, True, None, True)
        self._collect_fields(data.inputs, Inputs, True, None, True)
        self._send_and_integrate(blocks_handler)
        return data

    def read(self, data=None):
        return self._shi_read(data)

    def write(self, holdings):
        self._shi_write(holdings)

    def write_and_read(self, holdings, data=None):
        return self._shi_write_and_read(holdings, data)