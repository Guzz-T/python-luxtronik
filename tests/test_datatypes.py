"""Test suite for datatypes module"""

# pylint: disable=too-few-public-methods,invalid-name
# fmt:off

import datetime
import pytest

from luxtronik.datatypes import (
    LuxtronikDataFieldDefinition,
    Base,
    SelectionBase,
    Celsius,
    Bool,
    Frequency,
    Seconds,
    Pulses,
    IPAddress,
    Timestamp,
    Errorcode,
    Kelvin,
    Pressure,
    Percent,
    Percent2,
    Speed,
    Power,
    Energy,
    Voltage,
    Hours,
    Minutes,
    Flow,
    Level,
    Count,
    Version,
    Icon,
    HeatingMode,
    CoolingMode,
    HotWaterMode,
    PoolMode,
    MixedCircuitMode,
    SolarMode,
    VentilationMode,
    HeatpumpCode,
    BivalenceLevel,
    OperationMode,
    SwitchoffFile,
    MainMenuStatusLine1,
    MainMenuStatusLine2,
    SecOperationMode,
    AccessLevel,
    Unknown,
)


class TestBase:
    """Test suite for Base datatype"""

    _base_def = LuxtronikDataFieldDefinition(1, "base", Base)

    def test_init(self):
        """Test cases for initialization"""

        a = Base(self._base_def)
        assert a.name == "base"
        assert a.writeable is False

        b = Base(LuxtronikDataFieldDefinition(1, "base", Base, writeable=True))
        assert b.name == "base"
        assert b.writeable is True

        c = Base(LuxtronikDataFieldDefinition(1, "base", Base, True))
        assert c.name == "base"
        assert c.writeable is True

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Base.from_heatpump(1) == 1

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Base.to_heatpump(1) == 1

    def test_repr(self):
        """Test cases for __repr__ function"""

        # unsure what to test and whether this method is needed at all
        pytest.skip("Not yet implemented")

    def test_str(self):
        """Test cases for __str__ function"""

        # unsure what to test and whether this method is needed at all
        pytest.skip("Not yet implemented")


class TestSelectionBase:
    """Test suite for SelectionBase datatype"""

    _sel_def = LuxtronikDataFieldDefinition(1, "selection_base", SelectionBase)

    def test_init(self):
        """Test cases for initialization"""

        a = SelectionBase(self._sel_def)
        assert a.name == "selection_base"
        assert not a.codes
        assert len(a.codes) == 0

    def test_options(self):
        """Test cases for options property"""

        a = SelectionBase(self._sel_def)
        a.codes = {0: "a", 1: "b", 2: "c"}
        assert len(a.options) == 3
        assert a.options() == list(a.codes.values())

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        a = SelectionBase(self._sel_def)
        a.codes = {0: "a", 1: "b", 2: "c"}
        assert len(a.codes) == 3
        assert a.from_heatpump(0) == "a"
        assert a.from_heatpump(1) == "b"
        assert a.from_heatpump(2) == "c"
        assert a.from_heatpump(3) is None

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        a = SelectionBase(self._sel_def)
        a.codes = {0: "a", 1: "b", 2: "c"}
        assert len(a.codes) == 3
        assert a.to_heatpump("a") == 0
        assert a.to_heatpump("b") == 1
        assert a.to_heatpump("c") == 2
        assert a.to_heatpump("d") is None


class TestCelsius:
    """Test suite for Celsius datatype"""

    _celsius_def = LuxtronikDataFieldDefinition(1, "celsius", Celsius)

    def test_init(self):
        """Test cases for initialization"""

        a = Celsius(self._celsius_def)
        assert a.name == "celsius"
        assert a.measurement_type == "celsius"

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Celsius.from_heatpump(10) == 1
        assert Celsius.from_heatpump(11) == 1.1

        assert Celsius.from_heatpump(-10) == -1
        assert Celsius.from_heatpump(-11) == -1.1

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Celsius.to_heatpump(1) == 10
        assert Celsius.to_heatpump(1.1) == 11

        assert Celsius.to_heatpump(-1) == -10
        assert Celsius.to_heatpump(-1.1) == -11


