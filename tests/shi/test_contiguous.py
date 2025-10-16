
from luxtronik.datatypes import Base
from luxtronik.shi.definitions import LuxtronikFieldDefinition
from luxtronik.shi.contiguous import (
    ContiguousDataPart,
    ContiguousDataBlock,
    ContiguousDataBlockList,
)


def_a1 = LuxtronikFieldDefinition({
    'index': 1,
    'count': 1,
}, 'test', 100)
def_a = LuxtronikFieldDefinition({
    'index': 1,
    'count': 2,
}, 'test', 100)
def_b = LuxtronikFieldDefinition({
    'index': 3,
    'count': 1,
}, 'test', 100)
def_c = LuxtronikFieldDefinition({
    'index': 4,
    'count': 3,
}, 'test', 100)
def_c1 = LuxtronikFieldDefinition({
    'index': 4,
    'count': 1,
}, 'test', 100)
def_c2 = LuxtronikFieldDefinition({
    'index': 5,
    'count': 1,
}, 'test', 100)
defs = []

field_a1 = Base('field_a')
field_a  = Base('field_a')
field_b  = Base('field_b')
field_c  = Base('field_c')
field_c1 = Base('field_c1')
field_c2 = Base('field_c2')


class TestContiguousDataPart:

    def test_init(self):
        part = ContiguousDataPart(def_a, field_a)
        assert part.index == 1
        assert part.addr == 101
        assert part.count == 2
        assert part.field == field_a
        assert part.definition == def_a

    def test_repr(self):
        part = ContiguousDataPart(def_a, None)
        assert repr(part) == "(1, 2)"

    def test_get_data(self):
        part = ContiguousDataPart(def_a, field_a)
        field_a.raw = [4, 2]
        assert part.get_data_arr() == [4, 2]

        field_a.raw = [1, 3, 5]
        assert part.get_data_arr() == [1, 3]

        field_a.raw = [9]
        assert part.get_data_arr() == None

        part = ContiguousDataPart(def_a1, field_a1)

        field_a1.raw = [8]
        assert part.get_data_arr() == [8]

        field_a1.raw = 7
        assert part.get_data_arr() == [7]

    def test_integrate_data(self):
        part = ContiguousDataPart(def_a, field_a)

        part.integrate_data([1, 5, 7, 9], 0)
        assert part.field.raw == [1, 5]

        part.integrate_data([1, 5, 7, 9])
        assert part.field.raw == [5, 7]

        part.integrate_data([1, 5, 7, 9], 2)
        assert part.field.raw == [7, 9]

        part.integrate_data([1, 5, 7, 9], 3)
        assert part.field.raw == None

        part.integrate_data([1, 5, LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE, 9], 1)
        assert part.field.raw == None

        part = ContiguousDataPart(def_c1, field_c1)

        part.integrate_data([2, 4, 6], 1)
        assert part.field.raw == 4

        part.integrate_data([2, 4, LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE], 2)
        assert part.field.raw == None

        part.integrate_data([2, 4, 6], 5)
        assert part.field.raw == None


