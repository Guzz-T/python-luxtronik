from luxtronik import LuxtronikSocketInterface, Calculations


class FakeSocketInterface(LuxtronikSocketInterface):

    write_counter = 0
    read_counter = 0

    @classmethod
    def reset(cls):
        FakeSocketInterface.write_counter = 0
        FakeSocketInterface.read_counter = 0

    def read(self, data):
        FakeSocketInterface.read_parameters(self, data.parameters)
        FakeSocketInterface.read_visibilities(self, data.visibilities)
        FakeSocketInterface.read_calculations(self, data.calculations)

    def read_parameters(self, parameters=None):
        parameters.get(0).raw = 2
        FakeSocketInterface.read_counter += 1

    def read_visibilities(self, visibilities):
        visibilities.get(0).raw = 4
        FakeSocketInterface.read_counter += 1

    def read_calculations(self, calculations=None):
        if calculations is None:
            calculations = Calculations()
        calculations.get(0).raw = 6
        FakeSocketInterface.read_counter += 1
        return calculations

    def write(self, data):
        FakeSocketInterface.write_counter += 1
