
from luxtronik import (
  Parameters,
  Calculations,
  Visibilities,
  LuxtronikData,
  LuxtronikSocketInterface,
)
from luxtronik.version import VER_IGNORE

class TestLuxtronikConfigData:

    def test_init(self):
        data1 = LuxtronikData()
        assert data1.parameters is not None
        assert data1.parameters.version == VER_IGNORE
        assert data1.parameters.safe
        assert data1.calculations is not None
        assert data1.calculations.version == VER_IGNORE
        assert data1.calculations.safe
        assert data1.visibilities is not None
        assert data1.visibilities.version == VER_IGNORE
        assert data1.visibilities.safe

        data2 = LuxtronikData(data1.parameters)
        assert data2.parameters is data1.parameters
        assert data2.calculations is not data1.calculations
        assert data2.visibilities is not data1.visibilities

    def test_empty(self):
        data = LuxtronikData.empty((1, 2, 0, 0), False)
        assert data.parameters is not None
        assert not data.parameters.safe
        assert data.parameters.version == (1, 2, 0, 0)
        assert data.calculations is not None
        assert data.calculations.safe
        assert data.calculations.version == (1, 2, 0, 0)
        assert data.visibilities is not None
        assert data.visibilities.safe
        assert data.visibilities.version == (1, 2, 0, 0)

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

        parameters[0].write_pending = True
        parameters[20].write_pending = True
        parameters[40].write_pending = True
        lux._parse(parameters, t)
        for definition, field in parameters.data.items():
            #if definition.index > n:
            #    assert field.raw is None # no update
            assert not field.write_pending

        calculations[0].write_pending = True
        calculations[20].write_pending = True
        calculations[40].write_pending = True
        lux._parse(calculations, t)
        for definition, field in calculations.data.items():
            #if definition.index > n:
            #    assert field.raw is None # no update
            assert not field.write_pending

        visibilities[0].write_pending = True
        visibilities[20].write_pending = True
        visibilities[40].write_pending = True
        lux._parse(visibilities, t)
        for definition, field in visibilities.data.items():
            #if definition.index > n:
            #    assert field.raw is None # no update
            assert not field.write_pending
