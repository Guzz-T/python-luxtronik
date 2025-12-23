from unittest.mock import patch

from luxtronik.shi import LuxtronikSmartHomeInterface
from luxtronik.shi.interface import LuxtronikSmartHomeData
from luxtronik import (
    Parameters,
    Holdings,
    LuxtronikSocketInterface,
    LuxtronikAllData,
    LuxtronikInterface,
    Luxtronik
)

###############################################################################
# Fake interfaces
###############################################################################

class FakeSocketInterface(LuxtronikSocketInterface):

    write_counter = 0
    read_counter = 0

    @classmethod
    def reset(cls):
        FakeSocketInterface.write_counter = 0
        FakeSocketInterface.read_counter = 0

    def _connect(self):
        pass

    def _disconnect(self):
        pass

    def read(self, data):
        FakeSocketInterface.read_parameters(self, data.parameters)
        FakeSocketInterface.read_visibilities(self, data.visibilities)
        FakeSocketInterface.read_calculations(self, data.calculations)

    def read_parameters(self, parameters):
        parameters.get(0).raw = 2
        FakeSocketInterface.read_counter += 1

    def read_visibilities(self, visibilities):
        visibilities.get(0).raw = 4
        FakeSocketInterface.read_counter += 1

    def read_calculations(self, calculations):
        calculations.get(0).raw = 6
        FakeSocketInterface.read_counter += 1

    def write(self, data):
        FakeSocketInterface.write_counter += 1

class FakeShiInterface(LuxtronikSmartHomeInterface):

    write_counter = 0
    read_counter = 0

    @classmethod
    def reset(cls):
        FakeShiInterface.write_counter = 0
        FakeShiInterface.read_counter = 0

    def read(self, data):
        FakeShiInterface.read_inputs(self, data.inputs)
        FakeShiInterface.read_holdings(self, data.holdings)

    def read_inputs(self, inputs):
        inputs[0].raw = 3
        FakeShiInterface.read_counter += 1

    def read_holdings(self, holdings):
        holdings[1].raw = 5
        FakeShiInterface.read_counter += 1

    def write(self, data):
        return FakeShiInterface.write_holdings(self, data.holdings)

    def write_holdings(self, holdings):
        FakeShiInterface.write_counter += 1
        return True

def fake_resolve_version(modbus_interface):
    return (3, 99, 11, 0)

###############################################################################
# Tests
###############################################################################

