
from luxtronik.definitions.keys import Keys


class TestKeys():

    def test_fully_filled(self):
        print("test")
        for key in Keys:
            assert isinstance(key.key_value, str)
            assert key.key_value != ""
            assert key.value == key.key_value
            assert isinstance(key.requirement, str)
            assert key.requirement != ""
            assert hasattr(key, "default_value")
            assert isinstance(key.description, str)
            assert key.description != ""

    def test_str(self):
        assert Keys.IDX == "index"
