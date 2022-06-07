"""Parse luxtonik visibilities."""
import logging

from luxtronik.datatypes import Unknown

LOGGER = logging.getLogger("Luxtronik.Visibilities")


class Visibilities:
    """Class that holds all visibilities."""

    visibilities = {
        0: Unknown("ID_Visi_NieAnzeigen"),
        1: Unknown("ID_Visi_ImmerAnzeigen"),
        2: Unknown("ID_Visi_Heizung"),
        3: Unknown("ID_Visi_Brauwasser"),
        4: Unknown("ID_Visi_Schwimmbad"),
        5: Unknown("ID_Visi_Kuhlung"),
        6: Unknown("ID_Visi_Lueftung"),
        7: Unknown("ID_Visi_MK1"),
        8: Unknown("ID_Visi_MK2"),
        9: Unknown("ID_Visi_ThermDesinfekt"),
        10: Unknown("ID_Visi_Zirkulation"),
        11: Unknown("ID_Visi_KuhlTemp_SolltempMK1"),
        12: Unknown("ID_Visi_KuhlTemp_SolltempMK2"),
        13: Unknown("ID_Visi_KuhlTemp_ATDiffMK1"),
        14: Unknown("ID_Visi_KuhlTemp_ATDiffMK2"),
        15: Unknown("ID_Visi_Service_Information"),
        16: Unknown("ID_Visi_Service_Einstellung"),
        17: Unknown("ID_Visi_Service_Sprache"),
        18: Unknown("ID_Visi_Service_DatumUhrzeit"),
        19: Unknown("ID_Visi_Service_Ausheiz"),
        20: Unknown("ID_Visi_Service_Anlagenkonfiguration"),
        21: Unknown("ID_Visi_Service_IBNAssistant"),
        22: Unknown("ID_Visi_Service_ParameterIBNZuruck"),
        23: Unknown("ID_Visi_Temp_Vorlauf"),
        24: Unknown("ID_Visi_Temp_Rucklauf"),
        25: Unknown("ID_Visi_Temp_RL_Soll"),
        26: Unknown("ID_Visi_Temp_Ruecklext"),
        27: Unknown("ID_Visi_Temp_Heissgas"),
        28: Unknown("ID_Visi_Temp_Aussent"),
        29: Unknown("ID_Visi_Temp_BW_Ist"),
        30: Unknown("ID_Visi_Temp_BW_Soll"),
        31: Unknown("ID_Visi_Temp_WQ_Ein"),
        32: Unknown("ID_Visi_Temp_Kaltekreis"),
        33: Unknown("ID_Visi_Temp_MK1_Vorlauf"),
        34: Unknown("ID_Visi_Temp_MK1VL_Soll"),
        35: Unknown("ID_Visi_Temp_Raumstation"),
        36: Unknown("ID_Visi_Temp_MK2_Vorlauf"),
        37: Unknown("ID_Visi_Temp_MK2VL_Soll"),
        38: Unknown("ID_Visi_Temp_Solarkoll"),
        39: Unknown("ID_Visi_Temp_Solarsp"),
        40: Unknown("ID_Visi_Temp_Ext_Energ"),
        41: Unknown("ID_Visi_IN_ASD"),
        42: Unknown("ID_Visi_IN_BWT"),
        43: Unknown("ID_Visi_IN_EVU"),
        44: Unknown("ID_Visi_IN_HD"),
        45: Unknown("ID_Visi_IN_MOT"),
        46: Unknown("ID_Visi_IN_ND"),
        47: Unknown("ID_Visi_IN_PEX"),
        48: Unknown("ID_Visi_IN_SWT"),
        49: Unknown("ID_Visi_OUT_Abtauventil"),
        50: Unknown("ID_Visi_OUT_BUP"),
        51: Unknown("ID_Visi_OUT_FUP1"),
        52: Unknown("ID_Visi_OUT_HUP"),
        53: Unknown("ID_Visi_OUT_Mischer1Auf"),
        54: Unknown("ID_Visi_OUT_Mischer1Zu"),
        55: Unknown("ID_Visi_OUT_Ventilation"),
        56: Unknown("ID_Visi_OUT_Ventil_BOSUP"),
        57: Unknown("ID_Visi_OUT_Verdichter1"),
        58: Unknown("ID_Visi_OUT_Verdichter2"),
        59: Unknown("ID_Visi_OUT_ZIP"),
        60: Unknown("ID_Visi_OUT_ZUP"),
        61: Unknown("ID_Visi_OUT_ZWE1"),
        62: Unknown("ID_Visi_OUT_ZWE2_SST"),
        63: Unknown("ID_Visi_OUT_ZWE3"),
        64: Unknown("ID_Visi_OUT_FUP2"),
        65: Unknown("ID_Visi_OUT_SLP"),
        66: Unknown("ID_Visi_OUT_SUP"),
        67: Unknown("ID_Visi_OUT_Mischer2Auf"),
        68: Unknown("ID_Visi_OUT_Mischer2Zu"),
        69: Unknown("ID_Visi_AblaufZ_WP_Seit"),
        70: Unknown("ID_Visi_AblaufZ_ZWE1_seit"),
        71: Unknown("ID_Visi_AblaufZ_ZWE2_seit"),
        72: Unknown("ID_Visi_AblaufZ_ZWE3_seit"),
        73: Unknown("ID_Visi_AblaufZ_Netzeinv"),
        74: Unknown("ID_Visi_AblaufZ_SSP_Zeit1"),
        75: Unknown("ID_Visi_AblaufZ_VD_Stand"),
        76: Unknown("ID_Visi_AblaufZ_HRM_Zeit"),
        77: Unknown("ID_Visi_AblaufZ_HRW_Zeit"),
        78: Unknown("ID_Visi_AblaufZ_TDI_seit"),
        79: Unknown("ID_Visi_AblaufZ_Sperre_BW"),
        80: Unknown("ID_Visi_Bst_BStdVD1"),
        81: Unknown("ID_Visi_Bst_ImpVD1"),
        82: Unknown("ID_Visi_Bst_dEZVD1"),
        83: Unknown("ID_Visi_Bst_BStdVD2"),
        84: Unknown("ID_Visi_Bst_ImpVD2"),
        85: Unknown("ID_Visi_Bst_dEZVD2"),
        86: Unknown("ID_Visi_Bst_BStdZWE1"),
        87: Unknown("ID_Visi_Bst_BStdZWE2"),
        88: Unknown("ID_Visi_Bst_BStdZWE3"),
        89: Unknown("ID_Visi_Bst_BStdWP"),
        90: Unknown("ID_Visi_Text_Kurzprogramme"),
        91: Unknown("ID_Visi_Text_Zwangsheizung"),
        92: Unknown("ID_Visi_Text_Zwangsbrauchwasser"),
        93: Unknown("ID_Visi_Text_Abtauen"),
        94: Unknown("ID_Visi_EinstTemp_RucklBegr"),
        95: Unknown("ID_Visi_EinstTemp_HystereseHR"),
        96: Unknown("ID_Visi_EinstTemp_TRErhmax"),
        97: Unknown("ID_Visi_EinstTemp_Freig2VD"),
        98: Unknown("ID_Visi_EinstTemp_FreigZWE"),
        99: Unknown("ID_Visi_EinstTemp_Tluftabt"),
        100: Unknown("ID_Visi_EinstTemp_TDISolltemp"),
        101: Unknown("ID_Visi_EinstTemp_HystereseBW"),
        102: Unknown("ID_Visi_EinstTemp_Vorl2VDBW"),
        103: Unknown("ID_Visi_EinstTemp_TAussenmax"),
        104: Unknown("ID_Visi_EinstTemp_TAussenmin"),
        105: Unknown("ID_Visi_EinstTemp_TWQmin"),
        106: Unknown("ID_Visi_EinstTemp_THGmax"),
        107: Unknown("ID_Visi_EinstTemp_TLABTEnde"),
        108: Unknown("ID_Visi_EinstTemp_Absenkbis"),
        109: Unknown("ID_Visi_EinstTemp_Vorlaufmax"),
        110: Unknown("ID_Visi_EinstTemp_TDiffEin"),
        111: Unknown("ID_Visi_EinstTemp_TDiffAus"),
        112: Unknown("ID_Visi_EinstTemp_TDiffmax"),
        113: Unknown("ID_Visi_EinstTemp_TEEHeizung"),
        114: Unknown("ID_Visi_EinstTemp_TEEBrauchw"),
        115: Unknown("ID_Visi_EinstTemp_Vorl2VDSW"),
        116: Unknown("ID_Visi_EinstTemp_VLMaxMk1"),
        117: Unknown("ID_Visi_EinstTemp_VLMaxMk2"),
        118: Unknown("ID_Visi_Priori_Brauchwasser"),
        119: Unknown("ID_Visi_Priori_Heizung"),
        120: Unknown("ID_Visi_Priori_Schwimmbad"),
        121: Unknown("ID_Visi_SysEin_EVUSperre"),
        122: Unknown("ID_Visi_SysEin_Raumstation"),
        123: Unknown("ID_Visi_SysEin_Einbindung"),
        124: Unknown("ID_Visi_SysEin_Mischkreis1"),
        125: Unknown("ID_Visi_SysEin_Mischkreis2"),
        126: Unknown("ID_Visi_SysEin_ZWE1Art"),
        127: Unknown("ID_Visi_SysEin_ZWE1Fkt"),
        128: Unknown("ID_Visi_SysEin_ZWE2Art"),
        129: Unknown("ID_Visi_SysEin_ZWE2Fkt"),
        130: Unknown("ID_Visi_SysEin_ZWE3Art"),
        131: Unknown("ID_Visi_SysEin_ZWE3Fkt"),
        132: Unknown("ID_Visi_SysEin_Stoerung"),
        133: Unknown("ID_Visi_SysEin_Brauchwasser1"),
        134: Unknown("ID_Visi_SysEin_Brauchwasser2"),
        135: Unknown("ID_Visi_SysEin_Brauchwasser3"),
        136: Unknown("ID_Visi_SysEin_Brauchwasser4"),
        137: Unknown("ID_Visi_SysEin_Brauchwasser5"),
        138: Unknown("ID_Visi_SysEin_BWWPmax"),
        139: Unknown("ID_Visi_SysEin_Abtzykmax"),
        140: Unknown("ID_Visi_SysEin_Luftabt"),
        141: Unknown("ID_Visi_SysEin_LuftAbtmax"),
        142: Unknown("ID_Visi_SysEin_Abtauen1"),
        143: Unknown("ID_Visi_SysEin_Abtauen2"),
        144: Unknown("ID_Visi_SysEin_Pumpenoptim"),
        145: Unknown("ID_Visi_SysEin_Zusatzpumpe"),
        146: Unknown("ID_Visi_SysEin_Zugang"),
        147: Unknown("ID_Visi_SysEin_SoledrDurchf"),
        148: Unknown("ID_Visi_SysEin_UberwachungVD"),
        149: Unknown("ID_Visi_SysEin_RegelungHK"),
        150: Unknown("ID_Visi_SysEin_RegelungMK1"),
        151: Unknown("ID_Visi_SysEin_RegelungMK2"),
        152: Unknown("ID_Visi_SysEin_Kuhlung"),
        153: Unknown("ID_Visi_SysEin_Ausheizen"),
        154: Unknown("ID_Visi_SysEin_ElektrAnode"),
        155: Unknown("ID_Visi_SysEin_SWBBer"),
        156: Unknown("ID_Visi_SysEin_SWBMin"),
        157: Unknown("ID_Visi_SysEin_Heizung"),
        158: Unknown("ID_Visi_SysEin_PeriodeMk1"),
        159: Unknown("ID_Visi_SysEin_LaufzeitMk1"),
        160: Unknown("ID_Visi_SysEin_PeriodeMk2"),
        161: Unknown("ID_Visi_SysEin_LaufzeitMk2"),
        162: Unknown("ID_Visi_SysEin_Heizgrenze"),
        163: Unknown("ID_Visi_Enlt_HUP"),
        164: Unknown("ID_Visi_Enlt_ZUP"),
        165: Unknown("ID_Visi_Enlt_BUP"),
        166: Unknown("ID_Visi_Enlt_Ventilator_BOSUP"),
        167: Unknown("ID_Visi_Enlt_MA1"),
        168: Unknown("ID_Visi_Enlt_MZ1"),
        169: Unknown("ID_Visi_Enlt_ZIP"),
        170: Unknown("ID_Visi_Enlt_MA2"),
        171: Unknown("ID_Visi_Enlt_MZ2"),
        172: Unknown("ID_Visi_Enlt_SUP"),
        173: Unknown("ID_Visi_Enlt_SLP"),
        174: Unknown("ID_Visi_Enlt_FP2"),
        175: Unknown("ID_Visi_Enlt_Laufzeit"),
        176: Unknown("ID_Visi_Anlgkonf_Heizung"),
        177: Unknown("ID_Visi_Anlgkonf_Brauchwarmwasser"),
        178: Unknown("ID_Visi_Anlgkonf_Schwimmbad"),
        179: Unknown("ID_Visi_Heizung_Betriebsart"),
        180: Unknown("ID_Visi_Heizung_TemperaturPlusMinus"),
        181: Unknown("ID_Visi_Heizung_Heizkurven"),
        182: Unknown("ID_Visi_Heizung_Zeitschlaltprogramm"),
        183: Unknown("ID_Visi_Heizung_Heizgrenze"),
        184: Unknown("ID_Visi_Mitteltemperatur"),
        185: Unknown("ID_Visi_Dataenlogger"),
        186: Unknown("ID_Visi_Sprachen_DEUTSCH"),
        187: Unknown("ID_Visi_Sprachen_ENGLISH"),
        188: Unknown("ID_Visi_Sprachen_FRANCAIS"),
        189: Unknown("ID_Visi_Sprachen_NORWAY"),
        190: Unknown("ID_Visi_Sprachen_TCHECH"),
        191: Unknown("ID_Visi_Sprachen_ITALIANO"),
        192: Unknown("ID_Visi_Sprachen_NEDERLANDS"),
        193: Unknown("ID_Visi_Sprachen_SVENSKA"),
        194: Unknown("ID_Visi_Sprachen_POLSKI"),
        195: Unknown("ID_Visi_Sprachen_MAGYARUL"),
        196: Unknown("ID_Visi_ErrorUSBspeichern"),
        197: Unknown("ID_Visi_Bst_BStdHz"),
        198: Unknown("ID_Visi_Bst_BStdBW"),
        199: Unknown("ID_Visi_Bst_BStdKue"),
        200: Unknown("ID_Visi_Service_Systemsteuerung"),
        201: Unknown("ID_Visi_Service_Systemsteuerung_Contrast"),
        202: Unknown("ID_Visi_Service_Systemsteuerung_Webserver"),
        203: Unknown("ID_Visi_Service_Systemsteuerung_IPAdresse"),
        204: Unknown("ID_Visi_Service_Systemsteuerung_Fernwartung"),
        205: Unknown("ID_Visi_Paralleleschaltung"),
        206: Unknown("ID_Visi_SysEin_Paralleleschaltung"),
        207: Unknown("ID_Visi_Sprachen_DANSK"),
        208: Unknown("ID_Visi_Sprachen_PORTUGES"),
        209: Unknown("ID_Visi_Heizkurve_Heizung"),
        210: Unknown("ID_Visi_SysEin_Mischkreis3"),
        211: Unknown("ID_Visi_MK3"),
        212: Unknown("ID_Visi_Temp_MK3_Vorlauf"),
        213: Unknown("ID_Visi_Temp_MK3VL_Soll"),
        214: Unknown("ID_Visi_OUT_Mischer3Auf"),
        215: Unknown("ID_Visi_OUT_Mischer3Zu"),
        216: Unknown("ID_Visi_SysEin_RegelungMK3"),
        217: Unknown("ID_Visi_SysEin_PeriodeMk3"),
        218: Unknown("ID_Visi_SysEin_LaufzeitMk3"),
        219: Unknown("ID_Visi_SysEin_Kuhl_Zeit_Ein"),
        220: Unknown("ID_Visi_SysEin_Kuhl_Zeit_Aus"),
        221: Unknown("ID_Visi_AblaufZ_AbtauIn"),
        222: Unknown("ID_Visi_Waermemenge_WS"),
        223: Unknown("ID_Visi_Waermemenge_WQ"),
        224: Unknown("ID_Visi_Enlt_MA3"),
        225: Unknown("ID_Visi_Enlt_MZ3"),
        226: Unknown("ID_Visi_Enlt_FP3"),
        227: Unknown("ID_Visi_OUT_FUP3"),
        228: Unknown("ID_Visi_Temp_Raumstation2"),
        229: Unknown("ID_Visi_Temp_Raumstation3"),
        230: Unknown("ID_Visi_Bst_BStdSW"),
        231: Unknown("ID_Visi_Sprachen_LITAUISCH"),
        232: Unknown("ID_Visi_Sprachen_ESTNICH"),
        233: Unknown("ID_Visi_SysEin_Fernwartung"),
        234: Unknown("ID_Visi_Sprachen_SLOVENISCH"),
        235: Unknown("ID_Visi_EinstTemp_TA_EG"),
        236: Unknown("ID_Visi_Einst_TVLmax_EG"),
        237: Unknown("ID_Visi_SysEin_PoptNachlauf"),
        238: Unknown("ID_Visi_RFV_K_Kuehlin"),
        239: Unknown("ID_Visi_SysEin_EffizienzpumpeNom"),
        240: Unknown("ID_Visi_SysEin_EffizienzpumpeMin"),
        241: Unknown("ID_Visi_SysEin_Effizienzpumpe"),
        242: Unknown("ID_Visi_SysEin_Waermemenge"),
        243: Unknown("ID_Visi_Service_WMZ_Effizienz"),
        244: Unknown("ID_Visi_SysEin_Wm_Versorgung_Korrektur"),
        245: Unknown("ID_Visi_SysEin_Wm_Auswertung_Korrektur"),
        246: Unknown("ID_Visi_IN_AnalogIn"),
        247: Unknown("ID_Visi_Eins_SN_Eingabe"),
        248: Unknown("ID_Visi_OUT_Analog_1"),
        249: Unknown("ID_Visi_OUT_Analog_2"),
        250: Unknown("ID_Visi_Solar"),
        251: Unknown("ID_Visi_SysEin_Solar"),
        252: Unknown("ID_Visi_EinstTemp_TDiffKollmax"),
        253: Unknown("ID_Visi_AblaufZ_HG_Sperre"),
        254: Unknown("ID_Visi_SysEin_Akt_Kuehlung"),
        255: Unknown("ID_Visi_SysEin_Vorlauf_VBO"),
        256: Unknown("ID_Visi_Einst_KRHyst"),
        257: Unknown("ID_Visi_Einst_Akt_Kuehl_Speicher_min"),
        258: Unknown("ID_Visi_Einst_Akt_Kuehl_Freig_WQE"),
        259: Unknown("ID_Visi_SysEin_AbtZykMin"),
        260: Unknown("ID_Visi_SysEin_VD2_Zeit_Min"),
        261: Unknown("ID_Visi_EinstTemp_Hysterese_HR_verkuerzt"),
        262: Unknown("ID_Visi_Einst_Luf_Feuchteschutz_akt"),
        263: Unknown("ID_Visi_Einst_Luf_Reduziert_akt"),
        264: Unknown("ID_Visi_Einst_Luf_Nennlueftung_akt"),
        265: Unknown("ID_Visi_Einst_Luf_Intensivlueftung_akt"),
        266: Unknown("ID_Visi_Temperatur_Lueftung_Zuluft"),
        267: Unknown("ID_Visi_Temperatur_Lueftung_Abluft"),
        268: Unknown("ID_Visi_OUT_Analog_3"),
        269: Unknown("ID_Visi_OUT_Analog_4"),
        270: Unknown("ID_Visi_IN_Analog_2"),
        271: Unknown("ID_Visi_IN_Analog_3"),
        272: Unknown("ID_Visi_IN_SAX"),
        273: Unknown("ID_Visi_OUT_VZU"),
        274: Unknown("ID_Visi_OUT_VAB"),
        275: Unknown("ID_Visi_OUT_VSK"),
        276: Unknown("ID_Visi_OUT_FRH"),
        277: Unknown("ID_Visi_KuhlTemp_SolltempMK3"),
        278: Unknown("ID_Visi_KuhlTemp_ATDiffMK3"),
        279: Unknown("ID_Visi_IN_SPL"),
        280: Unknown("ID_Visi_SysEin_Lueftungsstufen"),
        281: Unknown("ID_Visi_SysEin_Meldung_TDI"),
        282: Unknown("ID_Visi_SysEin_Typ_WZW"),
        283: Unknown("ID_Visi_BACnet"),
        284: Unknown("ID_Visi_Sprachen_SLOWAKISCH"),
        285: Unknown("ID_Visi_Sprachen_LETTISCH"),
        286: Unknown("ID_Visi_Sprachen_FINNISCH"),
        287: Unknown("ID_Visi_Kalibrierung_LWD"),
        288: Unknown("ID_Visi_IN_Durchfluss"),
        289: Unknown("ID_Visi_LIN_ANSAUG_VERDICHTER"),
        290: Unknown("ID_Visi_LIN_VDH"),
        291: Unknown("ID_Visi_LIN_UH"),
        292: Unknown("ID_Visi_LIN_Druck"),
        293: Unknown("ID_Visi_Einst_Sollwert_TRL_Kuehlen"),
        294: Unknown("ID_Visi_Entl_ExVentil"),
        295: Unknown("ID_Visi_Einst_Medium_Waermequelle"),
        296: Unknown("ID_Visi_Einst_Multispeicher"),
        297: Unknown("ID_Visi_Einst_Minimale_Ruecklaufsolltemperatur"),
        298: Unknown("ID_Visi_Einst_PKuehlTime"),
        299: Unknown("ID_Visi_Sprachen_TUERKISCH"),
        300: Unknown("ID_Visi_RBE"),
        301: Unknown("ID_Visi_Einst_Luf_Stufen_Faktor"),
        302: Unknown("ID_Visi_Freigabe_Zeit_ZWE"),
        303: Unknown("ID_Visi_Einst_min_VL_Kuehl"),
        304: Unknown("ID_Visi_ZWE1"),
        305: Unknown("ID_Visi_ZWE2"),
        306: Unknown("ID_Visi_ZWE3"),
        307: Unknown("ID_Visi_SEC"),
        308: Unknown("ID_Visi_HZIO"),
        309: Unknown("ID_Visi_WPIO"),
        310: Unknown("ID_Visi_LIN_ANSAUG_VERDAMPFER"),
        311: Unknown("ID_Visi_LIN_MULTI1"),
        312: Unknown("ID_Visi_LIN_MULTI2"),
        313: Unknown("ID_Visi_Einst_Leistung_ZWE"),
        314: Unknown("ID_Visi_Sprachen_ESPANOL"),
        315: Unknown("ID_Visi_Temp_BW_oben"),
        316: Unknown("ID_Visi_MAXIO"),
        317: Unknown("ID_Visi_OUT_Abtauwunsch"),
        318: Unknown("ID_Visi_SmartGrid"),
        319: Unknown("ID_Visi_Drehzahlgeregelt"),
        320: Unknown("ID_Visi_P155_Inverter"),
        321: Unknown("ID_Visi_Leistungsfreigabe"),
        322: Unknown("ID_Visi_Einst_Vorl_akt_Kuehl"),
        323: Unknown("ID_Visi_Einst_Abtauen_im_Warmwasser"),
        324: Unknown("ID_Visi_Waermemenge_ZWE"),
        325: Unknown("Unknown_Visibility_325"),
        326: Unknown("Unknown_Visibility_326"),
        327: Unknown("Unknown_Visibility_327"),
        328: Unknown("Unknown_Visibility_328"),
        329: Unknown("Unknown_Visibility_329"),
        330: Unknown("Unknown_Visibility_330"),
        331: Unknown("Unknown_Visibility_331"),
        332: Unknown("Unknown_Visibility_332"),
        333: Unknown("Unknown_Visibility_333"),
        334: Unknown("Unknown_Visibility_334"),
        335: Unknown("Unknown_Visibility_335"),
        336: Unknown("Unknown_Visibility_336"),
        337: Unknown("Unknown_Visibility_337"),
        338: Unknown("Unknown_Visibility_338"),
        339: Unknown("Unknown_Visibility_339"),
        340: Unknown("Unknown_Visibility_340"),
        341: Unknown("Unknown_Visibility_341"),
        342: Unknown("Unknown_Visibility_342"),
        343: Unknown("Unknown_Visibility_343"),
        344: Unknown("Unknown_Visibility_344"),
        345: Unknown("Unknown_Visibility_345"),
        346: Unknown("Unknown_Visibility_346"),
        347: Unknown("Unknown_Visibility_347"),
        348: Unknown("Unknown_Visibility_348"),
        349: Unknown("Unknown_Visibility_349"),
        350: Unknown("Unknown_Visibility_350"),
        351: Unknown("Unknown_Visibility_351"),
        352: Unknown("Unknown_Visibility_352"),
        353: Unknown("Unknown_Visibility_353"),
        354: Unknown("Unknown_Visibility_354"),
    }

    def parse(self, raw_data):
        """Parse raw visibility data."""
        for index, data in enumerate(raw_data):
            visibility = self.visibilities.get(index, False)
            if visibility is not False:
                visibility.value = visibility.from_heatpump(data)
            else:
                #LOGGER.warning("Visibility '%d' not in list of visibilities", index)
                visibility = Unknown(f"Unknown_Parameter_{index}")
                visibility.value = visibility.from_heatpump(data)
                self.visibilities[index] = visibility

    def _lookup(self, target):
        """Lookup visibility by either id or name."""
        if isinstance(target, int):
            return self.visibilities.get(target, None)
        if isinstance(target, str):
            try:
                target = int(target)
                return self.visibilities.get(target, None)
            except ValueError:
                for _, visibility in self.visibilities.items():
                    if visibility.name == target:
                        return visibility
        LOGGER.warning("Visibility '%s' not found", target)
        return None

    def get(self, target):
        """Get visibility by id or name."""
        visibility = self._lookup(target)
        return visibility