@patch("luxtronik.LuxtronikSocketInterface", FakeSocketInterface)
@patch("luxtronik.LuxtronikSocketInterface._connect", FakeSocketInterface._connect)
@patch("luxtronik.LuxtronikSocketInterface._disconnect", FakeSocketInterface._disconnect)
@patch("luxtronik.LuxtronikSocketInterface.read_parameters", FakeSocketInterface.read_parameters)
@patch("luxtronik.LuxtronikSocketInterface.read_visibilities", FakeSocketInterface.read_visibilities)
@patch("luxtronik.LuxtronikSocketInterface.read_calculations", FakeSocketInterface.read_calculations)
@patch("luxtronik.LuxtronikSmartHomeInterface", FakeShiInterface)
@patch("luxtronik.LuxtronikSmartHomeInterface.read_inputs", FakeShiInterface.read_inputs)
@patch("luxtronik.LuxtronikSmartHomeInterface.read_holdings", FakeShiInterface.read_holdings)
@patch("luxtronik.resolve_version", fake_resolve_version)
class TestLuxtronik:

    def test_if_init(self):
        l = LuxtronikInterface('host', 1234, 5678)

        assert l._host == 'host'
        assert l._port == 1234
        assert l._interface._client._port == 5678
        assert l.version == (3, 99, 11, 0)

    def test_if_lock(self):
        l = LuxtronikInterface('host', 1234, 5678)
        l.lock.acquire(blocking=False)
        l.lock.acquire(blocking=False)
        l.lock.release()
        l.lock.release()

    def test_if_create_all_data(self):
        l = LuxtronikInterface('host', 1234, 5678)

        data = l.create_all_data()
        assert type(data) is LuxtronikAllData

    def test_if_read_all(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = LuxtronikInterface('host', 1234, 5678)

        assert FakeSocketInterface.read_counter == 0
        assert FakeShiInterface.read_counter == 0

        data1 = l.read_all()
        assert type(data1) is LuxtronikAllData
        assert data1.parameters.get(0).raw == 2
        assert data1.inputs[0].raw == 3
        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 2

        data2 = l.read(data1)
        assert data1 == data2
        assert FakeSocketInterface.read_counter == 6
        assert FakeShiInterface.read_counter == 4

    def test_if_write_all(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = LuxtronikInterface('host', 1234, 5678)

        assert FakeSocketInterface.write_counter == 0
        assert FakeShiInterface.write_counter == 0

        p = Parameters()
        result = l.write_all(p)
        assert result
        assert FakeSocketInterface.write_counter == 1
        assert FakeShiInterface.write_counter == 0

        d = LuxtronikAllData()
        data = l.write_and_read(d)
        assert data == d
        assert data.inputs[0].raw == 3
        assert FakeSocketInterface.write_counter == 2
        assert FakeShiInterface.write_counter == 1

        h = Holdings()
        result = l.write_all(h)
        assert result
        assert FakeSocketInterface.write_counter == 2
        assert FakeShiInterface.write_counter == 2

        s = LuxtronikSmartHomeData()
        result = l.write(s)
        assert result
        assert FakeSocketInterface.write_counter == 2
        assert FakeShiInterface.write_counter == 3

        result = l.write_all(None)
        assert not result
        assert FakeSocketInterface.write_counter == 2
        assert FakeShiInterface.write_counter == 3

    def test_lux_init(self):
        l = Luxtronik('host', 1234, 5678)

        assert isinstance(l, LuxtronikAllData)
        assert isinstance(l.interface, LuxtronikInterface)

    def test_read(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = Luxtronik('host', 1234, 5678)

        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 2

        l.read()
        assert l.parameters.get(0).raw == 2
        assert l.inputs[0].raw == 3
        assert FakeSocketInterface.read_counter == 6
        assert FakeShiInterface.read_counter == 4

    def test_read_parameters(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = Luxtronik('host', 1234, 5678)

        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 2

        l.read_parameters()
        assert l.parameters.get(0).raw == 2
        assert l.inputs[0].raw == 3
        assert FakeSocketInterface.read_counter == 4
        assert FakeShiInterface.read_counter == 2

    def test_read_visibilities(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = Luxtronik('host', 1234, 5678)

        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 2

        l.read_visibilities()
        assert l.visibilities.get(0).raw == 4
        assert l.inputs[0].raw == 3
        assert FakeSocketInterface.read_counter == 4
        assert FakeShiInterface.read_counter == 2

    def test_read_calculations(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = Luxtronik('host', 1234, 5678)

        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 2

        l.read_calculations()
        assert l.calculations.get(0).raw == 6
        assert l.inputs[0].raw == 3
        assert FakeSocketInterface.read_counter == 4
        assert FakeShiInterface.read_counter == 2

    def test_read_inputs(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = Luxtronik('host', 1234, 5678)

        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 2

        l.read_inputs()
        assert l.parameters.get(0).raw == 2
        assert l.inputs[0].raw == 3
        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 3

    def test_read_holdings(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = Luxtronik('host', 1234, 5678)

        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 2

        l.read_holdings()
        assert l.parameters.get(0).raw == 2
        assert l.holdings[1].raw == 5
        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.read_counter == 3

    def test_write(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = Luxtronik('host', 1234, 5678)

        assert FakeSocketInterface.write_counter == 0
        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.write_counter == 0
        assert FakeShiInterface.read_counter == 2

        result = l.write()
        assert result
        assert FakeSocketInterface.write_counter == 1
        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.write_counter == 1
        assert FakeShiInterface.read_counter == 2

        data = LuxtronikAllData()
        result = l.write(data)
        assert result
        assert FakeSocketInterface.write_counter == 2
        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.write_counter == 2
        assert FakeShiInterface.read_counter == 2

    def test_write_and_read(self):
        FakeSocketInterface.reset()
        FakeShiInterface.reset()
        l = Luxtronik('host', 1234, 5678)

        assert FakeSocketInterface.write_counter == 0
        assert FakeSocketInterface.read_counter == 3
        assert FakeShiInterface.write_counter == 0
        assert FakeShiInterface.read_counter == 2

        result = l.write_and_read()
        assert result
        assert FakeSocketInterface.write_counter == 1
        assert FakeSocketInterface.read_counter == 6
        assert FakeShiInterface.write_counter == 1
        assert FakeShiInterface.read_counter == 4

        data = LuxtronikAllData()
        result = l.write_and_read(data)
        assert result
        assert FakeSocketInterface.write_counter == 2
        assert FakeSocketInterface.read_counter == 9
        assert FakeShiInterface.write_counter == 2
        assert FakeShiInterface.read_counter == 6
