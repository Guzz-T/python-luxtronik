import pytest

from luxtronik.version import (
    parse_version,
    parse_version_requirement,
    version_fulfill_requirement,
    version_in_range,
    get_version_str,
    get_op_func_str,
    get_since_requirement_str,
    get_until_requirement_str,
    VersionRequirement,
    VersionRequirements,
    resolve_version_input,
    VER_IGNORE,
    VER_NONE,
)
from luxtronik.constants import (
    LUXTRONIK_VERSION_DETECT,
    LUXTRONIK_VERSION_LATEST,
    LUXTRONIK_VERSION_IGNORE,
    LUXTRONIK_LATEST_VERSION,
)
import operator

###############################################################################
# Tests
###############################################################################

class TestVersion:

    @pytest.mark.parametrize(
        "string, version",
        [
            ("1",           (1, 0, 0, 0)),
            ("2.1",         (2, 1, 0, 0)),
            ("3.2.1",       (3, 2, 1, 0)),
            ("1.2.3.4",     (1, 2, 3, 4)),
            ("1.2.3.4.5",   (1, 2, 3, 4)),
            ("a.b",         None),
            ("hello",       None),
            ("foo.bar",     None),
            ("1_2",         None),
            ("3 4",         None),
            (None,          None),
            ((1, 0, 0, 4),  (1, 0, 0, 4)),
            ((2, 1, 3),     (2, 1, 3, 0)),
            ((3, 2),        (3, 2, 0, 0)),
            ((5,),          (5, 0, 0, 0)),
            ((),            (0, 0, 0, 0)),
            ((3, "foo", 2), None),
        ]
    )
    def test_parse(self, string, version):
        parsed = parse_version(string)
        assert parsed == version

    @pytest.mark.parametrize(
        "string, op, version",
        [
            ("!=1",          operator.ne, (1, 0, 0, 0)),
            (">=2.1",        operator.ge, (2, 1, 0, 0)),
            ("<3.2.1",       operator.lt, (3, 2, 1, 0)),
            ("<=  1.2.3.4",  operator.le, (1, 2, 3, 4)),
            ("== 1.2.3.4.5", operator.eq, (1, 2, 3, 4)),
            ("< a.b",        operator.lt, None),
            ("> hello",      operator.gt, None),
            ("xx foo.bar",   None,        None),
            ("!= 1_2",       operator.ne, None),
            ("==3 4",        operator.eq, None),
            (None,           None,        None),
            (2,              None,        None),
            ((1, 0, 0, 4),   None,        None),
        ]
    )
    def test_parse_requirement(self, string, op, version):
        parsed_op, parsed_ver = parse_version_requirement(string)
        assert parsed_op == op
        assert parsed_ver == version

    @pytest.mark.parametrize(
        "version, op, requirement, fulfilled",
        [
            (None,   None,        None,    True),
            ((1, 2), None,        (2, 1),  True),
            ((1, 2), operator.eq, None,    True),
            (None,   operator.eq, (2, 1),  True),
            ((2, 4), operator.gt, (1, 3),  True),
            ((2, 4), operator.gt, (2, 4),  False),
            ((2, 4), operator.lt, (1, 3),  False),
            ((2, 4), operator.lt, (2, 5),  True),
            ((2, 4), operator.le, (1, 3),  False),
            ((2, 4), operator.le, (2, 4),  True),
            ((2, 4), operator.ge, (3, 3),  False),
            ((2, 4), operator.ge, (2, 4),  True),
            ((2, 4), operator.eq, (3, 3),  False),
            ((2, 4), operator.eq, (2, 4),  True),
            ((2, 4), operator.ne, (3, 3),  True),
            ((2, 4), operator.ne, (2, 4),  False),
        ]
    )
    def test_fulfill_requirements(self, version, op, requirement, fulfilled):
        result = version_fulfill_requirement(version, op, requirement)
        assert result == fulfilled

    @pytest.mark.parametrize(
        "version, since, until, in_range",
        [
            (None,   None,   None,         True),
            ((1, 2), None,   None,         True),
            (None,   (5, 4), (2, 1),       True),
            ((2, 4), (1, 3), None,         True),
            ((2, 4), (5, 1), None,         False),
            ((2, 4), None,   (2, 3, 9),    False),
            ((2, 4), None,   (2, 4, 0, 1), True),
            ((5, 6), (5, 6), (5, 6),       True),
            ((5, 6), (5, 7), (5, 6),       False),
            ((5, 6), (5, 6), (5, 5),       False),
            ((3, 7), (2, 8), (4, 6),       True),
        ]
    )
    def test_in_range(self, version, since, until, in_range):
        result = version_in_range(version, since, until)
        assert result == in_range

    @pytest.mark.parametrize(
        "version, result",
        [
            ((1, 2),       '1.2'),
            ((2, 4, 1),    '2.4.1'),
            ((5, 1, 2, 2), '5.1.2.2'),
            (VER_NONE,     'VER_NONE'),
            (VER_IGNORE,   'VER_IGNORE'),
        ]
    )
    def test_version_str(self, version, result):
        output = get_version_str(version)
        assert result == output

    @pytest.mark.parametrize(
        "op, result",
        [
            (operator.le, '<= '),
            (operator.ne, '!= '),
            (operator.gt, '> '),
        ]
    )
    def test_op_str(self, op, result):
        output = get_op_func_str(op)
        assert result == output

    @pytest.mark.parametrize(
        "since, result",
        [
            ('1.0', '>= 1.0'),
            ('2',   '>= 2'),
        ]
    )
    def test_since_str(self, since, result):
        output = get_since_requirement_str(since)
        assert result == output

    @pytest.mark.parametrize(
        "since, result",
        [
            ('1.0', '<= 1.0'),
            ('2',   '<= 2'),
        ]
    )
    def test_until_str(self, since, result):
        output = get_until_requirement_str(since)
        assert result == output


