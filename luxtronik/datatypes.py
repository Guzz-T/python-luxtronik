"""datatype conversions."""
import logging
import datetime
import socket
import struct
from collections import namedtuple


LuxtronikDataFieldDefinition = namedtuple(
    "LuxtronikDataFieldDefinition",
    ["index", "name", "datatype", "writeable"],
    defaults=[False],
)

LOGGER = logging.getLogger("Luxtronik.DataTypes")


class Base:
    """Base datatype, no conversions."""

    measurement_type = None

    def __init__(self, data_field_def):
        """Initialize the data field class."""
        self._raw = None
        self._data_field_def = data_field_def

    @property
    def name(self) -> str:
        """Returns the name of the data field."""
        return self._data_field_def.name

    @property
    def writeable(self) -> bool:
        """Returns true if the data field is marked as writeable."""
        return self._data_field_def.writeable

    @classmethod
    def to_heatpump(cls, value):
        """Converts value into heatpump units."""
        return value

    @classmethod
    def from_heatpump(cls, value):
        """Converts value from heatpump units."""
        return value

    @property
    def value(self):
        """Return the stored value converted from heatpump units."""
        return self.from_heatpump(self._raw)

    @value.setter
    def value(self, value):
        """Converts the value into heatpump units and store it."""
        self._raw = self.to_heatpump(value)

    @property
    def raw(self):
        """Return the stored raw data."""
        return self._raw

    @raw.setter
    def raw(self, raw):
        """Store the raw data."""
        self._raw = raw

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        value = self.value
        if value is not None:
            return str(value)
        return str(self.raw)


class SelectionBase(Base):
    """Selection base datatype, converts from and to list of codes."""

    codes = {}

    @classmethod
    def options(cls):
        """Return list of all available options."""
        return [value for _, value in cls.codes.items()]

    @classmethod
    def from_heatpump(cls, value):
        if value in cls.codes:
            return cls.codes.get(value)
        return None

    @classmethod
    def to_heatpump(cls, value):
        for index, code in cls.codes.items():
            if code == value:
                return index
        return None


class Celsius(Base):
    """Celsius datatype, converts from and to Celsius."""

    measurement_type = "celsius"

    @classmethod
    def from_heatpump(cls, value):
        return value / 10

    @classmethod
    def to_heatpump(cls, value):
        return int(float(value) * 10)


class Bool(Base):
    """Boolean datatype, converts from and to Boolean."""

    measurement_type = "boolean"

    @classmethod
    def from_heatpump(cls, value):
        return bool(value)

    @classmethod
    def to_heatpump(cls, value):
        return int(value)


class Frequency(Base):
    """Frequency datatype, converts from and to Frequency in Hz."""

    measurement_type = "Hz"


class Seconds(Base):
    """Seconds datatype, converts from and to Seconds."""

    measurement_type = "seconds"


class Pulses(Base):
    """Pulses datatype, converts from and to Pulses."""

    measurement_type = "pulses"


class IPAddress(Base):
    """IP Address datatype, converts from and to an IP Address."""

    measurement_type = "ipaddress"

    @classmethod
    def from_heatpump(cls, value):
        return socket.inet_ntoa(struct.pack(">i", value))

    @classmethod
    def to_heatpump(cls, value):
        return struct.unpack(">i", socket.inet_aton(value))[0]


class Timestamp(Base):
    """Timestamp datatype, converts from and to Timestamp."""

    measurement_type = "timestamp"

    @classmethod
    def from_heatpump(cls, value):
        if value > 0:
            return datetime.datetime.fromtimestamp(value)
        return datetime.datetime.fromtimestamp(0)

    @classmethod
    def to_heatpump(cls, value):
        return datetime.datetime.timestamp(value)


class Errorcode(Base):
    """Errorcode datatype, converts from and to Errorcode."""

    measurement_type = "errorcode"


class Kelvin(Base):
    """Kelvin datatype, converts from and to Kelvin."""

    measurement_type = "kelvin"

    @classmethod
    def from_heatpump(cls, value):
        return value / 10

    @classmethod
    def to_heatpump(cls, value):
        return int(float(value) * 10)


class Pressure(Base):
    """Pressure datatype, converts from and to Pressure."""

    measurement_type = "bar"

    @classmethod
    def from_heatpump(cls, value):
        return value / 100

    @classmethod
    def to_heatpump(cls, value):
        return int(value * 100)


