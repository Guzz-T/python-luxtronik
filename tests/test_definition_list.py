import re

from luxtronik.version import parse_version, parse_version_requirement
from luxtronik.datatypes import Base
from luxtronik.definitions import Keys, LuxtronikDefinition
from luxtronik.definitions.calculations import CALCULATIONS_DEFINITIONS_LIST
from luxtronik.definitions.holdings import HOLDINGS_DEFINITIONS_LIST
from luxtronik.definitions.inputs import INPUTS_DEFINITIONS_LIST
from luxtronik.definitions.parameters import PARAMETERS_DEFINITIONS_LIST
from luxtronik.definitions.visibilities import VISIBILITIES_DEFINITIONS_LIST
from types_of_same_kind import TypesOfSameKind


class RunTestDefinitionList:

    # override this
    definitions = None

    # use True for SHI and false for CFI
    do_lower_case_test = True

    def get_names(self, definition):
        names = definition.get(Keys.NAMES, [])
        if isinstance(names, str):
            names = [names]
        return names

    def test_structure(self):
        for definition in self.definitions:

            # index
            assert Keys.IDX in definition, \
                f"{Keys.IDX} not defined: {definition}"
            assert isinstance(definition[Keys.IDX], int), \
                f"{Keys.IDX} must be of type 'int': {definition}"

            # count
            if Keys.COUNT in definition:
                assert isinstance(definition[Keys.COUNT], int), \
                    f"{Keys.COUNT} must be of type 'int': {definition}"

            # names
            if Keys.NAMES in definition:
                assert isinstance(definition[Keys.NAMES], list) \
                        or isinstance(definition[Keys.NAMES], str), \
                    f"{Keys.NAMES} must be of type 'list' or 'str': {definition}"
                if isinstance(definition[Keys.NAMES], list):
                    for name in definition[Keys.NAMES]:
                        assert isinstance(name, str), f"Entry of {Keys.NAMES} " \
                            f"must be of type 'int': {definition}"

            # successor
            if Keys.SUCCESSOR in definition:
                if definition[Keys.SUCCESSOR] is not None:
                    assert isinstance(definition[Keys.SUCCESSOR], str), \
                        f"{Keys.SUCCESSOR} must be of type 'str': {definition}"

            # field_type
            if Keys.TYPE in definition:
                assert issubclass(definition[Keys.TYPE], Base), \
                    f"{Keys.TYPE} must be inherit from 'Base': {definition}"

            # writeable
            if Keys.WRT in definition:
                assert isinstance(definition[Keys.WRT], bool), \
                    f"{Keys.WRT} must be of type 'bool': {definition}"

            # data type
            if Keys.DATATYPE in definition:
                assert isinstance(definition[Keys.DATATYPE], str), \
                    f"{Keys.DATATYPE} must be of type 'str': {definition}"

            # unit
            if Keys.UNIT in definition:
                assert isinstance(definition[Keys.UNIT], str), \
                    f"{Keys.UNIT} must be of type 'str': {definition}"

            # default (raw value)
            if Keys.DEFAULT in definition:
                assert isinstance(definition[Keys.DEFAULT], int), \
                    f"{Keys.DEFAULT} must be of type 'int': {definition}"

            # range (raw value)
            if Keys.RANGE in definition:
                assert isinstance(definition[Keys.RANGE], dict), \
                    f"{Keys.RANGE} must be of type 'dict': {definition}"

            # range - min (raw value)
            if Keys.RANGE in definition and Keys.MIN in definition[Keys.RANGE]:
                assert isinstance(definition[Keys.RANGE][Keys.MIN], int), \
                    f"{Keys.MIN} must be of type 'int': {definition}"

            # range - max (raw value)
            if Keys.RANGE in definition and Keys.MAX in definition[Keys.RANGE]:
                assert isinstance(definition[Keys.RANGE][Keys.MAX], int), \
                    f"{Keys.MAX} must be of type 'int': {definition}"

            # since
            if Keys.SINCE in definition:
                assert isinstance(definition[Keys.SINCE], str), \
                    f"{Keys.SINCE} must be of type 'str': {definition}"

            # until
            if Keys.UNTIL in definition:
                assert isinstance(definition[Keys.UNTIL], str), \
                    f"{Keys.UNTIL} must be of type 'str': {definition}"

            # version
            if Keys.VERSION in definition:
                assert isinstance(definition[Keys.VERSION], str), \
                    f"{Keys.VERSION} must be of type 'str': {definition}"

            # description
            if Keys.DESC in definition:
                assert isinstance(definition[Keys.DESC], str), \
                    f"{Keys.DESC} must be of type 'str': {definition}"

    def test_index(self):
        for definition in self.definitions:
            idx = definition.get(Keys.IDX, 0)
            assert idx >= 0, \
            f"The index must be greater or equal than zero: {definition}"

    def test_index_ascending(self):
        prev = self.definitions[0]

        for definition in self.definitions:
            prev_idx = prev.get(Keys.IDX, -1)
            this_idx = definition.get(Keys.IDX, 0)
            assert prev_idx <= this_idx, \
                "The definitions must be arranged in ascending order. " \
                "This allows us to avoid sorting them afterwards." \
                f"this  = {definition}" \
                f"other = {prev}"
            prev = definition

    def test_count(self):
        for definition in self.definitions:
            count = definition.get(Keys.COUNT, 1)
            assert count > 0, \
                f"Count field must be greater than zero: {definition}"

    def test_name_valid(self):
        for definition in self.definitions:
            names = self.get_names(definition)
            for name in names:
                sanitized = re.sub(r"[^a-z0-9_]", "", name)
                assert not self.do_lower_case_test or sanitized == name, \
                    f"The name may only contain a-z0-9_ {definition}"
                assert sanitized != "", \
                    f"Name must not be empty. {definition}"
                try:
                    int(name)
                    assert False, "Name must not be a number."
                except Exception:
                    pass

    def do_unique_self_check(self, definition):
        names = self.get_names(definition)
        length = len(names)
        for i in range(length):
            name_i = names[i]
            for j in range(i + 1, length):
                name_j = names[j]
                assert (name_i != name_j), \
                    "All names of the same definition must be unique. " \
                    f"definition  = {definition}"

    def do_unique_compare_check(self, def_a, def_b):
        names_a = self.get_names(def_a)
        index_a = def_a.get(Keys.IDX, -1)
        type_a = def_a.get(Keys.TYPE, Base)
        names_b = self.get_names(def_b)
        index_b = def_a.get(Keys.IDX, -2)
        type_b = def_b.get(Keys.TYPE, Base)

        # We allow duplicate names at the same index
        duplicated_allowed = (index_a == index_b) and TypesOfSameKind.match(type_a, type_b)

        for name_a in names_a:
            for name_b in names_b:
                assert (name_a != name_b) or duplicated_allowed, \
                    "All names of the same definition type must be unique " \
                    "(except for the same index). " \
                    f"this  = {def_a}" \
                    f"other = {def_b}"
        return True

    def test_name_unique(self):
        length = len(self.definitions)

        for i in range(length):
            def_i = self.definitions[i]
            self.do_unique_self_check(def_i)
            for j in range(i + 1, length):
                def_j = self.definitions[j]
                self.do_unique_compare_check(def_i, def_j)

    def test_field_type(self):
        for definition in self.definitions:
            field_type = definition.get(Keys.TYPE, None)
            assert issubclass(field_type, Base), \
                f"Type must be set: {definition}"

    def test_data_type(self):
        for definition in self.definitions:
            if Keys.DATATYPE in definition:
                data_type = definition[Keys.DATATYPE]
                assert data_type in LuxtronikDefinition.VALID_DATA_TYPES, \
                    f"Datatype must be set correctly: {definition}"

    def test_since(self):
        for definition in self.definitions:
            if Keys.SINCE in definition:
                since = definition[Keys.SINCE]
                parsed = parse_version(since)
                assert parsed is not None, \
                    f"Since must be a valid version instead of {since}: {definition}"

    def test_until(self):
        for definition in self.definitions:
            if Keys.UNTIL in definition:
                until = definition[Keys.UNTIL]
                parsed = parse_version(until)
                assert parsed is not None, \
                    f"Until must be a valid version instead of {until}: {definition}"

    def test_version(self):
        for definition in self.definitions:
            if Keys.VERSION in definition:
                version = definition[Keys.VERSION]
                parsed = parse_version_requirement(version)
                assert parsed is not None, \
                    f"Version must be a valid version requirement instead of {version}: {definition}"

    def test_successor(self):
        for definition in self.definitions:
            if Keys.SUCCESSOR in definition:
                successor = definition[Keys.SUCCESSOR]
                found = False
                for d in self.definitions:
                    if definition is not d and Keys.NAMES in d:
                        found |= (d[Keys.NAMES][0].lower() == successor.lower())
                assert found, \
                    f"The successor {successor} must be defined correctly as the preferred name of another field: {definition}"

###############################################################################
# Tests
###############################################################################

class TestCalculationsDefinitionList(RunTestDefinitionList):

    definitions = CALCULATIONS_DEFINITIONS_LIST
    do_lower_case_test = False


class TestHoldingsDefinitionList(RunTestDefinitionList):

    definitions = HOLDINGS_DEFINITIONS_LIST
    do_lower_case_test = True


class TestInputsDefinitionList(RunTestDefinitionList):

    definitions = INPUTS_DEFINITIONS_LIST
    do_lower_case_test = True


class TestParametersDefinitionList(RunTestDefinitionList):

    definitions = PARAMETERS_DEFINITIONS_LIST
    do_lower_case_test = False


class TestVisibilitiesDefinitionList(RunTestDefinitionList):

    definitions = VISIBILITIES_DEFINITIONS_LIST
    do_lower_case_test = False
