"""Test suite for data_vector module"""

# pylint: disable=too-few-public-methods,invalid-name,too-many-lines

import pytest

from luxtronik.data_vector import DataVector
from luxtronik.datatypes import Base
from luxtronik.definitions import Keys, LuxtronikDefinition


class ObsoleteDataVector(DataVector):

    name = "Obsolete"

    _obsolete = {
        "baz": "foo"
    }

    def __init__(self):
        super().__init__()
        d = LuxtronikDefinition({
            Keys.IDX: 0,
            Keys.TYPE: Base,
            Keys.NAMES: ["foo", "bar"],
        }, "type", 0)
        self._data = {
            d: d.create_field()
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
