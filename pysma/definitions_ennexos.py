from typing import Any, Dict
from .sensor import Sensor
from .const import Identifier


'''
Data-Source:
https://www.sma.de/produkte/solar-wechselrichter/sunny-tripower-x
Technical Information - Parameters and Measured Values STP 12-50 / STP 15-50 / STP 20-50 / STP 25-50 (Sunny Tripower X) with firmware package 03.02.07.R 



'''
ennexMapper: Dict[int, str] = {
    35: "Error",
    51: "Closed",
    276: "Instantaneous value",
    295: "MPP",
    303: "Off",
    307: "OK",
    308: "On",
    309: "Operation",
    311: "Open",
    325: "Phase L1 (phsA)",
    326: "Phases L1, L2 and L3 (phsABC)",
    327: "Phase L2 (phsB)",
    329: "Phase L3 (phsC)",
    336: "Contact the manufacturer",
    337: "Contact the installer",
    338: "Invalid",
    381: "Stop",
    402: "Phases L1 and L2 (phsAB)",
    403: "Phases L1 and L3 (phsAC)",
    404: "Phases L2 and L3 (phsBC)",
    433: "Contant voltage",
    455: "Warning",
    461: "SMA",
    887: "No recommended action",
    1041: "leading / overexcited",
    1042: "lagging / underexcited",
    1069: "Reactive power / voltage characteristic curve Q(V)",
    1070: "Reactive power Q, direct setpoint",
    1071: "Reactive power const. Q (kVAr)",
    1072: "Q specified by PV system control",
    1073: "Reactive power Q(P)",
    1074: "cos φ, direct setpoint",
    1075: "cos φ, setpoint via system control",
    1076: "cos φ(P) characteristic curve",
    1077: "Active power limitation P (W)",
    1078: "Active power limitation P (%) of PMAX",
    1079: "Active power limitation P via system control",
    1129: "Yes",
    1130: "No",
    1264: "Full dynamic grid support",
    1265: "Limited dynamic grid support",
    1387: "Reactive power Q, setpoint via analog input",
    1388: "cos φ, setpoint via analog input",
    1389: "Reactive power / voltage characteristic curve Q(U) with hysteresis and deadband",
    1390: "Active power limitation P via analog input",
    1391: "Active power limitation P via digital inputs",
    1392: "Errors",
    1393: "Wait for PV voltage",
    1394: "Wait for valid AC grid",
    1395: "DC area",
    1396: "AC grid",
    1438: "Automatic",
    1455: "Emergency stop",
    1466: "Waiting",
    1467: "Starting",
    1468: "MPP search",
    1469: "Shutdown",
    1470: "Event message",
    1471: "Warning/error e-mail OK",
    1472: "Warning/error e-mail not OK",
    1473: "System info Parameter.Nameplate.Modele-mail OK",
    1474: "System info e-mail not OK",
    1475: "Error e-mail OK",
    1476: "Error e-mail not OK",
    1477: "Warning e-mail OK",
    1478: "Warning e-mail not OK",
    1479: "Wait after grid interruption",
    1480: "Wait for electric utility company",
    1749: "Full Stop",
    # 2055: "Status digital inlet: DI1",
    # 2056: "Status digital inlet: DI1, DI2",
    # 2057: "Status digital inlet: DI1, DI2, DI3",
    # 2058: "Status digital inlet: DI1, DI2, DI3, DI4",
    # 2059: "Status digital inlet: DI1, DI2, DI4",
    # 2060: "Status digital inlet: DI1, DI3",
    # 2061: "Status digital inlet: DI1, DI3, DI4",
    # 2062: "Status digital inlet: DI1, DI4",
    # 2063: "Status digital inlet: DI2",
    # 2064: "Status digital inlet: DI2, DI3",
    # 2065: "Status digital inlet: DI2, DI3, DI4",
    # 2066: "Status digital inlet: DI2, DI4",
    # 2067: "Status digital inlet: DI3",
    # 2068: "Status digital inlet: DI3, DI4",
    # 2069: "Status digital inlet: DI4",
    2270: "cos φ or Q specification through optimum PV system control",
    2506: "Values maintained",
    2507: "Apply fallback values",
    4354: "Maximum active power export",
    4405: "Maximum active power WMax",
    4406: "Maximum reactive power VArMax",
    4433: "Zero at dead band boundary",
    4434: "Zero at origin (ZerAtZer)",
    4443: "Current power",
    4444: "Potential power",
    4450: "Q limitation",
    4562: "cos φ(V) charac. curve",
    4520: "Mean value of the phase voltages",
    4521: "Maximum phase voltage",
    4718: "Boost Charging", # EV-Charger
    4950: "Smart Chargig", # EV-Charger
    5169: "Station locked", # EV-Charger
    5249: "Potential power with characteristic curve break",



    # DevClass
    8001: "Solar Inveters",
    8008: "SMAEVCharger",

    9492: "STP-12-50",
    9484: "EVC22-3AC-10",


    200111: "Not connected", # EV-Charger
    200112: "Sleep Mode", # EV-Charger
    200113: "Active Mode", # EV-Charger

    16777213: "Information not available",
}