class TestBool:
    """Test suite for Bool datatype"""

    _bool_def = LuxtronikDataFieldDefinition(1, "bool", Bool)

    def test_init(self):
        """Test cases for initialization"""

        a = Bool(self._bool_def)
        assert a.name == "bool"
        assert a.measurement_type == "boolean"

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Bool.from_heatpump(0) is False
        assert Bool.from_heatpump(1) is True

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Bool.to_heatpump(False) == 0
        assert Bool.to_heatpump(True) == 1


class TestFrequency:
    """Test suite for Frequency datatype"""

    _frequency_def = LuxtronikDataFieldDefinition(1, "frequency", Celsius)

    def test_init(self):
        """Test cases for initialization"""

        a = Frequency(self._frequency_def)
        assert a.name == "frequency"
        assert a.measurement_type == "Hz"


class TestSeconds:
    """Test suite for Seconds datatype"""

    _seconds_def = LuxtronikDataFieldDefinition(1, "seconds", Seconds)

    def test_init(self):
        """Test cases for initialization"""

        a = Seconds(self._seconds_def)
        assert a.name == "seconds"
        assert a.measurement_type == "seconds"


class TestPulses:
    """Test suite for Pulses datatype"""

    _pulses_def = LuxtronikDataFieldDefinition(1, "pulses", Pulses)

    def test_init(self):
        """Test cases for initialization"""

        a = Pulses(self._pulses_def)
        assert a.name == "pulses"
        assert a.measurement_type == "pulses"


class TestIPAddress:
    """Test suite for IPAddress datatype"""

    _ipaddress_def = LuxtronikDataFieldDefinition(1, "ipaddress", IPAddress)

    def test_init(self):
        """Test cases for initialization"""

        a = IPAddress(self._ipaddress_def)
        assert a.name == "ipaddress"
        assert a.measurement_type == "ipaddress"

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert IPAddress.from_heatpump(0) == "0.0.0.0"
        assert IPAddress.from_heatpump(16909060) == "1.2.3.4"
        assert IPAddress.from_heatpump(-1062731775) == "192.168.0.1"
        assert IPAddress.from_heatpump(-256) == "255.255.255.0"
        assert IPAddress.from_heatpump(-1) == "255.255.255.255"

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert IPAddress.to_heatpump("0.0.0.0") == 0
        assert IPAddress.to_heatpump("1.2.3.4") == 16909060
        assert IPAddress.to_heatpump("192.168.0.1") == -1062731775
        assert IPAddress.to_heatpump("255.255.255.0") == -256
        assert IPAddress.to_heatpump("255.255.255.255") == -1


class TestTimestamp:
    """Test suite for Timestamp datatype"""

    _timestamp_def = LuxtronikDataFieldDefinition(1, "timestamp", Timestamp)

    def test_init(self):
        """Test cases for initialization"""

        a = Timestamp(self._timestamp_def)
        assert a.name == "timestamp"
        assert a.measurement_type == "timestamp"

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        a = Timestamp(self._timestamp_def)
        assert a.from_heatpump(-1) == datetime.datetime.fromtimestamp(0)
        assert a.from_heatpump(0) == datetime.datetime.fromtimestamp(0)
        assert a.from_heatpump(1) == datetime.datetime.fromtimestamp(1)
        # pylint: disable=fixme
        # TODO Consider to drop microseconds when dealing with this datatype?
        b = datetime.datetime.now()
        assert a.from_heatpump(datetime.datetime.timestamp(b)) == b

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        a = Timestamp(self._timestamp_def)
        assert a.to_heatpump(datetime.datetime.fromtimestamp(0)) == 0
        assert a.to_heatpump(datetime.datetime.fromtimestamp(1)) == 1
        # pylint: disable=fixme
        # TODO Consider to drop microseconds when dealing with this datatype?
        b = datetime.datetime.now()
        assert a.to_heatpump(b) == datetime.datetime.timestamp(b)