class TestContiguousDataBlock:

    def test_clear(self):
        block = ContiguousDataBlock()
        block.add(def_a, None)
        block.add(def_b, None)
        block.add(def_c, None)
        block.clear()
        assert len(block) == 0
        assert block._last_idx == -1

    def test_iter(self):
        block = ContiguousDataBlock.create_and_add(def_a, None)
        block.add(def_b, None)
        block.add(def_c, None)
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

        can_add = block.can_add(def_b)
        assert can_add == True
        block.add(def_b, None)
        assert len(block) == 1

        can_add = block.can_add(def_c2)
        assert can_add == False
        block.add(def_c2, None)
        assert len(block) == 2

        can_add = block.can_add(def_a)
        assert can_add == False
        block.add(def_a, None)
        assert len(block) == 3

    def test_first_index(self):
        block = ContiguousDataBlock()
        assert block.first_index == 0

        block.add(def_b,field_b)
        block.add(def_c, field_c)

        assert block.first_index == 3
        assert block.first_addr == 103
        assert block.overall_count == 4

    def test_overall_count(self):
        block = ContiguousDataBlock()
        assert block.overall_count == 0

        # Several parts for one register
        block.add(def_a1, field_a1)
        block.add(def_a, field_a)
        block.add(def_b, field_b)
        block.add(def_c, field_c)
        block.add(def_c1, field_c1)
        block.add(def_c2, field_c2)

        assert block.first_index == 1
        assert block.first_addr == 101
        assert block.overall_count == 6

    def test_integrate_data(self):
        block = ContiguousDataBlock()

        block.add(def_a1, field_a1)
        block.add(def_a, field_a)
        block.add(def_b, field_b)

        valid = block.integrate_data(None)
        assert not valid

        valid = block.integrate_data([11, 12, 13])
        assert valid == True
        assert block[0].field.raw == 11
        assert block[1].field.raw == [11, 12]
        assert block[2].field.raw == 13

        block.add(def_c, field_c)

        block.integrate_data([7, 6, 5, 4, 3, 2])
        assert valid == True
        assert block[0].field.raw == 7
        assert block[1].field.raw == [7, 6]
        assert block[2].field.raw == 5
        assert block[3].field.raw == [4, 3, 2]

        block.add(def_c1, field_c1)
        block.add(def_c2, field_c2)

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
        block = ContiguousDataBlock()

        # Multiple data for a single register #1
        field_a1.raw = 35
        field_a.raw = [56, 57]
        block.add(def_a1, field_a1)
        block.add(def_a, field_a)

        data_arr = block.get_data_arr()
        assert data_arr == None

        block = ContiguousDataBlock()
        field_b.raw = 11
        field_c.raw = [21, 22, 23]
        block.add(def_b, field_b)
        block.add(def_c, field_c)

        data_arr = block.get_data_arr()
        assert data_arr == [11, 21, 22, 23]

        # To less data for one register
        field_c.raw = [21, 22]
        data_arr = block.get_data_arr()
        assert data_arr == None

        # Multiple data for a single register #2
        field_b.raw = 11
        field_c.raw = [21, 22, 23]
        field_c1.raw = 6
        field_c2.raw = 7
        block.add(def_c1, field_c1)
        block.add(def_c2, field_c2)

        data_arr = block.get_data_arr()
        assert data_arr == None



class TestContiguousDataBlockList:

    def test_init(self):
        blocks = ContiguousDataBlockList('foo', True)
        assert len(blocks) == 0
        assert blocks.type_name == 'foo'
        assert blocks.read_not_write == True

    def test_iter(self):
        blocks = ContiguousDataBlockList('foo', True)
        blocks.append_single(def_a, None)
        blocks.append_single(def_b, None)
        blocks.collect(def_c1, None)
        blocks.collect(def_c2, None)
        assert len(blocks) == 3
        for index, block in enumerate(blocks):
            if index == 0:
                assert len(block) == 1
                assert block.first_index == 1
                assert block.overall_count == 2
            if index == 1:
                assert len(block) == 1
                assert block.first_index == 3
                assert block.overall_count == 1
            if index == 2:
                assert len(block) == 2
                assert block.first_index == 4
                assert block.overall_count == 2

        blocks.clear()
        assert len(blocks) == 0

    def test_collect(self):
        blocks = ContiguousDataBlockList('foo', True)
        # First block
        blocks.collect(def_c1, None)
        blocks.collect(def_c2, None)
        # Second block
        blocks.collect(def_b, None)
        blocks.collect(def_c, None)
        # Third block
        blocks.collect(def_a1, None)
        blocks.collect(def_a, None)
        # Fourth block
        blocks.append_single(def_b, None)
        # Fifth block
        blocks.collect(def_c, None)

        assert len(blocks) == 5
        assert blocks[0].first_index == 4
        assert blocks[0].overall_count == 2
        assert blocks[1].first_index == 3
        assert blocks[1].overall_count == 4
        assert blocks[2].first_index == 1
        assert blocks[2].overall_count == 2
        assert blocks[3].first_index == 3
        assert blocks[3].overall_count == 1
        assert blocks[4].first_index == 4
        assert blocks[4].overall_count == 3

    def test_append(self):
        blocks = ContiguousDataBlockList('foo', True)

        block = ContiguousDataBlock()
        block.add(def_a, None)
        block.add(def_b, None)
        block.add(def_c, None)

        blocks.append(block)
        assert len(blocks) == 1
        assert blocks[0].first_index == 1
        assert blocks[0].overall_count == 6





