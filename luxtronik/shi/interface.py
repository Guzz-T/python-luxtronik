from luxtronik.datatypes import Base
from luxtronik.shi.constants import LUXTRONIK_LATEST_SHI_VERSION
from luxtronik.shi.common import (
    LOGGER,
    version_in_range,
    LuxtronikSmartHomeReadTelegram,
    LuxtronikSmartHomeWriteTelegram,
)
from luxtronik.shi.definitions import check_data
from luxtronik.shi.holdings import Holdings, HOLDINGS_DEFINITIONS
from luxtronik.shi.inputs import Inputs, INPUTS_DEFINITIONS
from luxtronik.shi.contiguous import ContiguousDataBlockList


###############################################################################
# Smart home interface data
###############################################################################

class LuxtronikSmartHomeData:
    """
    Container for the smart home interface data vectors.

    Holds both the `holdings` and `inputs` data structures that represent
    the smart-home data exposed by the Luxtronik controller.
    """

    def __init__(
        self,
        holdings=None,
        inputs=None,
        version=LUXTRONIK_LATEST_SHI_VERSION,
        safe=True
    ):
        """
        Initialize a LuxtronikSmartHomeData instance.

        Args:
            holdings (Holdings): Optional holdings data vector. If not provided,
                a new `Holdings` instance is created.
            inputs (Inputs): Optional inputs data vector. If not provided,
                a new `Inputs` instance is created.
            version (tuple[int] | None): Version to be used for creating the data vectors.
                This ensures that the data vectors only contain valid fields.
                If None is passed, all available fields are added.
                (default: LUXTRONIK_LATEST_SHI_VERSION)
            safe (bool): Flag passed to the `Holdings` constructor when creating
                a new instance. Defaults to True.
        """
        self.holdings = holdings if holdings is not None else Holdings(version, safe)
        self.inputs = inputs if inputs is not None else Inputs(version)

    @classmethod
    def empty(
        cls,
        version=LUXTRONIK_LATEST_SHI_VERSION,
        safe=True
    ):
        """
        Initialize an empty LuxtronikSmartHomeData instance
        (= no fields are added to the data-vectors).

        Args:
            version (tuple[int] | None): The version is added to the data vectors
                so some checks can be performed later.
                (default: LUXTRONIK_LATEST_SHI_VERSION)
            safe (bool): Flag passed to the `Holdings` constructor when creating
                a new instance. Defaults to True.
        """
        obj = cls.__new__(cls)
        obj.holdings = Holdings.empty(version, safe)
        obj.inputs = Inputs.empty(version)
        return obj

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

    def __init__(self, interface, version=LUXTRONIK_LATEST_SHI_VERSION):
        """
        Initialize the smart home interface.

        Args:
            interface: The underlying read/write interface.
            holdings_definitions: Definitions for holding indexing and name resolution
            inputs_definitions: Definitions for input indexing and name resolution
        """
        self._interface = interface
        self._version = version

    @property
    def version(self):
        return self._version


# Creator methods #############################################################

    def create_holding(self, name_or_idx):
        definition = HOLDING_DEFINITIONS.get(name_or_idx)
        if definition is not None and version_in_range(self._version, definition.since, definition.until):
            return definition.create_field()
        return None

    def create_holdings(self, safe=True):
        return Holdings(self._version, safe)

    def create_empty_holdings(self, safe=True):
        return Holdings.empty(self._version, safe)

    def create_input(self, name_or_idx):
        definition = INPUT_DEFINITIONS.get(name_or_idx)
        if definition is not None and version_in_range(self._version, definition.since, definition.until):
            return definition.create_field()
        return None

    def create_inputs(self):
        return Inputs(self._version, True)

    def create_empty_inputs(self):
        return Inputs.empty(self._version, True)

    def create_data(self, safe=True):
        return LuxtronikSmartHomeData(self._version, safe)

    def create_empty_data(self, safe=True):
        return LuxtronikSmartHomeData.empty(self._version, safe)

# Helper methods ##############################################################

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
            definitions (LuxtronikDefinitionsList): Field definition list to look-up the desired definition

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


