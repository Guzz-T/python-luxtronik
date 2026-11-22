
from luxtronik.datatypes import (
    Base,
    Unknown,
    FullVersion,
    Version,
    MajorMinorVersion
)
from luxtronik.definitions import (
    Keys,
    LuxtronikDefinition,
    LuxtronikDefinitionsDictionary,
    LuxtronikDefinitionsList,
    get_version_definitions,
)
from luxtronik.version import VER_IGNORE, VersionRequirement, VersionRequirements
import operator

###############################################################################
# Tests
###############################################################################

class TestDefinition:

    TEST_DATA = {
        'index': 4,
        'count': 3,
        'type': Base,
        'writeable': True,
        'names': ['test1', 'test2'],
        'successor': 'abcd',
        'datatype': 'INT16',
        'version': '>=1.1,<=3.16.7',
        'description': 'foo',
    }
    DEFAULT_DATA = LuxtronikDefinition.DEFAULT_DATA
    TEST_FIELD = Base('TestField', True)
    TEST_ARRAY = [13, 10, 14, 12, 18, 11, 16, 15, 17, 19]

    def test_init(self):
        definition = LuxtronikDefinition(self.TEST_DATA, 'Bar', 20)

        names = self.TEST_DATA['names']
        assert definition.index == self.TEST_DATA['index']
        assert definition.count == self.TEST_DATA['count']
        assert definition.field_type == self.TEST_DATA['type']
        assert definition.writeable == self.TEST_DATA['writeable']
        assert definition.names == names
        assert definition.name == names[0]
        assert definition.successor == 'abcd'
        assert definition.data_type == 'INT16'
        assert definition.valid
        assert definition
        assert definition.type_name == 'bar'
        assert definition.offset == 20
        assert definition.addr == 20 + self.TEST_DATA['index']
        assert definition.num_bits == 16
        vr = VersionRequirements([
            VersionRequirement(operator.ge, (1, 1, 0, 0)),
            VersionRequirement(operator.le, (3, 16, 7, 0))
        ])
        assert definition.version == vr

        definition = LuxtronikDefinition({
            'index': 10,
            'names': []
        }, 'Bar', 20)
        assert definition.valid
        assert definition.index == 10
        assert definition.name == '_invalid_'
        assert not definition.writeable

    def test_init_unknown(self):
        definition = LuxtronikDefinition.unknown(2, 'Foo', 30)

        names = ['unknown_foo_2']
        assert definition.index == 2
        assert definition.count == self.DEFAULT_DATA['count']
        assert definition.field_type == self.DEFAULT_DATA['type']
        assert definition.writeable == self.DEFAULT_DATA['writeable']
        assert definition.names == names
        assert definition.name == names[0]
        assert definition.valid
        assert definition
        assert definition.type_name == 'foo'
        assert definition.offset == 30
        assert definition.addr == 30 + 2
        vr = VersionRequirements([])
        assert definition.version == vr

    def test_init_invalid(self):
        # create invalid
        definition = LuxtronikDefinition.unknown(-3, '', 10)
        assert not definition.valid

        # trigger exception
        try:
            definition = LuxtronikDefinition.unknown(-3, '', 'foo')
            assert False
        except Exception:
            pass

    def test_create_field(self):
        # create from normal
        definition = LuxtronikDefinition(self.TEST_DATA, 'Bar', 0)
        field = definition.create_field()
        assert field.name == definition.name
        assert field.writeable == definition.writeable
        assert type(field) is Base

        # create from unknown
        definition = LuxtronikDefinition.unknown(2, 'Foo', 30)
        field = definition.create_field()
        assert field.name == 'unknown_foo_2'
        assert not field.writeable
        assert type(field) is Unknown

        # create from invalid
        definition = LuxtronikDefinition.unknown(-3, '', 10)
        field = definition.create_field()
        assert field is None

    def test_repr(self):
        definition = LuxtronikDefinition.unknown(2, 'Foo', 30)
        text = repr(definition)
        assert text


