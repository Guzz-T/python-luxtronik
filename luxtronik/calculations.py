"""Parse luxtronik calculations."""

import logging

from luxtronik.data_vector import DataVector

from luxtronik.datatypes import (
    BivalenceLevel,
    Bool,
    Celsius,
    Character,
    Count,
    Energy,
    Errorcode,
    Flow,
    Frequency,
    HeatpumpCode,
    Icon,
    IPv4Address,
    Kelvin,
    Level,
    MainMenuStatusLine1,
    MainMenuStatusLine2,
    MainMenuStatusLine3,
    OperationMode,
    Percent2,
    Power,
    Pressure,
    Seconds,
    SecOperationMode,
    Speed,
    SwitchoffFile,
    Timestamp,
    Unknown,
    MajorMinorVersion,
    Voltage,
)


class Calculations(DataVector):
    """Class that holds all calculations."""

    logger = logging.getLogger("Luxtronik.Calculations")
    name = "Calculation"

    _obsolete = {
        "ID_WEB_SoftStand": "get_firmware_version()"
    }

    def __init__(self):
        super().__init__()
        self._data = {
            0: Unknown("Unknown_Calculation_0"),
            1: Unknown("Unknown_Calculation_1"),
            2: Unknown("Unknown_Calculation_2"),
            3: Unknown("Unknown_Calculation_3"),
            4: Unknown("Unknown_Calculation_4"),
            5: Unknown("Unknown_Calculation_5"),
            6: Unknown("Unknown_Calculation_6"),
            7: Unknown("Unknown_Calculation_7"),
            8: Unknown("Unknown_Calculation_8"),
            9: Unknown("Unknown_Calculation_9"),
            10: Celsius(["ID_WEB_Temperatur_TVL", "Unknown_Calculation_10"]),
            11: Celsius(["ID_WEB_Temperatur_TRL", "Unknown_Calculation_11"]),
            12: Celsius(["ID_WEB_Sollwert_TRL_HZ", "Unknown_Calculation_12"]),
            13: Celsius(["ID_WEB_Temperatur_TRL_ext", "Unknown_Calculation_13"]),
            14: Celsius(["ID_WEB_Temperatur_THG", "Unknown_Calculation_14"]),
            15: Celsius(["ID_WEB_Temperatur_TA", "Unknown_Calculation_15"]),
            16: Celsius(["ID_WEB_Mitteltemperatur", "Unknown_Calculation_16"]),
            17: Celsius(["ID_WEB_Temperatur_TBW", "Unknown_Calculation_17"]),
            18: Celsius(["ID_WEB_Einst_BWS_akt", "Unknown_Calculation_18"]),
            19: Celsius(["ID_WEB_Temperatur_TWE", "Unknown_Calculation_19"]),
            20: Celsius(["ID_WEB_Temperatur_TWA", "Unknown_Calculation_20"]),
            21: Celsius(["ID_WEB_Temperatur_TFB1", "Unknown_Calculation_21"]),
            22: Celsius(["ID_WEB_Sollwert_TVL_MK1", "Unknown_Calculation_22"]),
            23: Celsius(["ID_WEB_Temperatur_RFV", "Unknown_Calculation_23"]),
            24: Celsius(["ID_WEB_Temperatur_TFB2", "Unknown_Calculation_24"]),
            25: Celsius(["ID_WEB_Sollwert_TVL_MK2", "Unknown_Calculation_25"]),
            26: Celsius(["ID_WEB_Temperatur_TSK", "Unknown_Calculation_26"]),
            27: Celsius(["ID_WEB_Temperatur_TSS", "Unknown_Calculation_27"]),
            28: Celsius(["ID_WEB_Temperatur_TEE", "Unknown_Calculation_28"]),
            29: Bool(["ID_WEB_ASDin", "Unknown_Calculation_29"]),
            30: Bool(["ID_WEB_BWTin", "Unknown_Calculation_30"]),
            31: Bool(["ID_WEB_EVUin", "Unknown_Calculation_31"]),
            32: Bool(["ID_WEB_HDin", "Unknown_Calculation_32"]),
            33: Bool(["ID_WEB_MOTin", "Unknown_Calculation_33"]),
            34: Bool(["ID_WEB_NDin", "Unknown_Calculation_34"]),
            35: Bool(["ID_WEB_PEXin", "Unknown_Calculation_35"]),
            36: Bool(["ID_WEB_SWTin", "Unknown_Calculation_36"]),
            37: Bool(["ID_WEB_AVout", "Unknown_Calculation_37"]),
            38: Bool(["ID_WEB_BUPout", "Unknown_Calculation_38"]),
            39: Bool(["ID_WEB_HUPout", "Unknown_Calculation_39"]),
            40: Bool(["ID_WEB_MA1out", "Unknown_Calculation_40"]),
            41: Bool(["ID_WEB_MZ1out", "Unknown_Calculation_41"]),
            42: Bool(["ID_WEB_VENout", "Unknown_Calculation_42"]),
            43: Bool(["ID_WEB_VBOout", "Unknown_Calculation_43"]),
            44: Bool(["ID_WEB_VD1out", "Unknown_Calculation_44"]),
            45: Bool(["ID_WEB_VD2out", "Unknown_Calculation_45"]),
            46: Bool(["ID_WEB_ZIPout", "Unknown_Calculation_46"]),
            47: Bool(["ID_WEB_ZUPout", "Unknown_Calculation_47"]),
            48: Bool(["ID_WEB_ZW1out", "Unknown_Calculation_48"]),
            49: Bool(["ID_WEB_ZW2SSTout", "Unknown_Calculation_49"]),
            50: Bool(["ID_WEB_ZW3SSTout", "Unknown_Calculation_50"]),
            51: Bool(["ID_WEB_FP2out", "Unknown_Calculation_51"]),
            52: Bool(["ID_WEB_SLPout", "Unknown_Calculation_52"]),
            53: Bool(["ID_WEB_SUPout", "Unknown_Calculation_53"]),
            54: Bool(["ID_WEB_MZ2out", "Unknown_Calculation_54"]),
            55: Bool(["ID_WEB_MA2out", "Unknown_Calculation_55"]),
            56: Seconds(["ID_WEB_Zaehler_BetrZeitVD1", "Unknown_Calculation_56"]),
            57: Count(["ID_WEB_Zaehler_BetrZeitImpVD1", "Unknown_Calculation_57"]),
            58: Seconds(["ID_WEB_Zaehler_BetrZeitVD2", "Unknown_Calculation_58"]),
            59: Count(["ID_WEB_Zaehler_BetrZeitImpVD2", "Unknown_Calculation_59"]),
            60: Seconds(["ID_WEB_Zaehler_BetrZeitZWE1", "Unknown_Calculation_60"]),
            61: Seconds(["ID_WEB_Zaehler_BetrZeitZWE2", "Unknown_Calculation_61"]),
            62: Seconds(["ID_WEB_Zaehler_BetrZeitZWE3", "Unknown_Calculation_62"]),
            63: Seconds(["ID_WEB_Zaehler_BetrZeitWP", "Unknown_Calculation_63"]),
            64: Seconds(["ID_WEB_Zaehler_BetrZeitHz", "Unknown_Calculation_64"]),
            65: Seconds(["ID_WEB_Zaehler_BetrZeitBW", "Unknown_Calculation_65"]),
            66: Seconds(["ID_WEB_Zaehler_BetrZeitKue", "Unknown_Calculation_66"]),
            67: Seconds(["ID_WEB_Time_WPein_akt", "Unknown_Calculation_67"]),
            68: Seconds(["ID_WEB_Time_ZWE1_akt", "Unknown_Calculation_68"]),
            69: Seconds(["ID_WEB_Time_ZWE2_akt", "Unknown_Calculation_69"]),
            70: Seconds(["ID_WEB_Timer_EinschVerz", "Unknown_Calculation_70"]),
            71: Seconds(["ID_WEB_Time_SSPAUS_akt", "Unknown_Calculation_71"]),
            72: Seconds(["ID_WEB_Time_SSPEIN_akt", "Unknown_Calculation_72"]),
            73: Seconds(["ID_WEB_Time_VDStd_akt", "Unknown_Calculation_73"]),
            74: Seconds(["ID_WEB_Time_HRM_akt", "Unknown_Calculation_74"]),
            75: Seconds(["ID_WEB_Time_HRW_akt", "Unknown_Calculation_75"]),
            76: Seconds(["ID_WEB_Time_LGS_akt", "Unknown_Calculation_76"]),
            77: Seconds(["ID_WEB_Time_SBW_akt", "Unknown_Calculation_77"]),
            78: HeatpumpCode(["ID_WEB_Code_WP_akt", "Unknown_Calculation_78"]),
            79: BivalenceLevel(["ID_WEB_BIV_Stufe_akt", "Unknown_Calculation_79"]),
            80: OperationMode(["ID_WEB_WP_BZ_akt", "Unknown_Calculation_80"]),
            81: Character(["ID_WEB_SoftStand_0", "Unknown_Calculation_81"]),
            82: Character(["ID_WEB_SoftStand_1", "Unknown_Calculation_82"]),
            83: Character(["ID_WEB_SoftStand_2", "Unknown_Calculation_83"]),
            84: Character(["ID_WEB_SoftStand_3", "Unknown_Calculation_84"]),
            85: Character(["ID_WEB_SoftStand_4", "Unknown_Calculation_85"]),
            86: Character(["ID_WEB_SoftStand_5", "Unknown_Calculation_86"]),
            87: Character(["ID_WEB_SoftStand_6", "Unknown_Calculation_87"]),
            88: Character(["ID_WEB_SoftStand_7", "Unknown_Calculation_88"]),
            89: Character(["ID_WEB_SoftStand_8", "Unknown_Calculation_89"]),
            90: Character(["ID_WEB_SoftStand_9", "Unknown_Calculation_90"]),
            91: IPv4Address(["ID_WEB_AdresseIP_akt", "Unknown_Calculation_91"]),
            92: IPv4Address(["ID_WEB_SubNetMask_akt", "Unknown_Calculation_92"]),
            93: IPv4Address(["ID_WEB_Add_Broadcast", "Unknown_Calculation_93"]),
            94: IPv4Address(["ID_WEB_Add_StdGateway", "Unknown_Calculation_94"]),
            95: Timestamp(["ID_WEB_ERROR_Time0", "Unknown_Calculation_95"]),
            96: Timestamp(["ID_WEB_ERROR_Time1", "Unknown_Calculation_96"]),
            97: Timestamp(["ID_WEB_ERROR_Time2", "Unknown_Calculation_97"]),
            98: Timestamp(["ID_WEB_ERROR_Time3", "Unknown_Calculation_98"]),
            99: Timestamp(["ID_WEB_ERROR_Time4", "Unknown_Calculation_99"]),
            100: Errorcode(["ID_WEB_ERROR_Nr0", "Unknown_Calculation_100"]),
            101: Errorcode(["ID_WEB_ERROR_Nr1", "Unknown_Calculation_101"]),
            102: Errorcode(["ID_WEB_ERROR_Nr2", "Unknown_Calculation_102"]),
            103: Errorcode(["ID_WEB_ERROR_Nr3", "Unknown_Calculation_103"]),
            104: Errorcode(["ID_WEB_ERROR_Nr4", "Unknown_Calculation_104"]),
            105: Count(["ID_WEB_AnzahlFehlerInSpeicher", "Unknown_Calculation_105"]),
            106: SwitchoffFile(["ID_WEB_Switchoff_file_Nr0", "Unknown_Calculation_106"]),
            107: SwitchoffFile(["ID_WEB_Switchoff_file_Nr1", "Unknown_Calculation_107"]),
            108: SwitchoffFile(["ID_WEB_Switchoff_file_Nr2", "Unknown_Calculation_108"]),
            109: SwitchoffFile(["ID_WEB_Switchoff_file_Nr3", "Unknown_Calculation_109"]),
            110: SwitchoffFile(["ID_WEB_Switchoff_file_Nr4", "Unknown_Calculation_110"]),
            111: Timestamp(["ID_WEB_Switchoff_file_Time0", "Unknown_Calculation_111"]),
            112: Timestamp(["ID_WEB_Switchoff_file_Time1", "Unknown_Calculation_112"]),
            113: Timestamp(["ID_WEB_Switchoff_file_Time2", "Unknown_Calculation_113"]),
            114: Timestamp(["ID_WEB_Switchoff_file_Time3", "Unknown_Calculation_114"]),
            115: Timestamp(["ID_WEB_Switchoff_file_Time4", "Unknown_Calculation_115"]),
            116: Bool(["ID_WEB_Comfort_exists", "Unknown_Calculation_116"]),
            117: MainMenuStatusLine1(["ID_WEB_HauptMenuStatus_Zeile1", "Unknown_Calculation_117"]),
            118: MainMenuStatusLine2(["ID_WEB_HauptMenuStatus_Zeile2", "Unknown_Calculation_118"]),
            119: MainMenuStatusLine3(["ID_WEB_HauptMenuStatus_Zeile3", "Unknown_Calculation_119"]),
            120: Seconds(["ID_WEB_HauptMenuStatus_Zeit", "Unknown_Calculation_120"]),
            121: Level(["ID_WEB_HauptMenuAHP_Stufe", "Unknown_Calculation_121"]),
            122: Celsius(["ID_WEB_HauptMenuAHP_Temp", "Unknown_Calculation_122"]),
            123: Seconds(["ID_WEB_HauptMenuAHP_Zeit", "Unknown_Calculation_123"]),
            124: Bool(["ID_WEB_SH_BWW", "Unknown_Calculation_124"]),
            125: Icon(["ID_WEB_SH_HZ", "Unknown_Calculation_125"]),
            126: Icon(["ID_WEB_SH_MK1", "Unknown_Calculation_126"]),
            127: Icon(["ID_WEB_SH_MK2", "Unknown_Calculation_127"]),
            128: Unknown(["ID_WEB_Einst_Kurzrpgramm", "Unknown_Calculation_128"]),
            129: Unknown(["ID_WEB_StatusSlave_1", "Unknown_Calculation_129"]),
            130: Unknown(["ID_WEB_StatusSlave_2", "Unknown_Calculation_130"]),
            131: Unknown(["ID_WEB_StatusSlave_3", "Unknown_Calculation_131"]),
            132: Unknown(["ID_WEB_StatusSlave_4", "Unknown_Calculation_132"]),
            133: Unknown(["ID_WEB_StatusSlave_5", "Unknown_Calculation_133"]),
            134: Timestamp(["ID_WEB_AktuelleTimeStamp", "Unknown_Calculation_134"]),
            135: Icon(["ID_WEB_SH_MK3", "Unknown_Calculation_135"]),
            136: Celsius(["ID_WEB_Sollwert_TVL_MK3", "Unknown_Calculation_136"]),
            137: Celsius(["ID_WEB_Temperatur_TFB3", "Unknown_Calculation_137"]),
            138: Bool(["ID_WEB_MZ3out", "Unknown_Calculation_138"]),
            139: Bool(["ID_WEB_MA3out", "Unknown_Calculation_139"]),
            140: Bool(["ID_WEB_FP3out", "Unknown_Calculation_140"]),
            141: Seconds(["ID_WEB_Time_AbtIn", "Unknown_Calculation_141"]),
            142: Celsius(["ID_WEB_Temperatur_RFV2", "Unknown_Calculation_142"]),
            143: Celsius(["ID_WEB_Temperatur_RFV3", "Unknown_Calculation_143"]),
            144: Icon(["ID_WEB_SH_SW", "Unknown_Calculation_144"]),
            145: Unknown(["ID_WEB_Zaehler_BetrZeitSW", "Unknown_Calculation_145"]),
            146: Bool(["ID_WEB_FreigabKuehl", "Unknown_Calculation_146"]),
            147: Voltage(["ID_WEB_AnalogIn", "Unknown_Calculation_147"]),
            148: Unknown(["ID_WEB_SonderZeichen", "Unknown_Calculation_148"]),
            149: Icon(["ID_WEB_SH_ZIP", "Unknown_Calculation_149"]),
            150: Icon(["ID_WEB_WebsrvProgrammWerteBeobarten", "Unknown_Calculation_150"]),
            151: Energy(["ID_WEB_WMZ_Heizung", "Unknown_Calculation_151"]),
            152: Energy(["ID_WEB_WMZ_Brauchwasser", "Unknown_Calculation_152"]),
            153: Energy(["ID_WEB_WMZ_Schwimmbad", "Unknown_Calculation_153"]),
            154: Energy(["ID_WEB_WMZ_Seit", "Unknown_Calculation_154"]),
            155: Flow(["ID_WEB_WMZ_Durchfluss", "Unknown_Calculation_155"]),
            156: Voltage(["ID_WEB_AnalogOut1", "Unknown_Calculation_156"]),
            157: Voltage(["ID_WEB_AnalogOut2", "Unknown_Calculation_157"]),
            158: Seconds(["ID_WEB_Time_Heissgas", "Unknown_Calculation_158"]),
            159: Celsius(["ID_WEB_Temp_Lueftung_Zuluft", "Unknown_Calculation_159"]),
            160: Celsius(["ID_WEB_Temp_Lueftung_Abluft", "Unknown_Calculation_160"]),
            161: Seconds(["ID_WEB_Zaehler_BetrZeitSolar", "Unknown_Calculation_161"]),
            162: Voltage(["ID_WEB_AnalogOut3", "Unknown_Calculation_162"]),
            163: Voltage(["ID_WEB_AnalogOut4", "Unknown_Calculation_163"]),
            164: Voltage(["ID_WEB_Out_VZU", "Unknown_Calculation_164"]),
            165: Voltage(["ID_WEB_Out_VAB", "Unknown_Calculation_165"]),
            166: Bool(["ID_WEB_Out_VSK", "Unknown_Calculation_166"]),
            167: Bool(["ID_WEB_Out_FRH", "Unknown_Calculation_167"]),
            168: Voltage(["ID_WEB_AnalogIn2", "Unknown_Calculation_168"]),
            169: Voltage(["ID_WEB_AnalogIn3", "Unknown_Calculation_169"]),
            170: Bool(["ID_WEB_SAXin", "Unknown_Calculation_170"]),
            171: Bool(["ID_WEB_SPLin", "Unknown_Calculation_171"]),
            172: Bool(["ID_WEB_Compact_exists", "Unknown_Calculation_172"]),
            173: Flow(["ID_WEB_Durchfluss_WQ", "Unknown_Calculation_173"]),
            174: Bool(["ID_WEB_LIN_exists", "Unknown_Calculation_174"]),
            175: Celsius(["ID_WEB_LIN_ANSAUG_VERDAMPFER", "Unknown_Calculation_175"]),
            176: Celsius(["ID_WEB_LIN_ANSAUG_VERDICHTER", "Unknown_Calculation_176"]),
            177: Celsius(["ID_WEB_LIN_VDH", "Unknown_Calculation_177"]),
            178: Kelvin(["ID_WEB_LIN_UH", "Unknown_Calculation_178"]),
            179: Kelvin(["ID_WEB_LIN_UH_Soll", "Unknown_Calculation_179"]),
            180: Pressure(["ID_WEB_LIN_HD", "Unknown_Calculation_180"]),
            181: Pressure(["ID_WEB_LIN_ND", "Unknown_Calculation_181"]),
            182: Bool(["ID_WEB_LIN_VDH_out", "Unknown_Calculation_182"]),
            183: Percent2(["ID_WEB_HZIO_PWM", "Unknown_Calculation_183"]),
            184: Speed(["ID_WEB_HZIO_VEN", "Unknown_Calculation_184"]),
            185: Unknown(["ID_WEB_HZIO_EVU2", "Unknown_Calculation_185"]),
            186: Bool(["ID_WEB_HZIO_STB", "Unknown_Calculation_186"]),
            187: Energy(["ID_WEB_SEC_Qh_Soll", "Unknown_Calculation_187"]),
            188: Energy(["ID_WEB_SEC_Qh_Ist", "Unknown_Calculation_188"]),
            189: Celsius(["ID_WEB_SEC_TVL_Soll", "Unknown_Calculation_189"]),
            190: Unknown(["ID_WEB_SEC_Software", "Unknown_Calculation_190"]),
            191: SecOperationMode(["ID_WEB_SEC_BZ", "Unknown_Calculation_191"]),
            192: Unknown(["ID_WEB_SEC_VWV", "Unknown_Calculation_192"]),
            193: Speed(["ID_WEB_SEC_VD", "Unknown_Calculation_193"]),
            194: Celsius(["ID_WEB_SEC_VerdEVI", "Unknown_Calculation_194"]),
            195: Celsius(["ID_WEB_SEC_AnsEVI", "Unknown_Calculation_195"]),
            196: Kelvin(["ID_WEB_SEC_UEH_EVI", "Unknown_Calculation_196"]),
            197: Kelvin(["ID_WEB_SEC_UEH_EVI_S", "Unknown_Calculation_197"]),
            198: Celsius(["ID_WEB_SEC_KondTemp", "Unknown_Calculation_198"]),
            199: Celsius(["ID_WEB_SEC_FlussigEx", "Unknown_Calculation_199"]),
            200: Celsius(["ID_WEB_SEC_UK_EEV", "Unknown_Calculation_200"]),
            201: Pressure(["ID_WEB_SEC_EVI_Druck", "Unknown_Calculation_201"]),
            202: Voltage(["ID_WEB_SEC_U_Inv", "Unknown_Calculation_202"]),
            203: Celsius(["ID_WEB_Temperatur_THG_2", "Unknown_Calculation_203"]),
            204: Celsius(["ID_WEB_Temperatur_TWE_2", "Unknown_Calculation_204"]),
            205: Celsius(["ID_WEB_LIN_ANSAUG_VERDAMPFER_2", "Unknown_Calculation_205"]),
            206: Celsius(["ID_WEB_LIN_ANSAUG_VERDICHTER_2", "Unknown_Calculation_206"]),
            207: Celsius(["ID_WEB_LIN_VDH_2", "Unknown_Calculation_207"]),
            208: Kelvin(["ID_WEB_LIN_UH_2", "Unknown_Calculation_208"]),
            209: Kelvin(["ID_WEB_LIN_UH_Soll_2", "Unknown_Calculation_209"]),
            210: Pressure(["ID_WEB_LIN_HD_2", "Unknown_Calculation_210"]),
            211: Pressure(["ID_WEB_LIN_ND_2", "Unknown_Calculation_211"]),
            212: Bool(["ID_WEB_HDin_2", "Unknown_Calculation_212"]),
            213: Bool(["ID_WEB_AVout_2", "Unknown_Calculation_213"]),
            214: Bool(["ID_WEB_VBOout_2", "Unknown_Calculation_214"]),
            215: Bool(["ID_WEB_VD1out_2", "Unknown_Calculation_215"]),
            216: Bool(["ID_WEB_LIN_VDH_out_2", "Unknown_Calculation_216"]),
            217: SwitchoffFile(["ID_WEB_Switchoff2_file_Nr0", "Unknown_Calculation_217"]),
            218: SwitchoffFile(["ID_WEB_Switchoff2_file_Nr1", "Unknown_Calculation_218"]),
            219: SwitchoffFile(["ID_WEB_Switchoff2_file_Nr2", "Unknown_Calculation_219"]),
            220: SwitchoffFile(["ID_WEB_Switchoff2_file_Nr3", "Unknown_Calculation_220"]),
            221: SwitchoffFile(["ID_WEB_Switchoff2_file_Nr4", "Unknown_Calculation_221"]),
            222: Timestamp(["ID_WEB_Switchoff2_file_Time0", "Unknown_Calculation_222"]),
            223: Timestamp(["ID_WEB_Switchoff2_file_Time1", "Unknown_Calculation_223"]),
            224: Timestamp(["ID_WEB_Switchoff2_file_Time2", "Unknown_Calculation_224"]),
            225: Timestamp(["ID_WEB_Switchoff2_file_Time3", "Unknown_Calculation_225"]),
            226: Timestamp(["ID_WEB_Switchoff2_file_Time4", "Unknown_Calculation_226"]),
            227: Celsius(["ID_WEB_RBE_RT_Ist", "Unknown_Calculation_227"]),
            228: Celsius(["ID_WEB_RBE_RT_Soll", "Unknown_Calculation_228"]),
            229: Celsius(["ID_WEB_Temperatur_BW_oben", "Unknown_Calculation_229"]),
            230: HeatpumpCode(["ID_WEB_Code_WP_akt_2", "Unknown_Calculation_230"]),
            231: Frequency(["ID_WEB_Freq_VD", "Unknown_Calculation_231"]),
            232: Celsius(["Vapourisation_Temperature", "Unknown_Calculation_232"]),
            233: Celsius(["Liquefaction_Temperature", "Unknown_Calculation_233"]),
            234: Unknown("Unknown_Calculation_234"),
            235: Unknown("Unknown_Calculation_235"),
            236: Frequency(["ID_WEB_Freq_VD_Soll", "Unknown_Calculation_236"]),
            237: Frequency(["ID_WEB_Freq_VD_Min", "Unknown_Calculation_237"]),
            238: Frequency(["ID_WEB_Freq_VD_Max", "Unknown_Calculation_238"]),
            239: Kelvin(["VBO_Temp_Spread_Soll", "Unknown_Calculation_239"]),
            240: Kelvin(["VBO_Temp_Spread_Ist", "Unknown_Calculation_240"]),
            241: Percent2(["HUP_PWM", "Circulation_Pump", "Unknown_Calculation_241"]),
            242: Kelvin(["HUP_Temp_Spread_Soll", "Unknown_Calculation_242"]),
            243: Kelvin(["HUP_Temp_Spread_Ist", "Unknown_Calculation_243"]),
            244: Unknown("Unknown_Calculation_244"),
            245: Unknown("Unknown_Calculation_245"),
            246: Unknown("Unknown_Calculation_246"),
            247: Unknown("Unknown_Calculation_247"),
            248: Unknown("Unknown_Calculation_248"),
            249: Unknown("Unknown_Calculation_249"),
            250: Unknown("Unknown_Calculation_250"),
            251: Unknown("Unknown_Calculation_251"),
            252: Unknown("Unknown_Calculation_252"),
            253: Unknown("Unknown_Calculation_253"),
            254: Flow(["Flow_Rate_254", "Unknown_Calculation_254"]),
            255: Unknown("Unknown_Calculation_255"),
            256: Unknown("Unknown_Calculation_256"),
            257: Power(["Heat_Output", "Unknown_Calculation_257"]),
            258: MajorMinorVersion(["RBE_Version", "Unknown_Calculation_258"]),
            259: Unknown("Unknown_Calculation_259"),
            260: Unknown("Unknown_Calculation_260"),
            261: Unknown("Unknown_Calculation_261"),
            262: Unknown("Unknown_Calculation_262"),
            263: Unknown("Unknown_Calculation_263"),
            264: Unknown("Unknown_Calculation_264"),
            265: Unknown("Unknown_Calculation_265"),
            266: Unknown("Unknown_Calculation_266"),
            267: Celsius(["Desired_Room_Temperature", "Unknown_Calculation_267"]),
        }
