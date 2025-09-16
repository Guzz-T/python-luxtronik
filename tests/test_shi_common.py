import pytest

from luxtronik.data_vector import LuxtronikFieldDefinition
from luxtronik.datatypes import Base
from luxtronik.shi_common import *

###############################################################################
# Tests
###############################################################################

class TestReadTelegram:

    def test_init(self):
        telegram = LuxtronikSmartHomeReadTelegram(10, 20)
        assert telegram.addr == 10
        assert telegram.count == 20
        assert telegram.data == []


class TestWriteTelegram:

    def test_init(self):
        telegram = LuxtronikSmartHomeWriteTelegram(10, [1, 2, 3])
        assert telegram.addr == 10
        assert telegram.count == 3
        assert telegram.data == [1, 2, 3]

        telegram = LuxtronikSmartHomeWriteTelegram(15, None)
        assert telegram.addr == 15
        assert telegram.count == 0
        assert telegram.data == []


def_a = LuxtronikFieldDefinition({
    'index': 1,
    'count': 2,
}, "Invalids")
def_b = LuxtronikFieldDefinition({
    'index': 3,
    'count': 1,
}, "Invalids")
def_c = LuxtronikFieldDefinition({
    'index': 4,
    'count': 3,
}, "Invalids")

field_b = Base('field_b')
field_c = Base('field_c')


class TestContiguousDataPart:

    def test_init(self):
        part = ContiguousDataPart(None, def_a)
        assert part.index == 1
        assert part.count == 2
        assert part.definition == def_a

    def test_str(self):
        part = ContiguousDataPart(None, def_a)
        assert str(part) == "(1, 2)"


class TestContiguousDataBlock:

    def test_iter(self):
        block = ContiguousDataBlock()
        block.add(None, def_a)
        block.add(None, def_b)
        block.add(None, def_c)
        for index, part in enumerate(block):
            if index == 0:
                assert part.index == 1
                assert part.count == 2
            if index == 1:
                assert part.index == 3
                assert part.count == 1
            if index == 2:
                assert part.index == 4
                assert part.count == 3

    def test_add(self):
        block = ContiguousDataBlock()
        try:
            block.add(None, def_a)
            block.add(None, def_c)
            success = True
        except:
            success = False
        assert success == False


    def test_first_index(self):
        block = ContiguousDataBlock()
        block.add(field_b, def_b)
        block.add(field_c, def_c)

        assert block.first_index == 3

    def test_overall_count(self):
        block = ContiguousDataBlock()
        block.add(field_b, def_b)
        block.add(field_c, def_c)

        assert block.overall_count == 4

    def test_integrate_data(self):
        block = ContiguousDataBlock()
        block.add(field_b, def_b)
        block.add(field_c, def_c)

        block.integrate_data([5, 4, 3, 2])
        assert block[0].field.raw == 5
        assert block[1].field.raw == [4, 3, 2]

        try:
            block.integrate_data([5, 4, 3])
            success = True
        except:
            success = False
        assert success == False



    def test_get_data(self):
        block = ContiguousDataBlock()
        field_b.raw = 11
        field_c.raw = [21, 22, 23]
        block.add(field_b, def_b)
        block.add(field_c, def_c)

        data_arr = block.get_data_arr()
        assert data_arr == [11, 21, 22, 23]

        field_c.raw = [21, 22]
        try:
            data_arr = block.get_data_arr()
            success = True
        except:
            success = False
        assert success == False