class TestErrorcode:
    """Test suite for Errorcode datatype"""

    _errorcode_def = LuxtronikDataFieldDefinition(1, "errorcode", Errorcode)

    def test_init(self):
        """Test cases for initialization"""

        a = Errorcode(self._errorcode_def)
        assert a.name == "errorcode"
        assert a.measurement_type == "errorcode"


class TestKelvin:
    """Test suite for Errorcode datatype"""

    _kelvin_def = LuxtronikDataFieldDefinition(1, "kelvin", Kelvin)

    def test_init(self):
        """Test cases for initialization"""

        a = Kelvin(self._kelvin_def)
        assert a.name == "kelvin"
        assert a.measurement_type == "kelvin"

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Kelvin.from_heatpump(10) == 1
        assert Kelvin.from_heatpump(11) == 1.1

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Kelvin.to_heatpump(1) == 10
        assert Kelvin.to_heatpump(1.1) == 11


class TestPressure:
    """Test suite for Pressure datatype"""

    _pressure_def = LuxtronikDataFieldDefinition(1, "pressure", Pressure)

    def test_init(self):
        """Test cases for initialization"""

        a = Pressure(self._pressure_def)
        assert a.name == "pressure"
        assert a.measurement_type == "bar"

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Pressure.from_heatpump(100) == 1
        assert Pressure.from_heatpump(101) == 1.01

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Pressure.to_heatpump(1) == 100
        assert Pressure.to_heatpump(1.01) == 101


class TestPercent:
    """Test suite for Percent datatype"""

    _percent_def = LuxtronikDataFieldDefinition(1, "percent", Percent)

    def test_init(self):
        """Test cases for initialization"""

        a = Percent(self._percent_def)
        assert a.name == "percent"
        assert a.measurement_type == "percent"

    def test_percent_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Percent.from_heatpump(10) == 1
        assert Percent.from_heatpump(11) == 1.1

    def test_percent_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Percent.to_heatpump(1) == 10
        assert Percent.to_heatpump(1.1) == 11


class TestPercent2:
    """Test suite for Percent2 datatype"""

    _percent2_def = LuxtronikDataFieldDefinition(1, "percent2", Percent2)

    def test_init(self):
        """Test cases for initialization"""

        a = Percent2(self._percent2_def)
        assert a.name == "percent2"
        assert a.measurement_type == "percent"

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Percent2.from_heatpump(10) == 10
        assert Percent2.from_heatpump(11) == 11

    def test_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Percent2.to_heatpump(10) == 10
        assert Percent2.to_heatpump(11) == 11


class TestSpeed:
    """Test suite for Speed datatype"""

    _speed_def = LuxtronikDataFieldDefinition(1, "speed", Speed)

    def test_init(self):
        """Test cases for initialization"""

        a = Speed(self._speed_def)
        assert a.name == "speed"
        assert a.measurement_type == "rpm"


class TestPower:
    """Test suite for Power datatype"""

    _power_def = LuxtronikDataFieldDefinition(1, "power", Power)

    def test_init(self):
        """Test cases for initialization"""

        a = Power(self._power_def)
        assert a.name == "power"
        assert a.measurement_type == "W"


class TestEnergy:
    """Test suite for Energy datatype"""

    _energy_def = LuxtronikDataFieldDefinition(1, "energy", Energy)

    def test_init(self):
        """Test cases for initialization"""

        a = Energy(self._energy_def)
        assert a.name == "energy"
        assert a.measurement_type == "energy"

    def test_energy_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Energy.from_heatpump(10) == 1
        assert Energy.from_heatpump(11) == 1.1

    def test_energy_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Energy.to_heatpump(1) == 10
        assert Energy.to_heatpump(1.1) == 11


