from luxtronik import LuxtronikAllData, Luxtronik


class FakeLuxtronik(Luxtronik):

    def __init__(self):
        LuxtronikAllData.__init__(self)
        for definition, field in self.parameters.items():
            field.raw = definition.idx
        for definition, field in self.calculations.items():
            field.raw = definition.idx
        for definition, field in self.visibilities.items():
            field.raw = definition.idx