class TestDefinitionsDict:

    def test_add_get(self):
        def_dict = LuxtronikDefinitionsDictionary()
        assert len(def_dict._index_dict) == 0
        assert len(def_dict._name_dict) == 0

        # add unknown definition
        d1 = LuxtronikDefinition.unknown(1, 'def', 0)
        def_dict.add(d1)
        assert len(def_dict._index_dict) == 1
        assert len(def_dict._name_dict) == 1

        # get via index
        assert 1 in def_dict
        d_out = def_dict.get(1)
        assert d1 == d_out

        # get via name
        assert 'unknown_def_1' in def_dict
        d_out = def_dict['unknown_def_1']
        assert d1 == d_out

        # get non-existing
        assert 2 not in def_dict
        d_out = def_dict.get(2)
        assert d_out is None

        # get via index as string
        assert '1' in def_dict
        d_out = def_dict.get('1')
        assert d1 == d_out

        # add normal definition
        d2 = LuxtronikDefinition({'index': 2, 'names': ['foo', 'bar', '4']}, 'def', 0)
        def_dict.add(d2)
        assert len(def_dict._index_dict) == 2
        assert len(def_dict._name_dict) == 4

        # get via name
        assert 'FOO' in def_dict
        d_out = def_dict.get('FOO')
        assert d2 == d_out

        # get via alternative name
        assert 'Bar' in def_dict
        d_out = def_dict['Bar']
        assert d2 == d_out

        # get non-existing
        assert 'Barf' not in def_dict
        d_out = def_dict['Barf']
        assert d_out is None

        # '4' cannot be found as name
        assert 4 not in def_dict
        d_out = def_dict[4]
        assert d_out is None
        assert '4' not in def_dict
        d_out = def_dict['4']
        assert d_out is None

        # add unknown definition (covers previously added definition)
        d3 = LuxtronikDefinition.unknown(1, 'def', 0)
        def_dict.add(d3)
        assert len(def_dict._index_dict) == 2
        assert len(def_dict._name_dict) == 4

        # get via index
        assert 1 in def_dict
        d_out = def_dict.get(1)
        assert d3 == d_out

        # invalid float
        assert 1.3 not in def_dict
        d_out = def_dict.get(1.3)
        assert d_out is None

        # invalid list
        assert list() not in def_dict
        d_out = def_dict.get(list())
        assert d_out is None

