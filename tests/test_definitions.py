import pytest

from luxtronik.definitions.holdings import HOLDINGS_DEFINITIONS
from luxtronik.definitions.inputs import INPUTS_DEFINITIONS


class RunTestDefinitions:

    # override this
    definitions = None

    def test_index_ascending(self):
        idx = self.definitions[0].index

        for definition in self.definitions:
            assert idx <= definition.index, f"""
                The definitions must be arranged in ascending order.
                This allows us to avoid sorting them afterwards.
            """
            idx = definition.index

    def test_name_unique(self):
        length = len(self.definitions)

        for i in range(length):
            for j in range(i + 1, length):
                for i_name in self.definitions[i].names:
                    for j_name in self.definitions[j].names:
                        assert i_name.lower() != j_name.lower(), """
                            All names of the same type must be unique.
                            index i = {self.definitions[i].index}
                            index j = {self.definitions[j].index}
                        """

###############################################################################
# Tests
###############################################################################

class TestHoldingsDefinitions(RunTestDefinitions):

    definitions = HOLDINGS_DEFINITIONS


class TestInputsDefinitions(RunTestDefinitions):

    definitions = INPUTS_DEFINITIONS