class Percent(Base):
    """Percent datatype, converts from and to Percent."""

    measurement_type = "percent"

    @classmethod
    def from_heatpump(cls, value):
        return value / 10

    @classmethod
    def to_heatpump(cls, value):
        return int(value * 10)


class Percent2(Base):
    """Percent datatype, converts from and to Percent with a different scale factor."""

    measurement_type = "percent"

    @classmethod
    def from_heatpump(cls, value):
        return value

    @classmethod
    def to_heatpump(cls, value):
        return int(value)


class Speed(Base):
    """Speed datatype, converts from and to Speed."""

    measurement_type = "rpm"


class Power(Base):
    """Power datatype, converts from and to Power."""

    measurement_type = "W"


class Energy(Base):
    """Energy datatype, converts from and to Energy."""

    measurement_type = "energy"

    @classmethod
    def from_heatpump(cls, value):
        return value / 10

    @classmethod
    def to_heatpump(cls, value):
        return int(value * 10)


class Voltage(Base):
    """Voltage datatype, converts from and to Voltage."""

    measurement_type = "voltage"

    @classmethod
    def from_heatpump(cls, value):
        return value / 10

    @classmethod
    def to_heatpump(cls, value):
        return int(value * 10)


class Hours(Base):
    """Hours datatype, converts from and to Hours."""

    measurement_type = "hours"

    @classmethod
    def from_heatpump(cls, value):
        return value / 10

    @classmethod
    def to_heatpump(cls, value):
        return int(value * 10)


class Minutes(Base):
    """Minutes datatype, converts from and to Minutes."""

    measurement_type = "Minutes"


class Flow(Base):
    """Flow datatype, converts from and to Flow."""

    measurement_type = "flow"


class Level(Base):
    """Level datatype, converts from and to Level."""

    measurement_type = "level"


class Count(Base):
    """Count datatype, converts from and to Count."""

    measurement_type = "count"


class Version(Base):
    """Version datatype, converts from and to a Heatpump Version."""

    measurement_type = "version"

    @classmethod
    def from_heatpump(cls, value):
        return "".join([chr(c) for c in value]).strip("\x00")


class Icon(Base):
    """Icon datatype, converts from and to Icon."""

    measurement_type = "icon"


class HeatingMode(SelectionBase):
    """HeatingMode datatype, converts from and to list of HeatingMode codes."""

    measurement_type = "selection"

    codes = {
        0: "Automatic",
        1: "Second heatsource",
        2: "Party",
        3: "Holidays",
        4: "Off",
    }


class CoolingMode(SelectionBase):
    """CoolingMode datatype, converts from and to list of CoolingMode codes."""

    measurement_type = "selection"

    codes = {0: "Off", 1: "Automatic"}


class HotWaterMode(SelectionBase):
    """HotWaterMode datatype, converts from and to list of HotWaterMode codes."""

    measurement_type = "selection"

    codes = {
        0: "Automatic",
        1: "Second heatsource",
        2: "Party",
        3: "Holidays",
        4: "Off",
    }


class PoolMode(SelectionBase):
    """PoolMode datatype, converts from and to list of PoolMode codes."""

    measurement_type = "selection"

    codes = {0: "Automatic", 2: "Party", 3: "Holidays", 4: "Off"}


class MixedCircuitMode(SelectionBase):
    """MixCircuitMode datatype, converts from and to list of MixCircuitMode codes."""

    measurement_type = "selection"

    codes = {0: "Automatic", 2: "Party", 3: "Holidays", 4: "Off"}


class SolarMode(SelectionBase):
    """SolarMode datatype, converts from and to list of SolarMode codes."""

    measurement_type = "selection"

    codes = {
        0: "Automatic",
        1: "Second heatsource",
        2: "Party",
        3: "Holidays",
        4: "Off",
    }


class VentilationMode(SelectionBase):
    """VentilationMode datatype, converts from and to list of VentilationMode codes."""

    measurement_type = "selection"

    codes = {0: "Automatic", 1: "Party", 2: "Holidays", 3: "Off"}


