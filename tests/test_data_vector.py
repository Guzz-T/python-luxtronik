import pytest

from luxtronik.data_vector import LuxtronikFieldDefinition
from luxtronik.datatypes import Base

###############################################################################
# Tests
###############################################################################


class TestFieldDefinition:

    TEST_DATA = {
        'index': 4,
        'count': 3,
        'type': Base,
        'writeable': True,
        'names': ['Test1', 'Test2'],
        'since': 'v1',
        'until': 'v3',
        'description': 'foo',
    }
    DEFAULT_DATA = LuxtronikFieldDefinition.DEFAULT_DATA
    TEST_FIELD = Base('TestField', True)
    TEST_ARRAY = [13, 10, 14, 12, 18, 11, 16, 15, 17, 19]

    def test_init_norm(self):
        definition = LuxtronikFieldDefinition(self.TEST_DATA, 'Bar')

        names = self.TEST_DATA['names'] + ['Unknown_Bar_4']
        assert definition.index == self.TEST_DATA['index']
        assert definition.count == self.TEST_DATA['count']
        assert definition.data_type == self.TEST_DATA['type']
        assert definition.writeable == self.TEST_DATA['writeable']
        assert definition.names == names
        assert definition.name == names[0]
        assert definition.valid == True

    def test_init_invalid(self):
        definition = LuxtronikFieldDefinition.invalid()

        names = self.DEFAULT_DATA['names'] + ['_invalid_']
        assert definition.index == 0
        assert definition.count == self.DEFAULT_DATA['count']
        assert definition.data_type == self.DEFAULT_DATA['type']
        assert definition.writeable == self.DEFAULT_DATA['writeable']
        assert definition.names == names
        assert definition.name == names[0]
        assert definition.valid == False

    def test_init_unknown(self):
        definition = LuxtronikFieldDefinition.unknown(2, 'Foo')

        names = self.DEFAULT_DATA['names'] + ['Unknown_Foo_2']
        assert definition.index == 2
        assert definition.count == self.DEFAULT_DATA['count']
        assert definition.data_type == self.DEFAULT_DATA['type']
        assert definition.writeable == self.DEFAULT_DATA['writeable']
        assert definition.names == names
        assert definition.name == names[0]
        assert definition.valid == True

    def test_init_field(self):
        definition = LuxtronikFieldDefinition.from_field(8, self.TEST_FIELD, 'Tests')

        names = [self.TEST_FIELD.name, 'Unknown_Tests_8']
        assert definition.index == 8
        assert definition.count == self.DEFAULT_DATA['count']
        assert definition.data_type == Base
        assert definition.writeable == self.TEST_FIELD.writeable
        assert definition.names == names
        assert definition.name == names[0]
        assert definition.valid == True


    def test_field_norm(self):
        definition = LuxtronikFieldDefinition(self.TEST_DATA, 'Bar')
        field = definition.create_field()

        assert field.name == definition.name
        assert field.writeable == definition.writeable

    def test_field_invalid(self):
        definition = LuxtronikFieldDefinition.invalid()
        field = definition.create_field()

        assert field == None

    def test_field_unknown(self):
        definition = LuxtronikFieldDefinition.unknown(2, 'Foo')
        field = definition.create_field()

        assert field.name == definition.name
        assert field.writeable == definition.writeable

    def test_field_field(self):
        definition = LuxtronikFieldDefinition.from_field(8, self.TEST_FIELD, 'Tests')
        field = definition.create_field()

        assert field.name == definition.name
        assert field.writeable == definition.writeable


    def test_extract_norm(self):
        definition = LuxtronikFieldDefinition(self.TEST_DATA, 'Bar')

        data_arr = definition.extract_raw(self.TEST_ARRAY)
        assert data_arr == self.TEST_ARRAY[definition.index:definition.index+definition.count]

        data_arr = definition.extract_raw(self.TEST_ARRAY, 3)
        assert data_arr == self.TEST_ARRAY[3:3+definition.count]

        data_arr = definition.extract_raw(self.TEST_ARRAY, len(self.TEST_ARRAY)-2)
        assert data_arr == None

    def test_extract_invalid(self):
        definition = LuxtronikFieldDefinition.invalid()

        data_arr = definition.extract_raw(self.TEST_ARRAY)
        assert data_arr == self.TEST_ARRAY[0]

        data_arr = definition.extract_raw(self.TEST_ARRAY, 1)
        assert data_arr == self.TEST_ARRAY[1]

        try:
            data_arr = definition.extract_raw(self.TEST_ARRAY, len(self.TEST_ARRAY)+1)
            assert False, "No assertion occurred!"
        except:
            pass

    def test_extract_unknown(self):
        definition = LuxtronikFieldDefinition.unknown(2, 'Foo')

        data_arr = definition.extract_raw(self.TEST_ARRAY)
        assert data_arr == self.TEST_ARRAY[definition.index]

    def test_extract_field(self):
        definition = LuxtronikFieldDefinition.from_field(8, self.TEST_FIELD, 'Tests')

        data_arr = definition.extract_raw(self.TEST_ARRAY)
        assert data_arr == self.TEST_ARRAY[definition.index]


    # the get_raw implicit tests get_data_arr
    def test_raw_norm(self):
        definition = LuxtronikFieldDefinition(self.TEST_DATA, 'Bar')

        self.TEST_FIELD.raw = [2, 2, 3]
        data_arr = definition.get_raw(self.TEST_FIELD)
        assert data_arr == [2, 2, 3]

        self.TEST_FIELD.raw = [2, 2]
        data_arr = definition.get_raw(self.TEST_FIELD)
        assert data_arr == None

        self.TEST_FIELD.raw = [1, 2, 3, 6]
        data_arr = definition.get_raw(self.TEST_FIELD)
        assert data_arr == [1, 2, 3]

        self.TEST_FIELD.raw = 8
        data_arr = definition.get_raw(self.TEST_FIELD)
        assert data_arr == None

    def test_raw_unknown(self): # same as with invalid and field
        definition = LuxtronikFieldDefinition.unknown(2, 'Foo')

        self.TEST_FIELD.raw = 4
        data_arr = definition.get_raw(self.TEST_FIELD)
        assert data_arr == [4]

        self.TEST_FIELD.raw = [2, 2, 3]
        data_arr = definition.get_raw(self.TEST_FIELD)
        assert data_arr == [2]

        self.TEST_FIELD.raw = []
        data_arr = definition.get_raw(self.TEST_FIELD)
        assert data_arr == None