import pytest
from test_definitions import RunTestDefinitions

from luxtronik.definitions.holdings import HOLDINGS_DEFINITIONS

###############################################################################
# Tests
###############################################################################

class TestHoldingsDefinitions(RunTestDefinitions):

    definitions = HOLDINGS_DEFINITIONS