class HeatpumpCode(SelectionBase):
    """HeatpumpCode datatype, converts from and to list of Heatpump codes."""

    measurement_type = "selection"

    codes = {
        0: "ERC",
        1: "SW1",
        2: "SW2",
        3: "WW1",
        4: "WW2",
        5: "L1I",
        6: "L2I",
        7: "L1A",
        8: "L2A",
        9: "KSW",
        10: "KLW",
        11: "SWC",
        12: "LWC",
        13: "L2G",
        14: "WZS",
        15: "L1I407",
        16: "L2I407",
        17: "L1A407",
        18: "L2A407",
        19: "L2G407",
        20: "LWC407",
        21: "L1AREV",
        22: "L2AREV",
        23: "WWC1",
        24: "WWC2",
        25: "L2G404",
        26: "WZW",
        27: "L1S",
        28: "L1H",
        29: "L2H",
        30: "WZWD",
        31: "ERC",
        40: "WWB_20",
        41: "LD5",
        42: "LD7",
        43: "SW 37_45",
        44: "SW 58_69",
        45: "SW 29_56",
        46: "LD5 (230V)",
        47: "LD7 (230 V)",
        48: "LD9",
        49: "LD5 REV",
        50: "LD7 REV",
        51: "LD5 REV 230V",
        52: "LD7 REV 230V",
        53: "LD9 REV 230V",
        54: "SW 291",
        55: "LW SEC",
        56: "HMD 2",
        57: "MSW 4",
        58: "MSW 6",
        59: "MSW 8",
        60: "MSW 10",
        61: "MSW 12",
        62: "MSW 14",
        63: "MSW 17",
        64: "MSW 19",
        65: "MSW 23",
        66: "MSW 26",
        67: "MSW 30",
        68: "MSW 4S",
        69: "MSW 6S",
        70: "MSW 8S",
        71: "MSW 10S",
        72: "MSW 13S",
        73: "MSW 16S",
        74: "MSW2-6S",
        75: "MSW4-16",
    }


class BivalenceLevel(SelectionBase):
    """BivalanceLevel datatype, converts from and to list of BivalanceLevel codes."""

    measurement_type = "selection"

    codes = {
        1: "one compressor allowed to run",
        2: "two compressors allowed to run",
        3: "additional heat generator allowed to run",
    }


class OperationMode(SelectionBase):
    """OperationMode datatype, converts from and to list of OperationMode codes."""

    measurement_type = "selection"

    codes = {
        0: "heating",
        1: "hot water",
        2: "swimming pool/solar",
        3: "evu",
        4: "defrost",
        5: "no request",
        6: "heating external source",
        7: "cooling",
    }


class SwitchoffFile(SelectionBase):
    """SwitchOff datatype, converts from and to list of SwitchOff codes."""

    measurement_type = "selection"

    codes = {
        1: "heatpump error",
        2: "system error",
        3: "evu lock",
        4: "operation mode second heat generator",
        5: "air defrost",
        6: "maximal usage temperature",
        7: "minimal usage temperature",
        8: "lower usage limit",
        9: "no request",
        11: "flow rate",
        19: "PV max",
    }


class MainMenuStatusLine1(SelectionBase):
    """MenuStatusLine datatype, converts from and to list of MenuStatusLine codes."""

    measurement_type = "selection"

    codes = {
        0: "heatpump running",
        1: "heatpump idle",
        2: "heatpump coming",
        3: "errorcode slot 0",
        4: "defrost",
        5: "waiting on LIN connection",
        6: "compressor heating up",
        7: "pump forerun",
    }


class MainMenuStatusLine2(SelectionBase):
    """MenuStatusLine datatype, converts from and to list of MenuStatusLine codes."""

    measurement_type = "selection"

    codes = {0: "since", 1: "in"}


class MainMenuStatusLine3(SelectionBase):
    """MenuStatusLine datatype, converts from and to list of MenuStatusLine codes."""

    measurement_type = "selection"

    codes = {
        0: "heating",
        1: "no request",
        2: "grid switch on delay",
        3: "cycle lock",
        4: "lock time",
        5: "domestic water",
        6: "info bake out program",
        7: "defrost",
        8: "pump forerun",
        9: "thermal desinfection",
        10: "cooling",
        12: "swimming pool/solar",
        13: "heating external energy source",
        14: "domestic water external energy source",
        16: "flow monitoring",
        17: "second heat generator 1 active",
    }


class SecOperationMode(SelectionBase):
    """SecOperationMode datatype, converts from and to list of SecOperationMode codes."""

    measurement_type = "selection"

    codes = {
        0: "off",
        1: "cooling",
        2: "heating",
        3: "fault",
        4: "transition",
        5: "defrost",
        6: "waiting",
        7: "waiting",
        8: "transition",
        9: "stop",
        10: "manual",
        11: "simulation start",
        12: "evu lock",
    }


