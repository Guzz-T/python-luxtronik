import pytest

from luxtronik.constants import LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE
from luxtronik.shi_common import LuxtronikSmartHomeReadTelegram, LuxtronikSmartHomeWriteTelegram
from luxtronik.shi_modbus import LuxtronikModbusTcpInterface

###############################################################################
# Fake modbus clients
###############################################################################

class FakeModbusClient:
    can_connect = True

    def __init__(self, host, port=0, timeout=0, *args, **kwargs):
        self._host = host
        self._port = port
        self._timeout = timeout
        self._connected = False
        self._error = 'None'

    def open(self):
        if self.can_connect:
            self._connected = True
        self._error = 'None' if self.can_connect else 'Connection error!'
        return self.can_connect

    def close(self):
        self._connected = False

    @property
    def is_open(self):
        return self._connected

    @property
    def last_error_as_txt(self):
        return self._error

    def _read(self, addr, count):
        if addr == 1000:
            self._error = 'Read returned "None"!'
            return None
        elif addr == 1001:
            self._error = 'Read returned to less data!'
            return []
        elif addr == 1002:
            self._error = 'Read returned to few data!'
            return [0] * 16
        else:
            self._error = 'None'
            values = []
            for i in range(count):
                values += [addr + i]
            return values

    def read_holding_registers(self, addr, count):
        return self._read(addr, count)

    def read_input_registers(self, addr, count):
        return self._read(addr, count)

    def write_multiple_registers(self, addr, data):
        if addr < 1000:
            self._error = 'None'
            return True
        else:
            self._error = 'Write error!'
            return False

###############################################################################
# Tests
###############################################################################

class TestModbusInterface:
    host = "local_host"
    port = 9876

    @classmethod
    def setup_class(cls):
        cls.modbus_interface = LuxtronikModbusTcpInterface(cls.host, cls.port)
        cls.modbus_interface._client = FakeModbusClient(cls.host, cls.port)
        assert isinstance(cls.modbus_interface._client, FakeModbusClient)

    def test_data_type(self):

        result = self.modbus_interface.read_holdings('data')
        assert result == False

        result = self.modbus_interface.read_holdings(0)
        assert result == False

        result = self.modbus_interface.read_holdings([2, 1])
        assert result == False

        result = self.modbus_interface.write_holdings('hello')
        assert result == False

        result = self.modbus_interface.write_holdings(2)
        assert result == False

        result = self.modbus_interface.write_holdings([5, 10])
        assert result == False

        result = self.modbus_interface.read_inputs('test')
        assert result == False

        result = self.modbus_interface.read_inputs(1)
        assert result == False

        result = self.modbus_interface.read_inputs([2, 3])
        assert result == False


    def test_no_holdings_read_data(self):
        data_list = [LuxtronikSmartHomeReadTelegram(0, 0), LuxtronikSmartHomeReadTelegram(0, 0)]

        result = self.modbus_interface.read_holdings(data_list)
        assert result == False
        assert data_list[0].data == []
        assert data_list[1].data == []


    def test_no_holdings_write_data(self):
        data_list = [LuxtronikSmartHomeWriteTelegram(0, []), LuxtronikSmartHomeWriteTelegram(0, [])]

        result = self.modbus_interface.write_holdings(data_list)
        assert result == False


    def test_no_inputs_read_data(self):
        data_list = [LuxtronikSmartHomeReadTelegram(0, 0), LuxtronikSmartHomeReadTelegram(0, 0)]

        result = self.modbus_interface.read_inputs(data_list)
        assert result == False
        assert data_list[0].data == []
        assert data_list[1].data == []


    def test_no_connection(self):
        FakeModbusClient.can_connect = False

        data = LuxtronikSmartHomeReadTelegram(0, 1)
        result = self.modbus_interface.read_holdings(data)
        assert result == False

        data = LuxtronikSmartHomeWriteTelegram(0, [1])
        result = self.modbus_interface.write_holdings(data)
        assert result == False

        data = LuxtronikSmartHomeReadTelegram(0, 1)
        result = self.modbus_interface.read_inputs(data)
        assert result == False

        FakeModbusClient.can_connect = True


    @pytest.mark.parametrize(
        "addr, count, valid, data",
        [
            (1,    2, True,  [1, 2]),
            (5,    3, True,  [5, 6, 7]),
            (0,    0, False, []),
            (1000, 2, False, [LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE] * 2), # client has read error
            (1001, 3, False, [LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE] * 3), # client returns to less data
            (1002, 4, False, [0] * 4),                                      # client returns to much data
        ]
    )
    def test_read_holdings(self, addr, count, valid, data):
        data_item = LuxtronikSmartHomeReadTelegram(addr, count)

        result = self.modbus_interface.read_holdings(data_item)
        assert result == valid
        assert data_item.data == data

        data_arr = self.modbus_interface.read_holdings_raw(addr, count)
        if valid:
            assert data_arr == data
        else:
            assert data_arr == None


    @pytest.mark.parametrize(
        "addr, count, valid, data",
        [
            (1,    2,  True, [1, 2]),
            (5,    3,  True, [5, 6, 7]),
            (0,    0, False, []),
            (1000, 2, False, [LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE] * 2), # client has read error
            (1001, 3, False, [LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE] * 3), # client returns to less data
            (1002, 4, False, [0] * 4),                                      # client returns to much data
        ]
    )
    def test_read_inputs(self, addr, count, valid, data):
        data_item = LuxtronikSmartHomeReadTelegram(addr, count)

        result = self.modbus_interface.read_inputs(data_item)
        assert result == valid
        assert data_item.data == data

        data_arr = self.modbus_interface.read_inputs_raw(addr, count)
        if valid:
            assert data_arr == data
        else:
            assert data_arr == None


    @pytest.mark.parametrize(
        "addr, data, valid",
        [
            (1,       [1, 2],  True),
            (5,    [5, 6, 7],  True),
            (0,           [], False),
            (1000,    [8, 9], False),
        ]
    )
    def test_write_holdings(self, addr, data, valid):
        data_item = LuxtronikSmartHomeWriteTelegram(addr, data)

        result = self.modbus_interface.write_holdings(data_item)
        assert result == valid

        result = self.modbus_interface.write_holdings_raw(addr, data)
        if valid:
            assert result == valid
        else:
            assert result == None