class TestDefinitionsList:

    def_list = [
        {
            Keys.IDX: 5,
            Keys.COUNT: 1,
            Keys.NAMES: ["field_5"],
            Keys.TYPE: Base,
            Keys.WRT: True,
            Keys.VERSION: ">=1.1,<=1.2",
        },
        {
            Keys.IDX: 7,
            Keys.COUNT: 2,
            Keys.NAMES: ["field_7"],
            Keys.TYPE: Base,
            Keys.WRT: True,
            Keys.VERSION: ">=3.1",
        },
        {
            Keys.IDX: 9,
            Keys.COUNT: 1,
            Keys.NAMES: ["field_9a"],
            Keys.TYPE: Base,
            Keys.WRT: True,
            Keys.VERSION: "<=1.3",
        },
        {
            Keys.IDX: 9,
            Keys.COUNT: 2,
            Keys.NAMES: ["field_9"],
            Keys.TYPE: Base,
            Keys.WRT: True,
            Keys.VERSION: "<=3.3",
        },
        {
            Keys.IDX: -1,
            Keys.COUNT: 1,
            Keys.NAMES: ["field_invalid"],
            Keys.TYPE: Base,
            Keys.WRT: True,
            Keys.VERSION: "<=3.3",
        },
    ]

    def test_init(self):
        definitions = LuxtronikDefinitionsList(self.def_list, 'foo', 100, '')

        # only valid
        assert len(definitions) == 4
        assert definitions.name == 'foo'
        assert definitions.offset == 100
        assert definitions._version is VER_IGNORE
        assert 5 in definitions
        assert 'field_9a' in definitions
        assert definitions[7] in definitions

        # correct fields
        assert definitions[5].name == "field_5"
        assert definitions["field_7"].index == 7
        assert definitions.get(9).addr == 109
        assert definitions.get(9).name == "field_9"

    def test_filtered(self):
        definitions = LuxtronikDefinitionsList(self.def_list, 'foo', 100, '')

        filtered1 = LuxtronikDefinitionsList.filtered(definitions, (1, 1, 0, 0))
        assert filtered1.name == 'foo'
        assert filtered1.offset == 100
        assert filtered1._version == (1, 1, 0, 0)
        assert 'field_5' in filtered1            # 1.1 - 1.2
        assert 'field_7' not in filtered1        # 3.1 -
        assert 'field_9a' in filtered1           #     - 1.3
        assert 'field_9' in filtered1            #     - 3.3
        assert 'field_invalid' not in filtered1  # invalid

        filtered1 = LuxtronikDefinitionsList.filtered(definitions, (3, 2, 0, 0))
        assert filtered1._version == (3, 2, 0, 0)
        assert 'field_5' not in filtered1        # 1.1 - 1.2
        assert 'field_7' in filtered1            # 3.1 -
        assert 'field_9a' not in filtered1       #     - 1.3
        assert 'field_9' in filtered1            #     - 3.3
        assert 'field_invalid' not in filtered1  # invalid

    def test_iter(self):
        definitions = LuxtronikDefinitionsList(self.def_list, 'foo', 100, '')

        for index, d in enumerate(definitions):
            if index == 0:
                assert d.index == 5
            if index == 1:
                assert d.index == 7
            if index == 2:
                assert d.index == 9
            if index == 3:
                assert d.index == 9

    def test_create(self):
        definitions = LuxtronikDefinitionsList(self.def_list, 'foo', 100, '')

        # create unknown definition
        definition = definitions.create_unknown_definition(4)
        assert definition.index == 4
        assert definition.count == 1
        assert definition.field_type is Unknown
        assert not definition.writeable
        assert definition.names == ['unknown_foo_4']
        assert definition.valid
        assert definition.type_name == 'foo'
        assert definition.offset == 100
        assert definition.addr == 100 + 4
        vr = VersionRequirements([])
        assert definition.version == vr

    def test_add(self):
        definitions = LuxtronikDefinitionsList(self.def_list, 'foo', 100, '')
        assert len(definitions) == 4

        # add custom definition
        added_1 = definitions.add({
            Keys.IDX: 5,
            Keys.COUNT: 2,
            Keys.NAMES: "baz"
        })
        assert len(definitions) == 5
        assert definitions.get(5) == added_1
        assert definitions.get("baz") == added_1

        # add custom definition (partly covers previously added)
        added_2 = definitions.add({
            Keys.IDX: 10,
            Keys.COUNT: 2,
            Keys.NAMES: "baz"
        })
        assert len(definitions) == 6
        assert definitions.get(5) == added_1
        assert definitions.get("baz") == added_2

        # add invalid definition (not valid)
        added_3 = definitions.add({
            Keys.IDX: -1,
            Keys.COUNT: 2,
            Keys.NAMES: "baz"
        })
        assert added_3 is None

        # add invalid definition (exception)
        added_4 = definitions.add({
            Keys.IDX: "foo",
            Keys.COUNT: 2,
            Keys.NAMES: 1
        })
        assert added_4 is None

    def test_repr(self):
        definitions = LuxtronikDefinitionsList(self.def_list, 'foo', 100, '')
        text = repr(definitions)
        assert text


def test_get_version_definitions():
    def_list = [
        {
            Keys.IDX: 5,
            Keys.TYPE: Base,
        },
        {
            Keys.IDX: 6,
            Keys.TYPE: MajorMinorVersion,
        },
        {
            Keys.IDX: 8,
            Keys.TYPE: Unknown,
        },
        {
            Keys.IDX: 10,
            Keys.TYPE: FullVersion,
            Keys.VERSION: ">1.0"
        },
        {
            Keys.IDX: 40,
            Keys.TYPE: Version,
        },
        {
            Keys.IDX: 41,
            Keys.TYPE: MajorMinorVersion,
        },
    ]

    definitions = LuxtronikDefinitionsList(def_list, 'bar', 100, '')
    got_definitions = get_version_definitions(definitions)
    assert len(got_definitions) == 4
    assert got_definitions[0].index == 10
    assert got_definitions[0].field_type is FullVersion
    assert got_definitions[1].index == 40
    assert got_definitions[1].field_type is Version
    assert got_definitions[2].index == 6
    assert got_definitions[2].field_type is MajorMinorVersion
    assert got_definitions[3].index == 41
    assert got_definitions[3].field_type is MajorMinorVersion

    defs = definitions.get_version_definitions()
    assert got_definitions == defs

    got_definitions = get_version_definitions(definitions, '1.0')
    assert len(got_definitions) == 3
    assert got_definitions[0].index == 40
    assert got_definitions[0].field_type is Version
    assert got_definitions[1].index == 6
    assert got_definitions[1].field_type is MajorMinorVersion
    assert got_definitions[2].index == 41
    assert got_definitions[2].field_type is MajorMinorVersion