class TestVersionRequirement:

    def test_create(self):
        vr = VersionRequirement(operator.ne, (1, 6))
        assert vr.op_func == operator.ne
        assert vr.version_requirement == (1,6)

    @pytest.mark.parametrize(
        "req, op, version",
        [
            (None,    None,        None),
            ('<=1.9', operator.le, (1, 9, 0, 0)),
            ('!= 2',  operator.ne, (2, 0, 0, 0)),
        ]
    )
    def test_from_string(self, req, op, version):
        vr = VersionRequirement.from_string(req)
        assert vr.op_func == op
        assert vr.version_requirement == version

    def test_matches(self):
        vr = VersionRequirement.from_string('>  4.1')
        assert not vr.matches((4, 1))
        assert vr.matches((4, 2))
        assert vr.matches((5, 0))
        assert vr.matches((5, 0, 0, 1))

    def test_str(self):
        vr = VersionRequirement.from_string('<=5.0')
        assert str(vr) == '<= 5.0.0.0'

    def test_repr(self):
        vr = VersionRequirement.from_string(' < 4.9 ')
        assert vr.__repr__() == '< 4.9.0.0'

    def test_eq(self):
        vr_a = VersionRequirement.from_string('<4.9')
        vr_b = VersionRequirement(operator.lt, (4, 9, 0, 0))
        assert vr_a == vr_b
        vr_b = VersionRequirement(operator.lt, (4, 9, 0, 1))
        assert vr_a != vr_b
        vr_b = VersionRequirement(operator.eq, (4, 9, 0, 0))
        assert vr_a != vr_b


class TestVersionRequirements:

    def test_create(self):
        vr = VersionRequirements([VersionRequirement(operator.ne, (1, 6))])
        assert vr.requirements[0].op_func == operator.ne
        assert vr.requirements[0].version_requirement == (1,6)

    @pytest.mark.parametrize(
        "req, idx, op, version",
        [
            (None,             None, None,        None),
            ('<=1.9, > 1.7.1', 0,    operator.le, (1, 9, 0, 0)),
            ('<=1.9, > 1.7.1', 1,    operator.gt, (1, 7, 1, 0)),
        ]
    )
    def test_from_list(self, req, idx, op, version):
        vr = VersionRequirements.from_list(req)
        if idx is not None:
            assert vr.requirements[idx].op_func == op
            assert vr.requirements[idx].version_requirement == version
        else:
            assert len(vr.requirements) == 0

    def test_matches(self):
        vr = VersionRequirements.from_list('>4.1,<=5.0')
        assert not vr.matches((4, 1))
        assert vr.matches((4, 2))
        assert vr.matches((4, 999999999))
        assert vr.matches((5, 0))
        assert not vr.matches((5, 0, 0, 1))

    def test_str(self):
        vr = VersionRequirements.from_list('>4.1,<= 5.0')
        assert str(vr) == '> 4.1.0.0;<= 5.0.0.0'

    def test_repr(self):
        vr = VersionRequirements.from_list('<4.9, >= 2.0')
        assert vr.__repr__() == '< 4.9.0.0;>= 2.0.0.0'

    def test_eq(self):
        vr_a = VersionRequirements.from_list('<4.9, >= 2.0')
        vr_b = VersionRequirements([
            VersionRequirement(operator.lt, (4, 9, 0, 0)),
            VersionRequirement(operator.ge, (2, 0, 0, 0)),
        ])
        assert vr_a == vr_b
        vr_b = VersionRequirements([
            VersionRequirement(operator.lt, (4, 9, 0, 0)),
            VersionRequirement(operator.gt, (2, 0, 0, 0)),
        ])
        assert vr_a != vr_b
        vr_b = VersionRequirements([
            VersionRequirement(operator.lt, (3, 9, 0, 0)),
            VersionRequirement(operator.ge, (2, 0, 0, 0)),
        ])
        assert vr_a != vr_b



class TestResolve:

    @pytest.mark.parametrize(
        "input, version, flag",
        [
            ((1, 3, 4),                (1, 3, 4, 0),             False),
            ("5.3.1",                  (5, 3, 1, 0),             False),
            (LUXTRONIK_LATEST_VERSION, LUXTRONIK_LATEST_VERSION, False),
            (LUXTRONIK_VERSION_DETECT, VER_NONE,                 True),
            (LUXTRONIK_VERSION_LATEST, LUXTRONIK_LATEST_VERSION, False),
            (LUXTRONIK_VERSION_IGNORE, VER_IGNORE,               False),
            (None,                     VER_IGNORE,               False),
            ("x.y",                    VER_IGNORE,               False),
            (2,                        VER_IGNORE,               False),
        ])
    def test_resolve_version_input(self, input, version, flag):
        v, f = resolve_version_input(input)
        assert v == version
        assert f == flag
