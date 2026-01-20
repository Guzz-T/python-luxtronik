from luxtronik.constants import LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE
from luxtronik.definitions import LuxtronikDefinition
from luxtronik.data_vector import (
    get_data_arr,
    integrate_data,
)

###############################################################################
# Tests
###############################################################################

class TestDefinitionFieldPair:

    def test_data_arr(self):
        definition = LuxtronikDefinition.unknown(2, 'Foo', 30)
        field = definition.create_field()
        field.concatenate_multiple_data_chunks = False

        # get from value
        definition._count = 1
        field.raw = 5
        arr = get_data_arr(definition, field)
        assert arr == [5]

        # get from array
        definition._count = 2
        field.raw = [7, 3]
        arr = get_data_arr(definition, field)
        assert arr == [7, 3]

        # too much data
        definition._count = 2
        field.raw = [4, 8, 1]
        arr = get_data_arr(definition, field)
        assert arr is None

        # insufficient data
        definition._count = 2
        field.raw = [9]
        arr = get_data_arr(definition, field)
        assert arr is None

        field.concatenate_multiple_data_chunks = True

        # get from array
        definition._count = 2
        field.raw = 0x0007_0003
        arr = get_data_arr(definition, field)
        assert arr == [7, 3]

        # too much data
        definition._count = 2
        field.raw = 0x0004_0008_0001
        arr = get_data_arr(definition, field)
        assert arr == [8, 1]

        # insufficient data
        definition._count = 2
        field.raw = 0x0009
        arr = get_data_arr(definition, field)
        assert arr == [0, 9]

    def test_integrate(self):
        definition = LuxtronikDefinition.unknown(2, 'Foo', 30)
        field = definition.create_field()
        field.concatenate_multiple_data_chunks = False

        data = [1, LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE, 3, 4, 5, 6, 7]

        # set array
        definition._count = 2
        definition._num_bits = 64
        definition._data_type = 'INT64'
        integrate_data(definition, field, data)
        assert field.raw == [3, 4]
        integrate_data(definition, field, data, 4)
        assert field.raw == [5, 6]
        integrate_data(definition, field, data, 7)
        assert field.raw is None
        integrate_data(definition, field, data, 0)
        assert field.raw == [1, LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE]

        # set value
        definition._count = 1
        definition._num_bits = 32
        definition._data_type = 'INT32'
        integrate_data(definition, field, data)
        assert field.raw == 3
        integrate_data(definition, field, data, 5)
        assert field.raw == 6
        integrate_data(definition, field, data, 9)
        assert field.raw is None
        integrate_data(definition, field, data, 1)
        # Currently there is no magic "not available" value for 32 bit values -> not None
        # This applies also to similar lines below
        assert field.raw == LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE

        field.concatenate_multiple_data_chunks = True

        # set array
        definition._count = 2
        definition._num_bits = 64
        definition._data_type = 'INT64'
        integrate_data(definition, field, data)
        assert field.raw == 0x00000003_00000004
        integrate_data(definition, field, data, 4)
        assert field.raw == 0x00000005_00000006
        integrate_data(definition, field, data, 7)
        assert field.raw is None
        integrate_data(definition, field, data, 0)
        assert field.raw == 0x00000001_00007FFF

        # set value
        definition._count = 1
        definition._num_bits = 32
        definition._data_type = 'INT32'
        integrate_data(definition, field, data)
        assert field.raw == 0x00000003
        integrate_data(definition, field, data, 5)
        assert field.raw == 0x00000006
        integrate_data(definition, field, data, 9)
        assert field.raw is None
        integrate_data(definition, field, data, 1)
        assert field.raw == 0x00007FFF

        field.concatenate_multiple_data_chunks = False

        # set array
        definition._count = 2
        definition._num_bits = 32
        definition._data_type = 'INT32'
        integrate_data(definition, field, data)
        assert field.raw == [3, 4]
        integrate_data(definition, field, data, 4)
        assert field.raw == [5, 6]
        integrate_data(definition, field, data, 7)
        assert field.raw is None
        integrate_data(definition, field, data, 0)
        assert field.raw == [1, LUXTRONIK_VALUE_FUNCTION_NOT_AVAILABLE]

        # set value
        definition._count = 1
        definition._num_bits = 16
        definition._data_type = 'INT16'
        integrate_data(definition, field, data)
        assert field.raw == 3
        integrate_data(definition, field, data, 5)
        assert field.raw == 6
        integrate_data(definition, field, data, 9)
        assert field.raw is None
        integrate_data(definition, field, data, 1)
        assert field.raw is None

        field.concatenate_multiple_data_chunks = True

        # set array
        definition._count = 2
        definition._num_bits = 32
        definition._data_type = 'INT32'
        integrate_data(definition, field, data)
        assert field.raw == 0x0003_0004
        integrate_data(definition, field, data, 4)
        assert field.raw == 0x0005_0006
        integrate_data(definition, field, data, 7)
        assert field.raw is None
        integrate_data(definition, field, data, 0)
        assert field.raw == 0x0001_7FFF

        # set value
        definition._count = 1
        definition._num_bits = 16
        definition._data_type = 'INT16'
        integrate_data(definition, field, data)
        assert field.raw == 0x0003
        integrate_data(definition, field, data, 5)
        assert field.raw == 0x0006
        integrate_data(definition, field, data, 9)
        assert field.raw is None
        integrate_data(definition, field, data, 1)
        assert field.raw is None

        field.concatenate_multiple_data_chunks = False
