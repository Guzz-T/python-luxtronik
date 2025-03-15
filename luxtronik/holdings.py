"""Parse luxtronik Holdings."""

import logging
from typing import Final

from luxtronik.data_vector import DataVectorModbus, LuxtronikModbusField

from luxtronik.datatypes import (
    ControlMode,
    Kelvin,
    LockMode,
    LpcMode,
    PowerLimit,
    Unknown,
)


HOLDINGS_DEFINITIONS = [
    # [Index, Count, DataType, Writeable, Names]
    [   0, 1, ControlMode,True,  ["Heating_mode"]],
    [   1, 1, Kelvin,     True,  ["Heating_setpoint"]],     # 15 - 75 °C
    [   2, 1, Kelvin,     True,  ["Heating_offset"]],       # 0 - 20 K
    [   5, 1, ControlMode,True,  ["Hot_water_mode"]],
    [   6, 1, Kelvin,     True,  ["Hot_water_setpoint"]],   # 30 - 75 °C
    [   7, 1, Kelvin,     True,  ["Hot_water_offset"]],     # 0 - 20 K
    [  10, 1, ControlMode,True,  ["MK1_heat_mode"]],
    [  11, 1, Kelvin,     True,  ["MK1_heat_setpoint"]],    # 20 - 65 °C
    [  12, 1, Kelvin,     True,  ["MK1_heat_offset"]],      # 0 - 5 K
    [  15, 1, ControlMode,True,  ["MK1_cool_mode"]],
    [  16, 1, Kelvin,     True,  ["MK1_cool_setpoint"]],    # 5 - 25 °C
    [  17, 1, Kelvin,     True,  ["MK1_cool_offset"]],      # 0 - 5 K
    [  20, 1, ControlMode,True,  ["MK2_heat_mode"]],
    [  21, 1, Kelvin,     True,  ["MK2_heat_setpoint"]],    # 20 - 65 °C
    [  22, 1, Kelvin,     True,  ["MK2_heat_offset"]],      # 0 - 5 K
    [  25, 1, ControlMode,True,  ["MK2_cool_mode"]],
    [  26, 1, Kelvin,     True,  ["MK2_cool_setpoint"]],    # 5 - 25 °C
    [  27, 1, Kelvin,     True,  ["MK2_cool_offset"]],      # 0 - 5 K
    [  30, 1, ControlMode,True,  ["MK3_heat_mode"]],
    [  31, 1, Kelvin,     True,  ["MK3_heat_setpoint"]],    # 20 - 65 °C
    [  32, 1, Kelvin,     True,  ["MK3_heat_offset"]],      # 0 - 5 K
    [  35, 1, ControlMode,True,  ["MK3_cool_mode"]],
    [  36, 1, Kelvin,     True,  ["MK3_cool_setpoint"]],    # 5 - 25 °C
    [  37, 1, Kelvin,     True,  ["MK3_cool_offset"]],      # 0 - 5 K
    [  40, 1, LpcMode,    True,  ["LPC_Mode"]],
    [  41, 1, PowerLimit, True,  ["PC_Limit"]],             # 0 - 30 kW
    [  52, 1, LockMode,   True,  ["Lock_Cooling"]],
    [  53, 1, LockMode,   True,  ["Lock_Swimming_pool"]],
]
HOLDINGS_DEFINITIONS: Final = [LuxtronikModbusField(definition) for definition in HOLDINGS_DEFINITIONS]
HOLDINGS_IDX_TO_DEF: Final = {definition.index: definition for definition in HOLDINGS_DEFINITIONS}


class Holdings(DataVectorModbus):
    """Class that holds all Holdings."""

    logger = logging.getLogger("Luxtronik.Holdings")
    name = "Holdings"
    offset = 10000

    @classmethod
    def _get_definitions(cls):
        return HOLDINGS_DEFINITIONS

    @classmethod
    def _get_definition_by_idx(cls, idx):
        return HOLDINGS_IDX_TO_DEF.get(idx, LuxtronikModbusField.invalid())

    def __init__(self, safe=True):
        """Initialize Holdings class."""
        super().__init__()
        self.safe = safe

    def set(self, target, value):
        """Set holding to new value."""
        index, holding = self._lookup(target, with_index=True)
        if index is not None:
            if holding.writeable or not self.safe:
                holding.value = value
            else:
                self.logger.warning("Holding '%s' not safe for writing!", holding.name)
        else:
            self.logger.warning("Holding '%s' not found", target)
