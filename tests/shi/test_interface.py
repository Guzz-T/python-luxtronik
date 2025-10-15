from luxtronik.shi.interface import LuxtronikSmartHomeData, LuxtronikSmartHomeInterface
from luxtronik.shi.modbus import LuxtronikModbusTcpInterface
from luxtronik.holdings import Holdings
from luxtronik.definitions.holdings import HOLDINGS_DEFINITIONS

from luxtronik.datatypes import Base

from luxtronik.shi.common import (
    LuxtronikSmartHomeReadHoldingsTelegram,
    LuxtronikSmartHomeReadInputsTelegram,
    LuxtronikSmartHomeWriteHoldingsTelegram,
)

###############################################################################
# Fake modbus client
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
            # Return None
            self._error = 'Read returned "None"!'
            return None
        elif addr == 1001:
            # Return empty data
            self._error = 'Read returned to less data!'
            return []
        elif addr == 1002:
            # Return too much data
            self._error = 'Read returned to few data!'
            return [0] * 16
        else:
            # Return the addr as value(s)
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
            # Return true
            self._error = 'None'
            return True
        else:
            # Return false
            self._error = 'Write error!'
            return False

###############################################################################
# Tests
###############################################################################

class TestLuxtronikSmartHomeData:

    def test_init(self):
        data1 = LuxtronikSmartHomeData()

        assert data1.holdings is not None
        assert data1.inputs is not None

        data2 = LuxtronikSmartHomeData(data1.holdings)
        assert data2.holdings == data1.holdings
        assert data2.inputs != data1.inputs


class TestLuxtronikSmartHomeInterface:
    host = 'local'
    port = 1234

    @classmethod
    def setup_class(cls):
        cls.interface = LuxtronikSmartHomeInterface.from_modbus_tcp(cls.host, cls.port)
        cls.interface._interface._client = FakeModbusClient(cls.host, cls.port)

    def test_init(self):
        assert isinstance(self.interface._interface._client, FakeModbusClient)

    def test_get_index(self):
        idx = self.interface._get_index_from_name('a_b_3')
        assert idx == 3

        idx = self.interface._get_index_from_name('unknown_test_111')
        assert idx == 111

        idx = self.interface._get_index_from_name('unknown_111')
        assert idx == None

        idx = self.interface._get_index_from_name('unknown_111_test')
        assert idx == None


    def test_get_definition(self):
        definition = self.interface._get_definition(0, Holdings)
        assert definition == HOLDINGS_DEFINITIONS[0]

        definition = self.interface._get_definition("Heating_state", Holdings)
        assert definition == HOLDINGS_DEFINITIONS[2]

        definition = self.interface._get_definition(49, Holdings)
        assert definition.index == 49
        assert definition.count == 1
        assert definition.name == "Unknown_Holding_49"

        definition = self.interface._get_definition("Unknown_Holding_0", Holdings)
        assert definition.index == 0
        assert definition.count == 1
        assert definition.name == "Unknown_Holding_0"



    def test_create_telegram(self):

        block = ContiguousDataBlock()
        block.add(def_a1, field_a1)
        block.add(def_a, field_a)
        telegram = block.create_telegram('holding', True)
        assert isinstance(telegram, LuxtronikSmartHomeReadHoldingsTelegram)
        assert telegram.addr == 101
        assert telegram.count == 2
        assert telegram.data == []


        block = ContiguousDataBlock()
        block.add(def_b, field_b)
        block.add(def_c, field_c)
        field_b.raw = 1
        field_c.raw = [5, 2, 3]
        telegram = block.create_telegram('holding', False)
        assert isinstance(telegram, LuxtronikSmartHomeWriteHoldingsTelegram)
        assert telegram.addr == 103
        assert telegram.count == 4
        assert telegram.data == [1, 5, 2, 3]

        field_b.raw = 1
        field_c.raw = [5, 3]
        telegram = block.create_telegram('holding', False)
        assert telegram is None

        block = ContiguousDataBlock()
        block.add(def_b, field_b)
        block.add(def_c, field_c)
        telegram = block.create_telegram('input', True)
        assert isinstance(telegram, LuxtronikSmartHomeReadInputsTelegram)
        assert telegram.addr == 103
        assert telegram.count == 4
        assert telegram.data == []