class TestVoltage:
    """Test suite for Voltage datatype"""

    _voltage_def = LuxtronikDataFieldDefinition(1, "voltage", Voltage)

    def test_init(self):
        """Test cases for initialization"""

        a = Voltage(self._voltage_def)
        assert a.name == "voltage"
        assert a.measurement_type == "voltage"

    def test_voltage_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Voltage.from_heatpump(10) == 1
        assert Voltage.from_heatpump(11) == 1.1

    def test_voltage_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Voltage.to_heatpump(1) == 10
        assert Voltage.to_heatpump(1.1) == 11


class TestHours:
    """Test suite for Hours datatype"""

    _hours_def = LuxtronikDataFieldDefinition(1, "hours", Hours)

    def test_init(self):
        """Test cases for initialization"""

        a = Hours(self._hours_def)
        assert a.name == "hours"
        assert a.measurement_type == "hours"

    def test_hours_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Hours.from_heatpump(10) == 1
        assert Hours.from_heatpump(11) == 1.1

    def test_hours_to_heatpump(self):
        """Test cases for to_heatpump function"""

        assert Hours.to_heatpump(1) == 10
        assert Hours.to_heatpump(1.1) == 11


class TestMinutes:
    """Test suite for Minutes datatype"""

    _minutes_def = LuxtronikDataFieldDefinition(1, "minutes", Minutes)

    def test_init(self):
        """Test cases for initialization"""

        a = Minutes(self._minutes_def)
        assert a.name == "minutes"
        assert a.measurement_type == "Minutes"


class TestFlow:
    """Test suite for Flow datatype"""

    _flow_def = LuxtronikDataFieldDefinition(1, "flow", Flow)

    def test_init(self):
        """Test cases for initialization"""

        a = Flow(self._flow_def)
        assert a.name == "flow"
        assert a.measurement_type == "flow"


class TestLevel:
    """Test suite for Level datatype"""

    _level_def = LuxtronikDataFieldDefinition(1, "level", Level)

    def test_init(self):
        """Test cases for initialization"""

        a = Level(self._level_def)
        assert a.name == "level"
        assert a.measurement_type == "level"


class TestCount:
    """Test suite for Count datatype"""

    _count_def = LuxtronikDataFieldDefinition(1, "count", Count)

    def test_init(self):
        """Test cases for initialization"""

        a = Count(self._count_def)
        assert a.name == "count"
        assert a.measurement_type == "count"


class TestVersion:
    """Test suite for Version datatype"""

    _version_def = LuxtronikDataFieldDefinition(1, "version", Version)

    def test_init(self):
        """Test cases for initialization"""

        a = Version(self._version_def)
        assert a.name == "version"
        assert a.measurement_type == "version"

    def test_from_heatpump(self):
        """Test cases for from_heatpump function"""

        assert Version.from_heatpump(bytes([51, 46, 56, 56])) == "3.88"
        assert Version.from_heatpump(bytes([51, 46, 56, 56, 00])) == "3.88"
        assert Version.from_heatpump(bytes([00, 51, 46, 56, 56, 00])) == "3.88"
        assert Version.from_heatpump(bytes([48])) == "0"


class TestIcon:
    """Test suite for Icon datatype"""

    _icon_def = LuxtronikDataFieldDefinition(1, "icon", Icon)

    def test_init(self):
        """Test cases for initialization"""

        a = Icon(self._icon_def)
        assert a.name == "icon"
        assert a.measurement_type == "icon"


class TestHeatingMode:
    """Test suite for HeatingMode datatype"""

    _heating_mode_def = LuxtronikDataFieldDefinition(1, "heating_mode", HeatingMode)

    def test_init(self):
        """Test cases for initialization"""

        a = HeatingMode(self._heating_mode_def)
        assert a.name == "heating_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 5

    def test_options(self):
        """Test cases for options property"""

        a = HeatingMode(self._heating_mode_def)
        assert len(a.options) == 5
        assert a.options() == list(a.codes.values())


