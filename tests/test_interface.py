from luxtronik.cfi import LuxtronikSocketInterface
from luxtronik.shi import LuxtronikSmartHomeInterface

class TestInterface:

    def test_unique_methods_and_functions(self):
        """
        Due to the implementation of LuxtronikInterface() we require
        unique function names
        """
        cfi = LuxtronikSocketInterface('host')
        shi = LuxtronikSmartHomeInterface(None)

        accepted_equal_names = {'read', 'write', 'write_and_read', 'version', 'determine_version', 'read_version'}

        attrs_cfi = {name for name in dir(cfi) if not name.startswith("__")}
        attrs_shi = {name for name in dir(shi) if not name.startswith("__")}

        equal_names = (attrs_cfi & attrs_shi) - accepted_equal_names

        assert not equal_names, (
            f"The CFI- and SHI-Interface contain both the following ambiguous methods or fields: {equal_names}"
        )