class AccessLevel(SelectionBase):
    """AccessLevel datatype, converts from and to list of AccessLevel codes"""

    measurement_type = "selection"

    codes = {
        0: "user",
        1: "after sales service",
        2: "manufacturer",
        3: "installer",
    }


class Unknown(Base):
    """Unknown datatype, fallback for unknown data."""

    measurement_type = None


class LuxtronikDataFieldFactory:
    """Factory to look-up data field definitions or to create data fields."""

    _data_field_defs = []

    @classmethod
    def count(cls) -> int:
        """Get the number of data field definitions."""
        return len(cls._data_field_defs)

    @classmethod
    def _lookup_by_index(cls, index: int) -> LuxtronikDataFieldDefinition:
        """Look-up a data field definition by its index."""
        if 0 <= index < cls.count():
            return cls._data_field_defs[index]
        return None

    @classmethod
    def _lookup_by_name(cls, name: str) -> LuxtronikDataFieldDefinition:
        """Look-up a data field definition by its name."""
        for data_field_def in cls._data_field_defs:
            if (str(data_field_def.index) == name) or (data_field_def.name == name):
                return data_field_def
        return None

    @classmethod
    def lookup(cls, target) -> LuxtronikDataFieldDefinition:
        """Look-up a data field definition by either its index or name."""
        if isinstance(target, int):
            # look-up by index
            return cls._lookup_by_index(target)
        if isinstance(target, str):
            # look-up by name
            return cls._lookup_by_name(target)
        return None

    @classmethod
    def create(cls, target):
        """Create a data field out of a data field definition."""
        if isinstance(target, LuxtronikDataFieldDefinition):
            # create data field class and assign its data field definition
            return target.index, target.datatype(target)
        # look-up the data field definition
        data_field_def = cls.lookup(target)
        if data_field_def:
            # call this function again with a data field definition as parameter
            return cls.create(data_field_def)
        return None, None


class LuxtronikDataFieldDict:
    """Class that holds all data fields."""

    def __init__(self, name, factory):
        """Initialize luxtronik data field dict."""
        self._name = name
        self._factory = factory
        self._data_dict = {}

    def __iter__(self):
        """Iterate over all assigned data fields."""
        return iter(self._data_dict.items())

    def _extract_data(self, index, raw_data):
        """Return the data for the data field and the next index where to proceed."""
        return index + 1, raw_data[index]

    def parse(self, raw_data, start_idx=0):
        """Parse raw data."""
        index = start_idx
        length = len(raw_data)
        # loop over all raw data bytes starting at data field index "start_idx"
        while index < (length + start_idx):
            # get the raw data for this data field and the index of the next data field to process
            next_index, data = self._extract_data(index, raw_data)
            # create a new data field class
            data_field = self._factory.create(index)[1]
            if not data_field:
                # LOGGER.warning("%s '%d' not in list of %ss", self._name, index, self._name)
                # create a new data field definition and class for this unknown raw data
                data_field_def = LuxtronikDataFieldDefinition(
                    index, f"Unknown_{self._name}_{index}", Unknown
                )
                data_field = Unknown(data_field_def)
            # assign the raw data to the new data field class
            data_field.raw = data
            # add the data field to the dictionary
            self._data_dict[index] = data_field
            # proceed with the next data field
            index = next_index

    def _get_data_field(self, target) -> (LuxtronikDataFieldDefinition, Base):
        """Look-up a data field definition and class."""
        data_field_def = self._factory.lookup(target)
        if data_field_def:
            return data_field_def, self._data_dict.get(data_field_def.index, None)
        if isinstance(target, int):
            return None, self._data_dict.get(target, None)
        return None, None

    def get(self, target) -> Base:
        """Get data field either by index or name."""
        # try get the data field
        data_field = self._get_data_field(target)[1]
        if not data_field:
            LOGGER.warning("%s '%s' not found", self._name, target)
        return data_field

    def set(self, target, value):
        """Set value of a data field, looked-up either by its index or name."""
        # try get the data field
        data_field_def, data_field = self._get_data_field(target)
        if data_field_def:
            if data_field:
                idx = data_field_def.index
            else:
                # Create a new data field
                idx, data_field = self._factory.create(data_field_def)
            # Set the value of the data field
            data_field.value = value
            # Re-assign the data field to the dictionary
            self._data_dict[idx] = data_field
        else:
            LOGGER.warning("%s '%s' not found", self._name, target)