class TestCoolingMode:
    """Test suite for CoolingMode datatype"""

    _cooling_mode_def = LuxtronikDataFieldDefinition(1, "cooling_mode", CoolingMode)

    def test_init(self):
        """Test cases for initialization"""

        a = CoolingMode(self._cooling_mode_def)
        assert a.name == "cooling_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 2

    def test_options(self):
        """Test cases for options property"""

        a = CoolingMode(self._cooling_mode_def)
        assert len(a.options) == 2


class TestHotWaterMode:
    """Test suite for HotWaterMode datatype"""

    _hot_water_mode_def = LuxtronikDataFieldDefinition(1, "hot_water_mode", HotWaterMode)

    def test_init(self):
        """Test cases for initialization"""

        a = HotWaterMode(self._hot_water_mode_def)
        assert a.name == "hot_water_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 5

    def test_options(self):
        """Test cases for options property"""

        a = HotWaterMode(self._hot_water_mode_def)
        assert len(a.options) == 5
        assert a.options() == list(a.codes.values())


class TestPoolMode:
    """Test suite for PoolMode datatype"""

    _pool_mode_def = LuxtronikDataFieldDefinition(1, "pool_mode", PoolMode)

    def test_init(self):
        """Test cases for initialization"""

        a = PoolMode(self._pool_mode_def)
        assert a.name == "pool_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 4

    def test_options(self):
        """Test cases for options property"""

        a = PoolMode(self._pool_mode_def)
        assert len(a.options) == 4
        assert a.options() == list(a.codes.values())


class TestMixedCircuitMode:
    """Test suite for MixedCircuitMode datatype"""

    _mixed_circuit_mode_def = LuxtronikDataFieldDefinition(1, "mixed_circuit_mode", MixedCircuitMode)

    def test_init(self):
        """Test cases for initialization"""

        a = MixedCircuitMode(self._mixed_circuit_mode_def)
        assert a.name == "mixed_circuit_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 4

    def test_options(self):
        """Test cases for options property"""

        a = MixedCircuitMode(self._mixed_circuit_mode_def)
        assert len(a.options) == 4
        assert a.options() == list(a.codes.values())


class TestSolarMode:
    """Test suite for SolarMode datatype"""

    _solar_mode_def = LuxtronikDataFieldDefinition(1, "solar_mode", SolarMode)

    def test_init(self):
        """Test cases for initialization"""

        a = SolarMode(self._solar_mode_def)
        assert a.name == "solar_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 5

    def test_options(self):
        """Test cases for options property"""

        a = SolarMode(self._solar_mode_def)
        assert len(a.options) == 5
        assert a.options() == list(a.codes.values())


class TestVentilationMode:
    """Test suite for VentilationMode datatype"""

    _ventilation_mode_def = LuxtronikDataFieldDefinition(1, "ventilation_mode", VentilationMode)

    def test_init(self):
        """Test cases for initialization"""

        a = VentilationMode(self._ventilation_mode_def)
        assert a.name == "ventilation_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 4

    def test_options(self):
        """Test cases for options property"""

        a = VentilationMode(self._ventilation_mode_def)
        assert len(a.options) == 4
        assert a.options() == list(a.codes.values())


class TestHeatpumpCode:
    """Test suite for HeatpumpCode datatype"""

    _heatpump_code_def = LuxtronikDataFieldDefinition(1, "heatpump_code", HeatpumpCode)

    def test_init(self):
        """Test cases for initialization"""

        a = HeatpumpCode(self._heatpump_code_def)
        assert a.name == "heatpump_code"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 68

    def test_options(self):
        """Test cases for options property"""

        a = HeatpumpCode(self._heatpump_code_def)
        assert len(a.options) == 68
        assert a.options() == list(a.codes.values())


class TestBivalenceLevel:
    """Test suite for BivalenceLevel datatype"""

    _bivalence_level_def = LuxtronikDataFieldDefinition(1, "bivalence_level", BivalenceLevel)

    def test_init(self):
        """Test cases for initialization"""

        a = BivalenceLevel(self._bivalence_level_def)
        assert a.name == "bivalence_level"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 3

    def test_options(self):
        """Test cases for options property"""

        a = BivalenceLevel(self._bivalence_level_def)
        assert len(a.options) == 3
        assert a.options() == list(a.codes.values())


