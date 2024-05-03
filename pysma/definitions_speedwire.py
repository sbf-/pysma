# based on https://github.com/Wired-Square/sma-query/blob/main/src/sma_query_sw/commands.py
# improved with https://github.com/mhop/fhem-mirror/blob/master/fhem/FHEM/76_SMAInverter.pm  

from .const import Identifier
from .sensor import Sensor
from .const import SMATagList

commands = {
    "login": {"command": 0xFFFD040C, 
              "response": 0xFFFD040D,
              "first": 0x0030CB00,
              "last": 0x0030CB00,
              "registers": [
                    {"name": "susyid", "format": "H", "offset": 20},
                    {"name": "serial", "format": "uint","offset": 22},
                    {"name": "pkt_ID", "format": "H","offset": 40},
                    {"name": "cmdid", "format": "H","offset": 42},
                    {"name": "error", "format": "uint","offset": 36},
                ]   
              },
    "logoff": {"command": 0xFFFD010E, "response": 0xFFFD010F},
    "TypeLabel": {
        "command": 0x58000200,
        "response": 0x00821E00,
        "first": 0x00821E00,
        "last": 0x008220FF,
        "registers": [
            {"name": "inverter_class", "offset": 102, "mask": 0x00FFFFFF},
            {"name": "inverter_type", "format": "list", "offset": 142},
        ],
    },
    "EnergyProduction": {
        "command": 0x54000200,
        "response": 0x00260100,
        "first": 0x00260100,
        "last": 0x002622FF,
    },
    "PVEnergyProduction": {
        "command": 0x54000200,
        "response": 0x0046C300,
        "first": 0x0046C300,
        "last": 0x0046C3FF,
    },
    "SpotDCPower": {
        "command": 0x53800200,
        "response": 0x00251E00,
        "first": 0x00251E00,
        "last": 0x00251EFF,
        "registers": [
            {"name": "spot_dc_power1", "format": "int", "offset": 62,
                     "sensor": Sensor("spot_dc_power1", Identifier.pv_power_a, factor=1, unit="W"),

             },
            {"name": "spot_dc_power2", "format": "int","offset": 90, 
                     "sensor": Sensor("spot_dc_power2", Identifier.pv_power_b, factor=1, unit="W"),
},
        ],
    },
    "SpotDCPower_3": {
        "command": 0x51000200,
        "response": 0x0046C200,
        "first": 0x0046C200,
        "last": 0x0046C2FF,
    },
    "SpotACPower": {
        "command": 0x51000200,
        "response": 0x00464000,
        "first": 0x00464000,
        "last": 0x004642FF,
    },
    "SpotACTotalPower": {
        "command": 0x51000200,
        "response": 0x00263F00,
        "first": 0x00263F00,
        "last": 0x00263FFF,
        "registers": [
            {
                "name": "SpotACTotalPower",
                "offset": 62,
                "format": "int",
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "SpotACTotalPower", Identifier.grid_power, factor=1, unit="W"
                ),
            }
        ],
    },
    "ChargeStatus": {
        "command": 0x51000200,
        "response": 0x00295A00,
        "first": 0x00295A00,
        "last": 0x00295AFF,
        "registers": [
            {
                "name": "ChargeStatus",
                "offset": 62,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "ChargeStatus", Identifier.battery_soc_total, unit="%"
                ),
            }
        ],
    },
    "SpotDCVoltage": {
        "command": 0x53800200,
        "response": 0x00451F00, #TODO 0x451F
        "first": 0x00451F00,
        "last": 0x004521FF,
        "registers": [
            {"name": "spot_dc_voltage1", "offset": 62, "sensor": Sensor("spot_dc_voltage1", Identifier.pv_voltage_a, factor=100, unit="V")},
            {"name": "spot_dc_voltage2", "offset": 90, "sensor": Sensor("spot_dc_voltage2", Identifier.pv_voltage_b, factor=100, unit="V")},
            {"name": "spot_dc_current1", "offset": 118, "sensor": Sensor("spot_dc_current1", Identifier.pv_current_a, factor=1000, unit="A")},
            {"name": "spot_dc_current2", "offset": 146, "sensor": Sensor("spot_dc_current2", Identifier.pv_current_b, factor=1000, unit="A")},
        ],
    },
    "SpotACVoltage": {
        "command": 0x51000200,
        "response": 0x00464800,
        "first": 0x00464800,
        "last": 0x004656FF,
    },
    "SpotACCurrent": {
        "command": 0x51000200,
        "response": 0x00465300,
        "first": 0x00465300,
        "last": 0x004655FF,
        "registers": [
            {
                "name": "SpotACCurrent_L1",
                "offset": 62,
                "format": "int",
                "sensor": Sensor(
                    "SpotACCurrent_L1", Identifier.current_l1, factor=1000, unit="A"
                ),
            },
            {
                "name": "SpotACCurrent_L2",
                "offset": 90,
                "format": "int",
                "sensor": Sensor(
                    "SpotACCurrent_L2", Identifier.current_l2, factor=1000, unit="A"
                ),
            },
            {
                "name": "SpotACCurrent_L3",
                "offset": 118,
                "format": "int",
                "sensor": Sensor(
                    "SpotACCurrent_L3", Identifier.current_l3, factor=1000, unit="A"
                ),
            },
        ],
    },
    "SpotACCurrentBackup": {
        "command": 0x51000200,
        "response": 0x40574600,
        "first": 0x40574600,
        "last": 0x405748FF,
    },
    # "BatteryInfo_TEMP": { ## TODO
    #     "command": 0x51000200,
    #     "response": 0x00495B00,
    #     "first": 0x00495B00,
    #     "last": 0x00495B10,
    # },
    "BatteryInfo_UDC": {
        "command": 0x51000200,
        "response": 0x00495C00,
        "first": 0x00495C00,
        "last": 0x00495C10,
        "registers": [
            {
                "name": "battery_voltage_a",
                "offset": 62,
                "sensor": Sensor(
                    "battery_voltage_a",
                    Identifier.battery_voltage_a,
                    unit="V",
                    factor=100,
                ),
            },
            {
                "name": "battery_voltage_b",
                "offset": 90,
                "sensor": Sensor(
                    "battery_voltage_b",
                    Identifier.battery_voltage_b,
                    unit="V",
                    factor=100,
                ),
            },
            {
                "name": "battery_voltage_c",
                "offset": 118,
                "sensor": Sensor(
                    "battery_voltage_c",
                    Identifier.battery_voltage_c,
                    unit="V",
                    factor=100,
                ),
            },
        ],
    },
    "BatteryInfo_IDC": {
        "command": 0x51000200,
        "response": 0x00495D00,
        "first": 0x00495D00,
        "last": 0x00495D10,
        "registers": [
            {
                "name": "battery_current_a",
                "format": "int",
                "offset": 62,
                "sensor": Sensor(
                    "battery_current_a",
                    Identifier.battery_current_a,
                    unit="A",
                    factor=1000,
                ),
            },
            {
                "name": "battery_current_b",
                "format": "int",
                "offset": 90,
                "sensor": Sensor(
                    "battery_current_b",
                    Identifier.battery_current_b,
                    unit="A",
                    factor=1000,
                ),
            },
            {
                "name": "battery_current_c",
                "offset": 118,
                "format": "int",
                "sensor": Sensor(
                    "battery_current_c",
                    Identifier.battery_current_c,
                    unit="A",
                    factor=1000,
                ),
            },
        ],
    },
    "BatteryInfo_Charge": {
        "command": 0x51000200,
        "response": 0x00496900,
        "first": 0x00496900,
        "last": 0x00496AFF,
        "registers": [
            {
                "name": "bat_p_charge",
                "offset": 62,
                "sensor": Sensor("bat_p_charge", Identifier.battery_power_charge_total, unit="W", factor=1)
            },
            {
                "name": "bat_p_discharge",
                "offset": 90,
                "sensor": Sensor("bat_p_discharge", Identifier.battery_power_discharge_total, unit="W", factor=1)
            },
        ],
    },
    "BatteryInfo_Capacity": {
        "command": 0x51000200,
        "response": 0x00696E00,
        "first": 0x00696E00,
        "last": 0x00696E10,
        "registers": [
            {
                "name": "BatteryInfo_Capacity",
                "offset": 62,
                "sensor": Sensor(
                    "BatteryInfo_Capacity", Identifier.battery_capacity_total, unit="%"
                ),
            }
        ],
    },
    "BatteryInfo": {
        "command": 0x51000200,
        "response": 0x00491E00,
        "first": 0x00491E00,
        "last": 0x00495DFF,
        "registers": [
            {
                "name": "TEMP BAT_CYCLES",
                "offset": 62,
                "sensor": Sensor(
                    "TEMP BAT_CYCLES", None, unit=None
                ),
            }
        ],
    },
    "BatteryInfo_3": {
        "command": 0x58020200,
        "response": 0x08822C00,
        "first": 0x08822C00,
        "last": 0x08822CFF,
    },
    "BatteryInfo_4": {
        "command": 0x58000200,
        "response": 0x00893700,
        "first": 0x00893700,
        "last": 0x008937FF,
        "registers": [
            {
                "name": "rated capacity",
                "offset": 78,
            },
        ],
    },
    "BatteryInfo_5": {
        "command": 0x58020200,
        "response": 0x00B18900,
        "first": 0x00B18900,
        "last": 0x00B189FF,
    },
    "SpotGridFrequency": {
        "command": 0x51000200,
        "response": 0x00465700,
        "first": 0x00465700,
        "last": 0x004657FF,
        "registers": [
            {
                "name": "grid_frequency",
                "offset": 62,
                "sensor": Sensor(
                    "grid_frequency", Identifier.frequency, factor=100, unit="Hz"
                ),
            }
        ],
    },
    "OperationTime": {
        "command": 0x54000200,
        "response": 0x00462E00,
        "first": 0x00462E00,
        "last": 0x00462FFF,
        "registers": [
            {
                "name": "OperationTime + OperationTime2",
                "offset": 62,
            }
        ],

    },
    "InverterTemperature": {
        "command": 0x52000200,
        "response": 0x00237700,
        "first": 0x00237700,
        "last": 0x002377FF,
        "format": "int",
        "registers": [
            {"name": "InverterTemperature", "offset": 62, "invalid": 0x80000000}
        ],
    },
    "MaxACPower": {
        "command": 0x51000200,
        "response": 0x00411E00,
        "first": 0x00411E00,
        "last": 0x004120FF,
        "registers": [
            {
                "name": "MaxACPower1",
                "offset": 62,
                "invalid": 0x80000000,
            },
            {
                "name": "MaxACPower2",
                "offset": 90,
                "invalid": 0x80000000,
            },
            {
                "name": "MaxACPower3",
                "offset": 118,
                "invalid": 0x80000000,
            },
        ],
    },
    "MaxACPower2": {
        "command": 0x51000200,
        "response": 0x00832A00,
        "first": 0x00832A00,
        "last": 0x00832AFF,
    },
    "GridRelayStatus": {
        "command": 0x51800200,
        "response": 0x00416400,
        "first": 0x00416400,
        "last": 0x004164FF,
        "registers": [
            {"name": "grid_relay_status", "format": "list", "offset": 62, "invalid": 0x80000000,
             "sensor":  Sensor("GridRelayStatus", Identifier.grid_relay_status, unit=None, mapper = SMATagList)}
        ],
    },
    "BackupRelayStatus": {
        "command": 0x51800200,
        "response": 0x08412500,
        "first": 0x08412500,
        "last": 0x084125FF,
    },
    "GridConection": {
        "command": 0x51800200,
        "response": 0x0046A600,
        "first": 0x0046A600,
        "last": 0x0046A6FF,
         "registers": [
             {"name": "GridConection", "format": "list", "offset": 62},
         ],
    },
    "OperatingStatus": {
        "command": 0x51800200,
        "response": 0x08412B00,
        "first": 0x08412B00,
        "last": 0x08412BFF,
    },
    "GeneralOperatingStatus": {
        "command": 0x51800200,
        "response": 0x00412800,
        "first": 0x00412800,
        "last": 0x004128FF,
        "registers": [
            {
                "name": "GeneralOperatingStatus", "format": "list", "offset": 62,
                "sensor":  Sensor(
                    "GeneralOperatingStatus", Identifier.operating_status_genereal, factor=1, unit=None, mapper = SMATagList
                )},
        ],
    },
    "WaitingTimeUntilFeedIn": {
        "command": 0x51000200,
        "response": 0x00416600,
        "first": 0x00416600,
        "last": 0x004166FF,
        "registers": [
            {"name": "WaitingTimeUntilFeedIn", "offset": 62, "invalid": 0x80000000}
        ],
    },
    "DeviceStatus": {
        "command": 0x51800200,
        "response": 0x00214800,
        "first": 0x00214800,
        "last": 0x002148FF,
        "registers": [
            {   
                "name": "inverter_status",
                "format": "list",
                "offset": 62,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "inverter_status", Identifier.status, factor=1, unit=None, mapper = SMATagList
                ),
            }
        ],
    },
    "SpotBatteryLoad": {
        "command": 0x54000200,
        "response": 0x00496700,
        "first": 0x00496700,
        "last": 0x004967FF,
        "registers": [
            {
                "name": "SpotBatteryLoad",
                "offset": 62,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "SpotBatteryLoad",
                    Identifier.battery_charge_total,
                    unit="kWh",
                    factor=1000,
                ),
            }
        ],
    },
    "SpotBatteryUnload": {
        "command": 0x54000200,
        "response": 0x00496800,
        "first": 0x00496800,
        "last": 0x004968FF,
        "registers": [
            {
                "name": "SpotBatteryUnLoad",
                "offset": 62,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "SpotBatteryUnLoad",
                    Identifier.battery_discharge_total,
                    unit="kWh",
                    factor=1000,
                ),
            }
        ],
    },
    "EM_1": {
        "command": 0x54000200,
        "response": 0x00462400,
        "first": 0x00462400,
        "last": 0x004628FF,
        "registers": [
            {
                "name": "meter_yield",
                "offset": 66,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "meter_yield",
                    Identifier.metering_total_yield,
                    unit="kWh",
                    factor=1000,
                ),
            },
            {
                "name": "meter_absorbed",
                "offset": 78,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "meter_absorbed",
                    Identifier.metering_total_absorbed,
                    unit="kWh",
                    factor=1000,
                ),
            }

        ],
    },
    "EM_2": {
        "command": 0x54000200,
        "response": 0x40469100,
        "first": 0x40469100,
        "last": 0x404692FF,
    },
    "EM_3": {
        "command": 0x51000200,
        # "response": 0x40463600,
        # "first":    0x40463600,
        # "last": 0x404637FF,
        "response": 0x00463600,
        "first":    0x00463600,
        "last": 0x004637FF,
        "registers": [
            {
                "name": "meter_yield3",
                "offset": 62,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "meter_yield3",
                    Identifier.metering_power_supplied,
                    unit="W",
                    factor=1,
                ),
            },
            {
                "name": "meter_absorbed3",
                "offset": 90,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "meter_absorbed3",
                    Identifier.metering_power_absorbed,
                    unit="W",
                    factor=1,
                ),
            }

        ],
    },
    "EM_4": {
        "command": 0x51000200,
        "response": 0x0046E800,
        "first": 0x0046E800,
        "last": 0x0046EDFF,
    },
    "Insulation_1": {
        "command": 0x51020200,
        "response": 0x40254E00,
        "first": 0x40254E00,
        "last": 0x40254FFF,
    },
    "Insulation_2": {
        "command": 0x51020200,
        "response": 0x00254F00,
        "first": 0x00254F00,
        "last": 0x00254FFF,
    },
    "Firmware": {
        "command": 0x58000200,
        "response": 0x00823400,
        "first": 0x00823400,
        "last": 0x008234FF,
        "registers": [
            {
                "name": "Firmware",
                "format": "version",
                "offset": 78,
                "invalid": 0x80000000,
            }
        ],
    },
    "energy_production": {
        "command": 0x54000200,
        "response": 0x54000201,
        "first": 0x00260100, # TODO Check length
        "last": 0x002622FF,
        "registers": [

            {
                "name": "total",
                "offset": 62,
                "invalid": 0x8000000000000000,
                "sensor": Sensor(
                    "total", Identifier.total_yield, factor=1000, unit="kWh"
                ),
            },
            {
                "name": "today",
                "offset": 78,
                "invalid": 0x8000000000000000,
                "sensor": Sensor(
                    "today", Identifier.daily_yield, unit="Wh"
                ),
            },
        ],
        # $inv_SPOT_ETODAY,$inv_SPOT_ETOTAL
    },
    "spot_ac_power": {
        "command": 0x51000200,
        "response": 0x00464000,
        "first": 0x00464000,
        "last": 0x004642FF,
        "registers": [
            {
                "name": "spot_ac_power_l1",
                "offset": 62,
                "format": "int",
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "spot_ac_power1", Identifier.power_l1, factor=1, unit="W"
                ),
            },
            {
                "name": "spot_ac_power_l2",
                "offset": 90,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "spot_ac_power2", Identifier.power_l2, factor=1, unit="W"
                ),
            },
            {
                "name": "spot_ac_power_l3",
                "offset": 118,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "spot_ac_power3", Identifier.power_l3, factor=1, unit="W"
                ),
            },
        ],
    },
    "spot_ac_voltage": {
        "command": 0x51000200,
        "response": 0x00464800,
        "first": 0x00464800,
        "last": 0x004655FF,
        "registers": [
            {
                "name": "spot_ac_voltage1",
                "offset": 62,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "spot_ac_voltage1", Identifier.voltage_l1, factor=100, unit="V"
                ),
            },
            {
                "name": "spot_ac_voltage2",
                "offset": 90,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "spot_ac_voltage2", Identifier.voltage_l2, factor=100, unit="V"
                ),
            },
            {
                "name": "spot_ac_voltage3",
                "offset": 118,
                "invalid": 0x80000000,
                "sensor": Sensor(
                    "spot_ac_voltage3", Identifier.voltage_l3, factor=100, unit="V"
                ),
            },
            # {
            #     "name": "spot_ac_current1",
            #     "offset": 146,
            #     "invalid": 0x80000000,
            #     "format": "int",
            #     "sensor": Sensor(
            #         "spot_ac_current1", Identifier.current_l1, factor=100, unit="A"
            #     ),
            # },
            # {
            #     "name": "spot_ac_current2",
            #     "offset": 174,
            #     "invalid": 0x80000000,
            #     "format": "int",
            #     "sensor": Sensor(
            #         "spot_ac_current2", Identifier.current_l2, factor=100, unit="A"
            #     ),
            # },
            # {
            #     "name": "spot_ac_current3",
            #     "offset": 202,
            #     "invalid": 0x80000000,
            #     "format": "int",
            #     "sensor": Sensor(
            #         "spot_ac_current3", Identifier.current_l3, factor=100, unit="A"
            #     ),
            # },
        ],
    },
}
