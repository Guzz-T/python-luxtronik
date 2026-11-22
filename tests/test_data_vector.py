"""Test suite for data_vector module"""

# pylint: disable=too-few-public-methods,invalid-name,too-many-lines

import pytest

from luxtronik.data_vector import DataVector
from luxtronik.datatypes import Base
from luxtronik.definitions import Keys, LuxtronikDefinitionsList


def_list = [
    {
        Keys.IDX: 0,
        Keys.TYPE: Base,
        Keys.NAMES: ["foo", "bar"],
    }
]
TEST_DEFINITIONS = LuxtronikDefinitionsList(def_list, 'foo', 100, 'INT32')


class ObsoleteDataVector(DataVector):

    name = "Obsolete"
    definitions = TEST_DEFINITIONS

    _obsolete = {
        "baz": "foo"
    }


class TestDataVector:
    """Test suite for DataVector"""

    @pytest.mark.parametrize("name, exception_expected", [
        ("foo", False),
        ("bar", False),
        ("baz", True),
        ("qux", False),
    ])
    def test_obsolete(self, name, exception_expected):
        """Test cases for initialization"""
        obsolete = ObsoleteDataVector()
        try:
            obsolete.get(name)
            assert not exception_expected
        except KeyError:
            assert exception_expected
