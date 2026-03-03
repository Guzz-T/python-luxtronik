
from luxtronik import (
    LuxtronikSettings,
    Parameters,
    Calculations,
    Visibilities,
    LuxtronikSocketInterface,
)


class TestLuxtronikSocketInterface:

    def test_parse(self):
        lux = LuxtronikSocketInterface('host')
        parameters = Parameters()
        calculations = Calculations()
        visibilities = Visibilities()

        n = 2000
        t = list(range(0, n + 1))

        parameters[0].write_pending = True
        lux._parse(parameters, t)
        p = parameters.get(n)
        assert p.name == f"unknown_parameter_{n}"
        assert p.raw == n
        assert not p.write_pending

        calculations[0].write_pending = True
        lux._parse(calculations, t)
        c = calculations.get(n)
        assert c.name == f"unknown_calculation_{n}"
        assert c.raw == n
        assert not c.write_pending

        visibilities[0].write_pending = True
        lux._parse(visibilities, t)
        v = visibilities.get(n)
        assert v.name == f"unknown_visibility_{n}"
        assert v.raw == n
        assert not v.write_pending

        n = 10
        t = list(range(0, n + 1))

        orig_preserve = LuxtronikSettings.preserve_last_read_value_on_fail

        LuxtronikSettings.preserve_last_read_value_on_fail = True
        preserve = LuxtronikSettings.preserve_last_read_value_on_fail
        for definition, field in parameters.data.items():
            field.write_pending = True
        lux._parse(parameters, t)
        for definition, field in parameters.data.items():
            value_available = definition.index > n
            if value_available and not preserve:
                assert field.raw is None
            assert field.write_pending == (value_available and preserve)

        LuxtronikSettings.preserve_last_read_value_on_fail = False
        preserve = LuxtronikSettings.preserve_last_read_value_on_fail
        for definition, field in calculations.data.items():
            field.write_pending = True
        lux._parse(calculations, t)
        for definition, field in calculations.data.items():
            value_available = definition.index > n
            if value_available and not preserve:
                assert field.raw is None
            assert field.write_pending == (value_available and preserve)

        LuxtronikSettings.preserve_last_read_value_on_fail = False
        preserve = LuxtronikSettings.preserve_last_read_value_on_fail
        for definition, field in visibilities.data.items():
            field.write_pending = True
        lux._parse(visibilities, t)
        for definition, field in visibilities.data.items():
            value_available = definition.index > n
            if value_available and not preserve:
                assert field.raw is None
            assert field.write_pending == (value_available and preserve)

        LuxtronikSettings.preserve_last_read_value_on_fail = orig_preserve