# Telegram methods ############################################################

    def _create_read_telegram(self, block, telegram_type):
        """
        Create a read-telegram of type `telegram_type` out of this `ContiguousDataBlock`.

        Args:
            telegram_type (class of LuxtronikSmartHomeReadTelegram):
                Type of the telegram to create.

        Returns:
            LuxtronikSmartHomeReadTelegram:
                The created telegram.
        """
        return telegram_type(block.first_addr, block.overall_count)

    def _create_write_telegram(self, block, telegram_type):
        """
        Create a write-telegram of type `telegram_type` out of this `ContiguousDataBlock`.

        Args:
            telegram_type (class of LuxtronikSmartHomeWriteTelegram):
                Type of the telegram to create.

        Returns:
            LuxtronikSmartHomeWriteTelegram | None:
                The created telegram or None in case of an error.
        """
        data_arr = block.get_data_arr()
        if data_arr is None:
            LOGGER.error(f"Failed to create a {telegram_type} telegram! The provided data is not valid.")
            return None
        return telegram_type(block.first_addr, data_arr)

    def _create_telegram(self, block, type_name, read_not_write):
        """
        Create a read or write-telegram out of this `ContiguousDataBlock`.

        Returns:
            LuxtronikSmartHomeReadTelegram | LuxtronikSmartHomeWriteTelegram | None:
                The created telegram or None in case of an error.
        """
        if type_name == HOLDINGS_FIELD_NAME and read_not_write:
            return self._create_read_telegram(block, LuxtronikSmartHomeReadHoldingsTelegram)
        if type_name == INPUTS_FIELD_NAME and read_not_write:
            return self._create_read_telegram(block, LuxtronikSmartHomeReadInputsTelegram)
        if type_name == HOLDINGS_FIELD_NAME and not read_not_write:
            return self._create_write_telegram(block, LuxtronikSmartHomeWriteHoldingsTelegram)
        LOGGER.error(f"Could not create a telegram for {block}. Skip this operation.")
        return None

    def _create_telegrams(self, blocks_list):
        """
        Create a read or write-telegram out of this `ContiguousDataBlock`.

        Returns:
            LuxtronikSmartHomeReadTelegram | LuxtronikSmartHomeWriteTelegram | None:
                The created telegram or None in case of an error.
        """
        telegrams_data = []
        for blocks in blocks_list:
            for block in blocks:
                telegram = self._create_telegram(block, blocks.type_name, blocks.read_not_write)
                if telegram is not None:
                    telegrams_data.append((block, telegram, blocks.read_not_write))
        return telegrams_data

    def _integrate_data(self, telegrams_data):
        """
        Integrate the read data from telegrams back into the corresponding blocks.
        '_create_telegrams' must be called up beforehand.

        Returns:
            bool: True if all data could be integrated.
        """
        success = True
        for block, telegram, read_not_write in telegrams_data:
            if read_not_write:
                valid = block.integrate_data(telegram.data)
                if not valid:
                    LOGGER.error('Failed to integrate read data into {block}')
                success &= valid
        return success