ennexosSensorProfiles = {
    "Sunny Tripower X ": [
        Sensor("Coolsys.Inverter.TmpVal.1", Identifier.temp_a, factor=1, unit="°C"),
        Sensor("Coolsys.Inverter.TmpVal.2", Identifier.temp_b, factor=1, unit="°C"),
        Sensor("Coolsys.Inverter.TmpVal.3", Identifier.temp_c, factor=1, unit="°C"),
        Sensor("DcMs.Amp.1", Identifier.pv_current_a, factor=1, unit="A"),
        Sensor("DcMs.Amp.2", Identifier.pv_current_b, factor=1, unit="A"),
        Sensor("DcMs.Amp.3", Identifier.pv_current_c, factor=1, unit="A"),
        Sensor("DcMs.TotDcEnCntWh.1", None, factor=1, unit=None), # Energy released by string [A]
        Sensor("DcMs.TotDcEnCntWh.2", None, factor=1, unit=None),
        Sensor("DcMs.TotDcEnCntWh.3", None, factor=1, unit=None),
        Sensor("DcMs.Vol.1", Identifier.pv_voltage_a, factor=1, unit="V"),
        Sensor("DcMs.Vol.2", Identifier.pv_voltage_b, factor=1, unit="V"),
        Sensor("DcMs.Vol.3", Identifier.pv_voltage_c, factor=1, unit="V"),
        Sensor("DcMs.Watt.1", Identifier.pv_power_a, factor=1, unit="W"),
        Sensor("DcMs.Watt.2", Identifier.pv_power_b, factor=1, unit="W"),
        Sensor("DcMs.Watt.3", Identifier.pv_power_c, factor=1, unit="W"),
        Sensor("GridGuard.Cntry", None, factor=1, unit=None), # Country standard set
        Sensor("GridMs.A.phsA", Identifier.current_l1, factor=1, unit="A"),
        Sensor("GridMs.A.phsB", Identifier.current_l2, factor=1, unit="A"),
        Sensor("GridMs.A.phsC", Identifier.current_l3, factor=1, unit="A"),
        Sensor("GridMs.GriTyp", None, factor=1, unit=None), # Measurement.GridMs.GriTyp
        Sensor("GridMs.Hz", Identifier.frequency, factor=1, unit="Hz"),
        Sensor("GridMs.PhV.phsA", Identifier.voltage_l1, factor=1, unit="V"),
        Sensor("GridMs.PhV.phsA2B", None, factor=1, unit=None), # Grid voltage phase L1 against L2
        Sensor("GridMs.PhV.phsB", Identifier.voltage_l2, factor=1, unit="V"),
        Sensor("GridMs.PhV.phsB2C", None, factor=1, unit=None), # Grid voltage phase L2 against L3
        Sensor("GridMs.PhV.phsC", Identifier.voltage_l3, factor=1, unit="V"),
        Sensor("GridMs.PhV.phsC2A", None, factor=1, unit=None), # Grid voltage phase L3 against L1
        Sensor("GridMs.TotA", Identifier.current_total, factor=1, unit="A"),
        Sensor("GridMs.TotPFEEI", None, factor=1, unit=None),  # EEI displacement power factor
        Sensor("GridMs.TotPFExt", None, factor=1, unit=None), # Excitation type of cos φ
        Sensor("GridMs.TotPFPrc", None, factor=1, unit=None), # Displacement power factor
        Sensor("GridMs.TotVA", Identifier.grid_apparent_power, factor=1, unit="VA"),
        Sensor("GridMs.TotVAr", Identifier.grid_reactive_power, factor=1, unit="var"),
        Sensor("GridMs.TotW", Identifier.grid_power, factor=1, unit="W"),
        Sensor("GridMs.TotW.Pv", Identifier.pv_power, factor=1, unit="W"),
        Sensor("GridMs.VA.phsA", Identifier.grid_apparent_power_l1, factor=1, unit="VA"),
        Sensor("GridMs.VA.phsB", Identifier.grid_apparent_power_l2, factor=1, unit="VA"),
        Sensor("GridMs.VA.phsC", Identifier.grid_apparent_power_l3, factor=1, unit="VA"),
        Sensor("GridMs.VAr.phsA", Identifier.grid_reactive_power_l1, factor=1, unit="var"),
        Sensor("GridMs.VAr.phsB", Identifier.grid_reactive_power_l2, factor=1, unit="var"),
        Sensor("GridMs.VAr.phsC", Identifier.grid_reactive_power_l3, factor=1, unit="var"),
        Sensor("GridMs.W.phsA", Identifier.power_l1, factor=1, unit="W"),
        Sensor("GridMs.W.phsB", Identifier.power_l2, factor=1, unit="W"),
        Sensor("GridMs.W.phsC", Identifier.power_l3, factor=1, unit="W"),
        Sensor("InOut.GI1", None, factor=1, unit=None), # Digital group input
        Sensor("Inverter.VArModCfg.PFCtlVolCfg.Stt", None, factor=1, unit=None),
        Sensor("Isolation.FltA", Identifier.insulation_residual_current, factor=1000, unit="mA"),
        Sensor("Isolation.LeakRis", None, factor=1, unit="kOhm"), # TODO "pv_isolation_resistance"
        Sensor("Metering.TotFeedTms", None, factor=1, unit=None), 
        Sensor("Metering.TotOpTms", None, factor=1, unit=None),
        Sensor("Metering.TotWhOut", Identifier.total_yield, factor=1000, unit="kWh"),
        Sensor("Metering.TotWhOut.Pv", Identifier.pv_gen_meter, factor=1000, unit="kWh"),
        Sensor("Operation.BckStt", None, factor=1, unit=None),
        Sensor("Operation.DrtStt", None, factor=1, unit=None),
        Sensor("Operation.Evt.Dsc", None, factor=1, unit=None),
        Sensor("Operation.Evt.EvtNo", None, factor=1, unit=None),
        Sensor("Operation.Evt.Msg", None, factor=1, unit=None),
        Sensor("Operation.EvtCntIstl", None, factor=1, unit=None),
        Sensor("Operation.EvtCntUsr", None, factor=1, unit=None),
        Sensor("Operation.GriSwCnt", None, factor=1, unit=None),
        Sensor("Operation.GriSwStt", None, factor=1, unit=None),
        Sensor("Operation.Health", Identifier.status, factor=1, unit=None, mapper=ennexMapper),
        Sensor("Operation.HealthStt.Alm", None, factor=1, unit=None),
        Sensor("Operation.HealthStt.Ok", None, factor=1, unit=None),
        Sensor("Operation.HealthStt.Wrn", None, factor=1, unit=None),
        Sensor("Operation.OpStt", None, factor=1, unit=None),
        Sensor("Operation.PvGriConn", None, factor=1, unit=None),
        Sensor("Operation.RstrLokStt", None, factor=1, unit=None),
        Sensor("Operation.RunStt", None, factor=1, unit=None),
        Sensor("Operation.StandbyStt", None, factor=1, unit=None),
        Sensor("Operation.VArCtl.VArModAct", None, factor=1, unit=None),
        Sensor("Operation.VArCtl.VArModStt", None, factor=1, unit=None),
        Sensor("Operation.WMaxLimSrc", None, factor=1, unit=None),
        Sensor("Operation.WMinLimSrc", None, factor=1, unit=None),
        Sensor("PvGen.PvW", None, factor=1, unit=None), #  PV generation power
        Sensor("PvGen.PvWh", None, factor=1, unit=None), # Meter count and PV gen. meter
        Sensor("Spdwr.ComSocA.Stt", None, factor=1, unit=None), # Speedwire connection status of SMACOM A
        Sensor("SunSpecSig.SunSpecTx.1", None, factor=1, unit=None), #SunSpec life sign [1]
        Sensor("Upd.Stt", None, factor=1, unit=None),
        Sensor("WebConn.Stt", None, factor=1, unit=None), #  Status of the Webconnect functionality
        Sensor("Wl.AcqStt", None, factor=1, unit=None), # Status of WiFi scan
        Sensor("Wl.AntMod", None, factor=1, unit=None), #  WiFi antenna type
        Sensor("Wl.ConnStt", None, factor=1, unit=None), # WiFi connection status
        Sensor("Wl.SigPwr", None, factor=1, unit=None), # Signal strength of the selected network
        Sensor("Wl.SoftAcsConnStt", None, factor=1, unit=None), #Soft Access Point status
        Sensor("Setpoint.PlantControl.InOut.GO1", None, factor=1, unit=None)
    ],
    "SMA EV Charger ": [
        Sensor("ChaSess.WhIn", None, factor=1, unit=None), # charging_session_energy
        Sensor("Chrg.ModSw", None, factor=1, unit=None, mapper=ennexMapper), # position_of_rotary_switch 4950 or 4718
        Sensor("GridMs.A.phsA", Identifier.current_l1, factor=1, unit="A"), #Netzstrom Phase L1
        Sensor("GridMs.A.phsB", Identifier.current_l2, factor=1, unit="A"),
        Sensor("GridMs.A.phsC", Identifier.current_l3, factor=1, unit="A"),
        Sensor("GridMs.Hz", Identifier.frequency, factor=1, unit="Hz"),
        Sensor("GridMs.PhV.phsA", Identifier.voltage_l1, factor=1, unit="V"),#Netzspannung Phase L1
        Sensor("GridMs.PhV.phsB", Identifier.voltage_l2, factor=1, unit="V"),
        Sensor("GridMs.PhV.phsC", Identifier.voltage_l3, factor=1, unit="V"),
        Sensor("GridMs.TotPF", None, factor=1, unit=None),
        Sensor("GridMs.TotVA", Identifier.grid_apparent_power, factor=1, unit="VA"),
        Sensor("GridMs.TotVAr", Identifier.grid_reactive_power, factor=1, unit="var"),
        Sensor("InOut.GI1", None, factor=1, unit=None),
        Sensor("Metering.GridMs.TotWIn", Identifier.metering_power_absorbed, factor=1, unit="W"), #
        Sensor("Metering.GridMs.TotWIn.ChaSta", None, factor=1, unit=None), # same as Metering.GridMs.TotWIn
        Sensor("Metering.GridMs.TotWhIn", Identifier.metering_total_absorbed, factor=1, unit="Wh"), # charging_station_meter_reading
        Sensor("Metering.GridMs.TotWhIn.ChaSta", None, factor=1, unit=None), # same as Metering.GridMs.TotWhIn 
        Sensor("Operation.EVeh.ChaStt", Identifier.operating_status, factor=1, unit=None, mapper=ennexMapper), # charging_session_status
        Sensor("Operation.EVeh.Health", Identifier.status, factor=1, unit=None, mapper=ennexMapper), 
        Sensor("Operation.Evt.Msg", None, factor=1, unit=None),
        Sensor("Operation.Health", None, factor=1, unit=None), # same as EVeh.Health?
        Sensor("Operation.WMaxLimNom", None, factor=1, unit=None),
        Sensor("Operation.WMaxLimSrc", None, factor=1, unit=None),
        Sensor("Wl.AcqStt", None, factor=1, unit=None),
        Sensor("Wl.ConnStt", None, factor=1, unit=None),
        Sensor("Wl.SigPwr", None, factor=1, unit=None),
        Sensor("Wl.SoftAcsConnStt", None, factor=1, unit=None),
    ]
}
