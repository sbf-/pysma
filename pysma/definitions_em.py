"""Definition for Speedwire-Energy Meter
"""

from .const import Identifier
from .sensor import Sensor

obis2sensor = [
    Sensor(
        "1:4:0", Identifier.metering_power_absorbed, factor=10, unit="W"
    ),  # p consume
    Sensor("1:8:0", Identifier.metering_total_absorbed, factor=3600000, unit="kWh"),
    Sensor(
        "2:4:0", Identifier.metering_power_supplied, factor=10, unit="W"
    ),  # p supply
    Sensor(
        "2:8:0",
        Identifier.metering_total_yield,
        factor=3600000,
        unit="kWh",
    ),
    Sensor("3:4:0", None),  # q consume
    Sensor("3:8:0", None),
    Sensor("4:4:0", None),  # q supply
    Sensor("4:8:0", None),
    Sensor("9:4:0", None),  # s consume
    Sensor("9:8:0", None),
    Sensor("10:4:0", None),  # s supply
    Sensor("10:8:0", None),
    Sensor("13:4:0", None),  # cospi
    Sensor("14:4:0", Identifier.metering_frequency, factor=1000, unit="Hz"),  # freq
    # Phase 1
    Sensor("21:4:0", Identifier.metering_active_power_draw_l1, factor=10, unit="W"),
    Sensor("21:8:0", None),
    Sensor("22:4:0", Identifier.metering_active_power_feed_l1, factor=10, unit="W"),
    Sensor("22:8:0", None),
    Sensor("23:4:0", None),
    Sensor("23:8:0", None),
    Sensor("24:4:0", None),
    Sensor("24:8:0", None),
    Sensor("29:4:0", None),
    Sensor("29:8:0", None),
    Sensor("30:4:0", None),
    Sensor("30:8:0", None),
    Sensor("31:4:0", Identifier.metering_current_l1, factor=1000, unit="A"),
    Sensor("32:4:0", Identifier.metering_voltage_l1, factor=1000, unit="V"),
    Sensor("33:4:0", None),  # cosphi1
    # Phase 2
    Sensor("41:4:0", Identifier.metering_active_power_draw_l2, factor=10, unit="W"),
    Sensor("41:8:0", None),
    Sensor("42:4:0", Identifier.metering_active_power_feed_l2, factor=10, unit="W"),
    Sensor("42:8:0", None),
    Sensor("43:4:0", None),
    Sensor("43:8:0", None),
    Sensor("44:4:0", None),
    Sensor("44:8:0", None),
    Sensor("49:4:0", None),
    Sensor("49:8:0", None),
    Sensor("50:4:0", None),
    Sensor("50:8:0", None),
    Sensor("51:4:0", Identifier.metering_current_l2, factor=1000, unit="A"),
    Sensor("52:4:0", Identifier.metering_voltage_l2, factor=1000, unit="V"),
    Sensor("53:4:0", None),
    # Phase 3
    Sensor("61:4:0", Identifier.metering_active_power_draw_l3, factor=10, unit="W"),
    Sensor("61:8:0", None),
    Sensor("62:4:0", Identifier.metering_active_power_feed_l3, factor=10, unit="W"),
    Sensor("62:8:0", None),
    Sensor("63:4:0", None),
    Sensor("63:8:0", None),
    Sensor("64:4:0", None),
    Sensor("64:8:0", None),
    Sensor("69:4:0", None),
    Sensor("69:8:0", None),
    Sensor("70:4:0", None),
    Sensor("70:8:0", None),
    Sensor("71:4:0", Identifier.metering_current_l3, factor=1000, unit="A"),
    Sensor("72:4:0", Identifier.metering_voltage_l3, factor=1000, unit="V"),
    Sensor("73:4:0", None),
]