# class TestContiguousDataBlocksHandler:

#     def test_collect1(self):
#         handler = ContiguousDataBlocksHandler()

#         handler.collect(None, def_a1)
#         assert handler._start_idx == def_a1.index
#         assert handler._next_index == def_a1.index + def_a1.count

#         handler.collect(None, def_a)
#         assert handler._start_idx == def_a1.index
#         assert handler._next_index == def_a.index + def_a.count

#         handler.collect(None, def_b)
#         assert handler._start_idx == def_a1.index
#         assert handler._next_index == def_b.index + def_b.count

#         handler.collect(None, def_c)
#         assert handler._start_idx == def_a1.index
#         assert handler._next_index == def_c.index + def_c.count

#         handler.collect(None, def_c1)
#         assert handler._start_idx == def_a1.index
#         assert handler._next_index == def_c.index + def_c.count

#         handler.collect(None, def_c2)
#         assert handler._start_idx == def_a1.index
#         assert handler._next_index == def_c.index + def_c.count

#     def test_collect2(self):
#         handler = ContiguousDataBlocksHandler()

#         handler.collect(None, def_a)
#         assert handler._start_idx == def_a.index
#         assert handler._next_index == def_a.index + def_a.count

#         handler.collect(None, def_c)
#         assert handler._start_idx == def_c.index
#         assert handler._next_index == def_c.index + def_c.count

#     def test_read_telegram(self):
#         handler = ContiguousDataBlocksHandler()

#         handler.collect(None, def_a)
#         handler.collect(None, def_c)
#         handler.collect(None, def_c1)

#         telegrams = handler.create_read_telegrams(50)
#         assert len(telegrams) == 2
#         assert telegrams[0].addr == def_a.index + 50
#         assert telegrams[0].count == def_a.count
#         assert telegrams[1].addr == def_c.index + 50
#         assert telegrams[1].count == def_c.count

#     def test_write_telegram(self):
#         handler = ContiguousDataBlocksHandler()

#         field_a.raw = [1, 2]
#         field_c.raw = [5, 6, 7]
#         handler.collect(field_a, def_a)
#         handler.collect(field_c, def_c)

#         telegrams = handler.create_write_telegrams(60)
#         assert len(telegrams) == 2
#         assert telegrams[0].addr == def_a.index + 60
#         assert telegrams[0].count == def_a.count
#         assert telegrams[1].addr == def_c.index + 60
#         assert telegrams[1].count == def_c.count

#         field_c1.raw = 9
#         handler.collect(field_c1, def_c1)
#         telegrams = handler.create_write_telegrams(70)
#         assert len(telegrams) == 1
#         assert telegrams[0].addr == def_a.index + 70
#         assert telegrams[0].count == def_a.count

#     def test_itegrate_data(self):

#         handler = ContiguousDataBlocksHandler()

#         field_a.raw = []
#         field_c.raw = []
#         field_c1.raw = []
#         handler.collect(field_a, def_a)
#         handler.collect(field_c, def_c)
#         handler.collect(field_c1, def_c1)

#         telegrams = handler.create_read_telegrams(20)
#         telegrams[0].data = [11, 12]
#         telegrams[1].data = [25, 26, 27]
#         handler.integrate_data()

#         assert field_a.raw == [11, 12]
#         assert field_c.raw == [25, 26, 27]
#         assert field_c1.raw == 25
