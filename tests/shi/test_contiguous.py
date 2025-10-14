
from luxtronik.shi.definitions import LuxtronikFieldDefinition
from luxtronik.datatypes import Base


def_a1 = LuxtronikFieldDefinition({
    'index': 1,
    'count': 1,
}, 'test', 0)
def_a = LuxtronikFieldDefinition({
    'index': 1,
    'count': 2,
}, 'test', 0)
def_b = LuxtronikFieldDefinition({
    'index': 3,
    'count': 1,
}, 'test', 0)
def_c = LuxtronikFieldDefinition({
    'index': 4,
    'count': 3,
}, 'test', 0)
def_c1 = LuxtronikFieldDefinition({
    'index': 4,
    'count': 1,
}, 'test', 0)
def_c2 = LuxtronikFieldDefinition({
    'index': 5,
    'count': 1,
}, 'test', 0)
defs = []

field_a1 = Base('field_a')
field_a = Base('field_a')
field_b = Base('field_b')
field_c = Base('field_c')
field_c1 = Base('field_c1')
field_c2 = Base('field_c2')


class TestContiguousDataPart:

    def test_init(self):
        part = ContiguousDataPart(field_a, def_a)
        assert part.index == 1
        assert part.count == 2
        assert part.field == field_a
        assert part.definition == def_a

    def test_str(self):
        part = ContiguousDataPart(None, def_a)
        assert str(part) == "(1, 2)"


class TestContiguousDataBlock:

    def test_iter(self):
        block = ContiguousDataBlock('unknown', True)
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
        block = ContiguousDataBlock('unknown', True)

        added = block.add(None, def_a)
        assert added == True
        added = block.add(None, def_c)
        assert added == False

    def test_first_index(self):
        block = ContiguousDataBlock('unknown', True)
        block.add(field_b, def_b)
        block.add(field_c, def_c)

        assert block.first_index == 3
        assert block.overall_count == 4

    def test_overall_count(self):
        block = ContiguousDataBlock('unknown', True)

        # Several parts for one register
        block.add(field_a1, def_a1)
        block.add(field_a, def_a)
        block.add(field_b, def_b)
        block.add(field_c, def_c)
        block.add(field_c1, def_c1)
        block.add(field_c2, def_c2)

        assert block.first_index == 1
        assert block.overall_count == 6

    def test_integrate_data(self):
        block = ContiguousDataBlock('unknown', True)

        block.add(field_a1, def_a1)
        block.add(field_a, def_a)
        block.add(field_b, def_b)

        valid = block.integrate_data([11, 12, 13])
        assert valid == True
        assert block[0].field.raw == 11
        assert block[1].field.raw == [11, 12]
        assert block[2].field.raw == 13

        block.add(field_c, def_c)

        block.integrate_data([7, 6, 5, 4, 3, 2])
        assert valid == True
        assert block[0].field.raw == 7
        assert block[1].field.raw == [7, 6]
        assert block[2].field.raw == 5
        assert block[3].field.raw == [4, 3, 2]

        block.add(field_c1, def_c1)
        block.add(field_c2, def_c2)

        block.integrate_data([21, 22, 23, 24, 25, 26])
        assert valid == True
        assert block[0].field.raw == 21
        assert block[1].field.raw == [21, 22]
        assert block[2].field.raw == 23
        assert block[3].field.raw == [24, 25, 26]
        assert block[4].field.raw == 24
        assert block[5].field.raw == 25

        valid = block.integrate_data([5, 4, 3])
        assert valid == False

    def test_get_data(self):
        block = ContiguousDataBlock('unknown', True)

        field_a1.raw = 35
        field_a.raw = [56, 57]
        block.add(field_a1, def_a1)
        block.add(field_a, def_a)

        data_arr = block.get_data_arr()
        assert data_arr == None

        block = ContiguousDataBlock('unknown', True)
        field_b.raw = 11
        field_c.raw = [21, 22, 23]
        block.add(field_b, def_b)
        block.add(field_c, def_c)

        data_arr = block.get_data_arr()
        assert data_arr == [11, 21, 22, 23]

        field_c.raw = [21, 22]
        data_arr = block.get_data_arr()
        assert data_arr == None

        field_b.raw = 11
        field_c.raw = [21, 22, 23]
        field_c1.raw = 6
        field_c2.raw = 7
        block.add(field_c1, def_c1)
        block.add(field_c2, def_c2)

        data_arr = block.get_data_arr()
        assert data_arr == None


class TestContiguousDataBlocksHandler:

    def test_collect1(self):
        handler = ContiguousDataBlocksHandler()

        handler.collect(None, def_a1)
        assert handler._start_idx == def_a1.index
        assert handler._next_index == def_a1.index + def_a1.count

        handler.collect(None, def_a)
        assert handler._start_idx == def_a1.index
        assert handler._next_index == def_a.index + def_a.count

        handler.collect(None, def_b)
        assert handler._start_idx == def_a1.index
        assert handler._next_index == def_b.index + def_b.count

        handler.collect(None, def_c)
        assert handler._start_idx == def_a1.index
        assert handler._next_index == def_c.index + def_c.count

        handler.collect(None, def_c1)
        assert handler._start_idx == def_a1.index
        assert handler._next_index == def_c.index + def_c.count

        handler.collect(None, def_c2)
        assert handler._start_idx == def_a1.index
        assert handler._next_index == def_c.index + def_c.count

    def test_collect2(self):
        handler = ContiguousDataBlocksHandler()

        handler.collect(None, def_a)
        assert handler._start_idx == def_a.index
        assert handler._next_index == def_a.index + def_a.count

        handler.collect(None, def_c)
        assert handler._start_idx == def_c.index
        assert handler._next_index == def_c.index + def_c.count

    def test_read_telegram(self):
        handler = ContiguousDataBlocksHandler()

        handler.collect(None, def_a)
        handler.collect(None, def_c)
        handler.collect(None, def_c1)

        telegrams = handler.create_read_telegrams(50)
        assert len(telegrams) == 2
        assert telegrams[0].addr == def_a.index + 50
        assert telegrams[0].count == def_a.count
        assert telegrams[1].addr == def_c.index + 50
        assert telegrams[1].count == def_c.count

    def test_write_telegram(self):
        handler = ContiguousDataBlocksHandler()

        field_a.raw = [1, 2]
        field_c.raw = [5, 6, 7]
        handler.collect(field_a, def_a)
        handler.collect(field_c, def_c)

        telegrams = handler.create_write_telegrams(60)
        assert len(telegrams) == 2
        assert telegrams[0].addr == def_a.index + 60
        assert telegrams[0].count == def_a.count
        assert telegrams[1].addr == def_c.index + 60
        assert telegrams[1].count == def_c.count

        field_c1.raw = 9
        handler.collect(field_c1, def_c1)
        telegrams = handler.create_write_telegrams(70)
        assert len(telegrams) == 1
        assert telegrams[0].addr == def_a.index + 70
        assert telegrams[0].count == def_a.count

    def test_itegrate_data(self):

        handler = ContiguousDataBlocksHandler()

        field_a.raw = []
        field_c.raw = []
        field_c1.raw = []
        handler.collect(field_a, def_a)
        handler.collect(field_c, def_c)
        handler.collect(field_c1, def_c1)

        telegrams = handler.create_read_telegrams(20)
        telegrams[0].data = [11, 12]
        telegrams[1].data = [25, 26, 27]
        handler.integrate_data()

        assert field_a.raw == [11, 12]
        assert field_c.raw == [25, 26, 27]
        assert field_c1.raw == 25
