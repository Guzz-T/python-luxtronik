from luxtronik.datatypes import Base
from luxtronik.definitions import Keys, LuxtronikDefinitionsList
from luxtronik.cfi.vector import DataVectorConfig


###############################################################################
# Tests
###############################################################################

def_list = [
    {
        Keys.IDX: 5,
        Keys.COUNT: 1,
        Keys.NAMES: ["field_5_bit1"],
        Keys.BIT_OFFS: 0,
        Keys.BIT_CNT: 1,
        Keys.TYPE: Base,
        Keys.WRT: False,
    },
    {
        Keys.IDX: 5,
        Keys.COUNT: 1,
        Keys.NAMES: ["field_5_bit2"],
        Keys.BIT_OFFS: 1,
        Keys.BIT_CNT: 3,
        Keys.TYPE: Base,
        Keys.WRT: False,
    },
    {
        Keys.IDX: 5,
        Keys.COUNT: 1,
        Keys.NAMES: ["field_5_all"],
        Keys.TYPE: Base,
        Keys.WRT: False,
    },
    {
        Keys.IDX: 7,
        Keys.COUNT: 2,
        Keys.NAMES: ["field_7"],
        Keys.TYPE: Base,
        Keys.WRT: True,
    },
    {
        Keys.IDX: 9,
        Keys.COUNT: 2,
        Keys.NAMES: ["field_9"],
        Keys.TYPE: Base,
        Keys.WRT: True,
    }
]
TEST_DEFINITIONS = LuxtronikDefinitionsList(def_list, 'foo', 100, 'INT32')

FIELD_11_DICT = {
    Keys.IDX: 11,
    Keys.COUNT: 1,
    Keys.NAMES: ["field_11"],
    Keys.TYPE: Base,
    Keys.WRT: True,
}
FIELD_12_DICT = {
    Keys.IDX: 12,
    Keys.COUNT: 1,
    Keys.NAMES: ["field_12"],
    Keys.TYPE: Base,
    Keys.WRT: True,
}

class DataVectorTest(DataVectorConfig):
    name = 'foo'
    definitions = TEST_DEFINITIONS

class TestDataVector:

    def test_add(self):
        data_vector = DataVectorTest.empty()
        assert len(data_vector) == 0

        # In case the definitions are added after the creation
        data_vector.definitions.add(FIELD_11_DICT)
        data_vector.definitions.add(FIELD_12_DICT)

        # Add available index
        field = data_vector.add(11)
        assert len(data_vector) == 1
        assert 11 in data_vector
        assert field.name == 'field_11'

        # Add not available index (not existing)
        field = data_vector.add(13)
        assert 'field_6' not in data_vector
        assert field is None
        assert len(data_vector) == 1

        # Re-add available index
        field = data_vector.add(11)
        assert len(data_vector) == 1
        assert field.name == 'field_11'

        # Add available field
        field_12 = Base('field_12', False)
        field = data_vector.add(field_12)
        assert 12 in data_vector
        assert len(data_vector) == 2
        assert field == field_12

        # Re-add available field
        field = data_vector.add(field_12)
        assert field_12 in data_vector
        assert len(data_vector) == 2
        assert field == field_12
