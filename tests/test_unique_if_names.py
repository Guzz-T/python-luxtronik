import ast
import inspect
import textwrap

from luxtronik.cfi import LuxtronikData, LuxtronikSocketInterface
from luxtronik.shi import LuxtronikSmartHomeData, LuxtronikSmartHomeInterface

from tests.fake import FakeModbus

# All names listed here are handled correctly in the LuxtronikInterface class.
# Therefore, the implementation in both LuxtronikSocketInterface and LuxtronikSmartHomeInterface
# is permissible, despite multiple derivation with respect to LuxtronikInterface.
# However, these must not be used within the corresponding interfaces,
# as otherwise the wrong function might be called.
# Example:
# def LuxtronikInterface.FuncA(self):
#     return LuxtronikSmartHomeInterface.FuncA(self)
# def LuxtronikInterface.FuncB(self):
#     return LuxtronikSocketInterface.FuncB(self)
# def LuxtronikSmartHomeInterface.FuncB(self):
#     return self.FuncA <- this will call LuxtronikSmartHomeInterface.FuncA via LuxtronikInterface.FuncA
INTF_ALLOWED_DUPLICATED = {'lock', 'info', 'version', 'read_version', 'create_data',
    'determine_version', '_abc_impl', 'read', 'write', 'write_and_read'}
# All names listed here are handled correctly in the LuxtronikData class.
# See above.
DATA_ALLOWED_DUPLICATED = {'empty', 'get_firmware_version'}


class TestUniqueFieldsAndFunctions:
    """Field names and functions must be unique"""

    def test_unique_data_methods_and_functions(self):
        """
        Due to the implementation of LuxtronikAllData() we require
        unique function names
        """
        cfi = LuxtronikData(None)
        shi = LuxtronikSmartHomeData(None)

        attrs_cfi = {name for name in dir(cfi) if not name.startswith("__")}
        attrs_shi = {name for name in dir(shi) if not name.startswith("__")}

        equal_names = (attrs_cfi & attrs_shi) - DATA_ALLOWED_DUPLICATED

        assert not equal_names, (
            f"The CFI- and SHI-Data contain both the following ambiguous methods or fields: {equal_names}"
        )

    def test_unique_interface_methods_and_functions(self):
        """
        Due to the implementation of LuxtronikInterface() we require
        unique function names
        """
        cfi = LuxtronikSocketInterface('host')
        modbus = FakeModbus('host')
        shi = LuxtronikSmartHomeInterface(modbus)

        attrs_cfi = {name for name in dir(cfi) if not name.startswith("__")}
        attrs_shi = {name for name in dir(shi) if not name.startswith("__")}

        equal_names = (attrs_cfi & attrs_shi) - INTF_ALLOWED_DUPLICATED

        assert not equal_names, (
            f"The CFI- and SHI-Interface contain both the following ambiguous methods or fields: {equal_names}"
        )



class TestNoNonUniqueCall:
    """Do not use functions that are not unique inside the class."""

    def check_no_non_unique_calls(self, class_to_check, names_to_check):
        # Get class source code and normalize indentation
        source = textwrap.dedent(inspect.getsource(class_to_check))
        tree = ast.parse(source)

        violations = []
        # All names listed here are handled correctly in the LuxtronikData class

        # Iterate over all methods (sync and async) in the class
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_name = node.name
                for child in ast.walk(node):
                    # Check for pattern: self.<name>
                    if (
                        isinstance(child, ast.Attribute)
                        and isinstance(child.value, ast.Name)
                        and child.value.id == "self"
                    ):
                        target_name = child.attr
                        if target_name in names_to_check:
                            violations.append(
                                f"In '{method_name}' (line {child.lineno}): called self.{target_name}()"
                            )
        assert violations == [], "Disallowed internal calls found:\n" + "\n".join(violations)


    def test_cfi_data_no_non_unique_calls(self):
        self.check_no_non_unique_calls(LuxtronikData, DATA_ALLOWED_DUPLICATED)

    def test_shi_data_no_non_unique_calls(self):
        self.check_no_non_unique_calls(LuxtronikSmartHomeData, DATA_ALLOWED_DUPLICATED)

    def test_cfi_if_no_non_unique_calls(self):
        self.check_no_non_unique_calls(LuxtronikSocketInterface, INTF_ALLOWED_DUPLICATED)

    def test_shi_if_no_non_unique_calls(self):
        self.check_no_non_unique_calls(LuxtronikSmartHomeInterface, INTF_ALLOWED_DUPLICATED)