# Common methods ##############################################################

    def _send_and_integrate(self, blocks_list):
        """
        Read or write the data for multiple fields (a single field may correspond to multiple registers)
        using the contiguous-data-blocks-handler. Subsequently, the retrieved data
        is integrated into the provided fields.

        Args:
            blocks_list (list[TODO ....]): Handler that groups fields into contiguous blocks.
        """
        # Convert the list of contiguous blocks to telegrams
        telegrams = self._create_telegrams(blocks_list)
        # Send all telegrams. The retrieved data is returned within the telegrams
        success = self._interface.send(telegrams)
        # Transfer the data from the telegrams into the fields
        success &= self._integrate_data(blocks_list)
        return success

    def _prepare_read_field(self, definition, field):

        # Skip non-existing fields
        if not version_in_range(self._version, definition.since, definition.until):
            field.raw = LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE
            return False

        return True

    def _prepare_write_field(self, definition, field, data, safe):

        # Skip non-existing fields
        if not version_in_range(self._version, definition.since, definition.until):
            return False

        # Skip fields that do not carry user-data
        if not field.set_by_user:
            return False

        # Abort if field is not writeable
        if safe and not definition.writeable:
            LOGGER.warning(f"Field marked as non-writeable: name={definition.name}, data={field.raw}")
            return False

        # Override the field's data with the provided data
        if data is not False:
            field.raw = data

        # Abort if insufficient data is provided
        if not check_data(definition, field):
            LOGGER.warning(f"Data error / insufficient data provided: name={definition.name}, data={field.raw}")
            return False

        return True

    def _collect_field(self, blocks_list, field_or_name_or_idx, definitions, read_not_write, data, safe):
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

        blocks = ContiguousDataBlockList(definitions.name, read_not_write)
        if read_not_write and not self._prepare_read_field(definition, field)
            return None
        if not read_not_write and not self._prepare_write_field(definition, field, data, safe)
            return None

        blocks.append_single(definition, field)
        return field

    def _collect_fields(self, blocks_list, data_vector, definitions, read_not_write, data, safe):
        """
        Read the data of all fields within the given data vector.

        The provided callback method determines whether input or holding registers are read.
        The retrieved data is integrated into the data-vector fields.

        Args:
            data_vector (DataVectorSmartHome): The data vector class providing fields.
        """
        if self._version is None:
            # Trial-and-error mode: Add a block for every field
            blocks = ContiguousDataBlockList(definitions.name, read_not_write)
            if read_not_write:
                for definition, field in data_vector:
                    if self._prepare_read_field(definition, field):
                        blocks.append_single(definition, field)
            else:
                for definition, field in data_vector:
                    if self._prepare_write_field(definition, field, data, safe):
                        blocks.append_single(definition, field)
        else:
            if read_not_write:
                # We can directly use the prepared read-blocks
                data_vector.update_read_blocks()
                blocks_list.append(data_vector._read_blocks)
            else:
                blocks = ContiguousDataBlockList(definitions.name, False)
                # Organize data into contiguous blocks
                for definition, field in data_vector:
                    if self._prepare_write_field(self, definition, field, data, safe):
                        blocks.collect(definition, field)
                blocks_list.append(blocks)


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
        blocks_list = []
        field = self._collect_field(blocks_list, field_or_name_or_idx, Holdings, True, None, True)
        success = self._send_and_integrate(blocks_list)
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
            holdings = self.create_holdings()

        blocks_list = []
        self._collect_fields(blocks_list, holdings, Holdings, True, None, True)
        self._send_and_integrate(blocks_list)
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
        blocks_list = []
        field = self._collect_field(blocks_list, field_or_name_or_idx, Holdings, False, data, safe)
        success = self._send_and_integrate(blocks_list)
        return field if success else None

    def write_holdings(self, holdings):
        """
        Write the data of all fields within the holdings data vector.

        Args:
            holdings (Holdings): The holdings object containing field data.
                If None is provided, the write is aborted.
        """
        if holdings is None:
            LOGGER.warning("Abort write! No data to write provided.")
            return

        blocks_list = []
        self._collect_fields(blocks_list, holdings, Holdings, False, None, holdings.safe)
        self._send_and_integrate(blocks_list)

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
        blocks_list = []
        field = self._collect_field(blocks_list, field_or_name_or_idx, Inputs, True, None, True)
        success = self._send_and_integrate(blocks_list)
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
            inputs = self.create_inputs()

        blocks_list = []
        self._collect_fields(blocks_list, inputs, Inputs, True, None, True)
        self._send_and_integrate(blocks_list)
        return inputs

# Full read/write methods #####################################################
# Be careful with method names!
# Identical named methods could be overridden in a derived class.

    def _shi_read(self, data):
        if data is None:
            data = self.create_data()

        blocks_list = []
        self._collect_fields(blocks_list, data.holdings, Holdings, True, None, True)
        self._collect_fields(blocks_list, data.inputs, Inputs, True, None, True)
        self._send_and_integrate(blocks_list)
        return data

    def _shi_write(self, holdings):
        self.write_holdings(holdings)

    def _shi_write_and_read(self, holdings, data=None):
        if holdings is None:
            LOGGER.warning("Abort SHI write and read! No data to write provided.")
            return
        if data is None:
            data = self.create_data()

        blocks_list = []
        self._collect_fields(blocks_list, holdings, Holdings, False, None, holdings.safe)
        self._collect_fields(blocks_list, data.holdings, Holdings, True, None, True)
        self._collect_fields(blocks_list, data.inputs, Inputs, True, None, True)
        self._send_and_integrate(blocks_list)
        return data

    def read(self, data=None):
        return self._shi_read(data)

    def write(self, holdings):
        self._shi_write(holdings)

    def write_and_read(self, holdings, data=None):
        return self._shi_write_and_read(holdings, data)