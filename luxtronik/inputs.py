"""Parse luxtronik Inputs."""

import logging
from typing import Final

from luxtronik.data_vector import DataVectorModbus, LuxtronikModbusField

from luxtronik.datatypes import (
    FullVersion,
    Kelvin,
    Power,
    OperationMode,
    Unknown,
)


INPUTS_DEFINITIONS = [
    # [Index, Count, DataType, Writeable, Names]
    [   0, 1, Unknown,       False, ["Unknown_Inputs_0"]], # 1 if heatpump runs (either heat or hot_water) else 0 -> Compressor?
    [   2, 1, OperationMode, False, ["Operation_mode"]],
    [   3, 1, Unknown,       False, ["Unknown_Inputs_3"]], # Heat request. 1 -> no request, 2 -> heat request from master / heat requested, 3 -> heat request at slave / heat running
    [   4, 1, Unknown,       False, ["Unknown_Inputs_4"]], # Hot_water request. 0 -> disabled, 1 -> no request, 3 -> hot_water request at slave / hot_water running
    [   6, 1, Unknown,       False, ["Unknown_Inputs_6"]],
    [   7, 1, Unknown,       False, ["Unknown_Inputs_7"]],
    [ 100, 1, Kelvin,        False, ["TRL"]],
    [ 101, 1, Kelvin,        False, ["TRL_target"]],
    [ 102, 1, Kelvin,        False, ["TRL_ext"]],
    [ 103, 1, Kelvin,        False, ["TRL_limit"]],
    [ 104, 1, Kelvin,        False, ["TRL_min_target"]],
    [ 105, 1, Kelvin,        False, ["TVL"]],
    [ 106, 1, Unknown,       False, ["Unknown_Inputs_106"]],
    [ 107, 1, Kelvin,        False, ["Inside_temp"]],
    [ 108, 1, Kelvin,        False, ["Outside_temp"]],
    [ 120, 1, Kelvin,        False, ["Hot_water_temp"]],
    [ 121, 1, Kelvin,        False, ["Hot_water_target"]],
    [ 122, 1, Kelvin,        False, ["Hot_water_min"]],
    [ 123, 1, Kelvin,        False, ["Hot_water_max"]],
    [ 124, 1, Unknown,       False, ["Unknown_Inputs_124"]], # hot_water idle -> 405, hot_water running -> 525
    [ 140, 1, Kelvin,        False, ["MK1_heat_temp"]],
    [ 141, 1, Kelvin,        False, ["MK1_heat_target"]],
    [ 142, 1, Unknown,       False, ["Unknown_Inputs_142"]], # MK1_cool_temp?
    [ 143, 1, Unknown,       False, ["Unknown_Inputs_143"]], # MK1_cool_target?
    [ 150, 1, Kelvin,        False, ["MK2_heat_temp"]],
    [ 151, 1, Kelvin,        False, ["MK2_heat_target"]],
    [ 152, 1, Unknown,       False, ["Unknown_Inputs_152"]], # MK2_cool_temp?
    [ 153, 1, Unknown,       False, ["Unknown_Inputs_153"]], # MK2_cool_target?
    [ 160, 1, Kelvin,        False, ["MK3_heat_temp"]],
    [ 161, 1, Kelvin,        False, ["MK3_heat_target"]],
    [ 162, 1, Unknown,       False, ["Unknown_Inputs_162"]], # MK3_cool_temp?
    [ 163, 1, Unknown,       False, ["Unknown_Inputs_163"]], # MK3_cool_target?
    [ 201, 1, Unknown,       False, ["Unknown_Inputs_201"]],
    [ 202, 1, Unknown,       False, ["Unknown_Inputs_202"]],
    [ 203, 1, Unknown,       False, ["Unknown_Inputs_203"]],
    [ 204, 1, Unknown,       False, ["Unknown_Inputs_204"]],
    [ 205, 1, Unknown,       False, ["Unknown_Inputs_205"]],
    [ 206, 1, Unknown,       False, ["Unknown_Inputs_206"]],
    [ 207, 1, Unknown,       False, ["Unknown_Inputs_207"]],
    [ 300, 1, Unknown,       False, ["Unknown_Inputs_300"]],
    [ 301, 1, Unknown,       False, ["Unknown_Inputs_301"]],
    [ 302, 1, Unknown,       False, ["Unknown_Inputs_302"]],
    [ 310, 1, Unknown,       False, ["Unknown_Inputs_310"]],
    [ 311, 1, Energy,        False, ["Total_power_consumption"]],
    [ 312, 1, Unknown,       False, ["Unknown_Inputs_312"]],
    [ 313, 1, Energy,        False, ["Heat_power_consumption"]],
    [ 314, 1, Unknown,       False, ["Unknown_Inputs_314"]],
    [ 315, 1, Energy,        False, ["Hot_water_power_consumption"]],
    [ 316, 1, Unknown,       False, ["Unknown_Inputs_316"]],
    [ 317, 1, Unknown,       False, ["Unknown_Inputs_317"]],
    [ 318, 1, Unknown,       False, ["Unknown_Inputs_318"]],
    [ 319, 1, Unknown,       False, ["Unknown_Inputs_319"]],
    [ 400, 3, FullVersion,   False, ["Version"]],
]
INPUTS_DEFINITIONS: Final = [LuxtronikModbusField(definition) for definition in INPUTS_DEFINITIONS]
INPUTS_IDX_TO_DEF: Final = {definition.index: definition for definition in INPUTS_DEFINITIONS}

class Inputs(DataVectorModbus):
    """Class that holds all Inputs."""

    logger = logging.getLogger("Luxtronik.Inputs")
    name = "Inputs"
    offset = 10000

    @classmethod
    def _get_definitions(cls):
        return INPUTS_DEFINITIONS

    @classmethod
    def _get_definition_by_idx(cls, idx):
        return INPUTS_IDX_TO_DEF.get(idx, LuxtronikModbusField.invalid())