class TestOperationMode:
    """Test suite for OperationMode datatype"""

    _operation_mode_def = LuxtronikDataFieldDefinition(1, "operation_mode", OperationMode)

    def test_init(self):
        """Test cases for initialization"""

        a = OperationMode(self._operation_mode_def)
        assert a.name == "operation_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 8

    def test_options(self):
        """Test cases for options property"""

        a = OperationMode(self._operation_mode_def)
        assert len(a.options) == 8
        assert a.options() == list(a.codes.values())


class TestSwitchoffFile:
    """Test suite for SwitchoffFile datatype"""

    _switchoff_file_def = LuxtronikDataFieldDefinition(1, "switchoff_file", SwitchoffFile)

    def test_init(self):
        """Test cases for initialization"""

        a = SwitchoffFile(self._switchoff_file_def)
        assert a.name == "switchoff_file"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 11

    def test_options(self):
        """Test cases for options property"""

        a = SwitchoffFile(self._switchoff_file_def)
        assert len(a.options) == 11
        assert a.options() == list(a.codes.values())


class TestMainMenuStatusLine1:
    """Test suite for MainMenuStatusLine1 datatype"""

    _main_menu_status_line1_def = LuxtronikDataFieldDefinition(1, "main_menu_status_line1", MainMenuStatusLine1)

    def test_init(self):
        """Test cases for initialization"""

        a = MainMenuStatusLine1(self._main_menu_status_line1_def)
        assert a.name == "main_menu_status_line1"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 8

    def test_options(self):
        """Test cases for options property"""

        a = MainMenuStatusLine1(self._main_menu_status_line1_def)
        assert len(a.options) == 8
        assert a.options() == list(a.codes.values())


class TestMainMenuStatusLine2:
    """Test suite for MainMenuStatusLine2 datatype"""

    _main_menu_status_line2_def = LuxtronikDataFieldDefinition(1, "main_menu_status_line2", MainMenuStatusLine2)

    def test_init(self):
        """Test cases for initialization"""

        a = MainMenuStatusLine2(self._main_menu_status_line2_def)
        assert a.name == "main_menu_status_line2"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 2

    def test_options(self):
        """Test cases for options property"""

        a = MainMenuStatusLine2(self._main_menu_status_line2_def)
        assert len(a.options) == 2
        assert a.options() == list(a.codes.values())


class TestSecOperationMode:
    """Test suite for SecOperationMode datatype"""

    _sec_operation_mode_def = LuxtronikDataFieldDefinition(1, "sec_operation_mode", SecOperationMode)

    def test_init(self):
        """Test cases for initialization"""

        a = SecOperationMode(self._sec_operation_mode_def)
        assert a.name == "sec_operation_mode"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 13

    def test_options(self):
        """Test cases for options property"""

        a = SecOperationMode(self._sec_operation_mode_def)
        assert len(a.options) == 13
        assert a.options() == list(a.codes.values())


class TestAccessLevel:
    """Test suite for AccessLevel datatype"""

    _access_level_def = LuxtronikDataFieldDefinition(1, "access_level", AccessLevel)

    def test_init(self):
        """Test cases for initialization"""

        a = AccessLevel(self._access_level_def)
        assert a.name == "access_level"
        assert a.measurement_type == "selection"
        assert len(a.codes) == 4

    def test_options(self):
        """Test cases for options property"""

        a = AccessLevel(self._access_level_def)
        assert len(a.options) == 4
        assert a.options() == list(a.codes.values())


class TestUnknown:
    """Test suite for Unknown datatype"""

    _unknown_def = LuxtronikDataFieldDefinition(1, "unknown", Unknown)

    def test_init(self):
        """Test cases for initialization"""

        a = Unknown(self._unknown_def)
        assert a.name == "unknown"
        assert a.measurement_type is None
