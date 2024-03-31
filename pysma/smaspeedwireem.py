import socket
import struct
import asyncio
import copy
import logging
import binascii
from typing import Any, Dict, Optional

# https://www.unifox.at/software/sma-em-daemon/
# https://cdn.sma.de/fileadmin/content/www.developer.sma.de/docs/EMETER-Protokoll-TI-en-10.pdf?v=1699276024


from .sensor import Sensor
from .const import Identifier

from .exceptions import (
    SmaConnectionException,
    SmaReadException,
)
from .helpers import version_int_to_string
from .sensor import Sensors
from .device import Device

obis2sensor= [
    Sensor("1:4:0", Identifier.metering_power_absorbed, factor=10, unit="W"), # p consume
    Sensor("1:8:0", Identifier.metering_total_absorbed, factor=3600000, unit="kWh"),
    Sensor("2:4:0", Identifier.metering_power_supplied, factor=10, unit="W"), # p supply
    Sensor("2:8:0", Identifier.metering_total_yield, factor=3600000, unit="kWh", ),
    Sensor("3:4:0", None), # q consume
    Sensor("3:8:0", None),
    Sensor("4:4:0", None), # q supply
    Sensor("4:8:0", None),
    Sensor("9:4:0", None), # s consume
    Sensor("9:8:0", None),
    Sensor("10:4:0", None), # s supply
    Sensor("10:8:0", None),
    Sensor("13:4:0", None), # cospi
    Sensor("14:4:0", Identifier.metering_frequency, factor=1000, unit="Hz"), # freq

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
    Sensor("33:4:0", None), #cosphi1

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
    Sensor("73:4:0", None)
]


_LOGGER = logging.getLogger(__name__)
class SMAspeedwireEM(Device):
    """Class to connect to the ennexos based SMA inverters. (e.g. Tripower X Devices)"""
    _sock: socket
    _susyid: Dict[int, Any] = {270: "Energy Meter", 349: "Energy Meter 2", 372: "Sunny Home Manager 2"}

    def __init__(self):
        """Init SMA connection.

        Args:
            session (ClientSession): aiohttp client session
            url (str): Url or IP address of device
            password (str, optional): Password to use during login.
            group (str, optional): Username to use during login. 

        """
        pass



    async def new_session(self) -> bool:
        """Establish a new session.

        Returns:
            bool: authentication successful
        """
        MCAST_GRP = '239.12.255.254'
        MCAST_PORT = 9522
        IPBIND = '0.0.0.0'

        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("", MCAST_PORT))
        try:
            mreq = struct.pack("4s4s", socket.inet_aton(MCAST_GRP), socket.inet_aton(IPBIND))
            self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except BaseException as exc:
            raise SmaConnectionException(
                f"Could not start multicast"
            ) from exc


        return True


    async def get_sensors(self) -> Sensors:
        """Get the sensors that are present on the device.

        Returns:
            Sensors: Sensors object containing Sensor objects
        """
        device_sensors = Sensors()

        for s in obis2sensor:
            if s.name is not None:
                device_sensors.add(copy.copy(s)) 

        return device_sensors


    async def close_session(self) -> None:
        """Close the session login."""
        # TODO
        pass



    async def read(self, sensors: Sensors) -> bool:
        """Read a set of keys.

        Args:
            sensors (Sensors): Sensors object containing Sensor objects to read

        Returns:
            bool: reading was successful
        """
        notfound = []
        for i in range(0,4):
            data=self._decode(self._sock.recv(608))
            if data:
                break
        # TODO raise SmaConnectionException or SmaReadException if no connection after 4 tries
            
        for sensor in sensors:
          if (sensor.key in data):
              value = data[sensor.key]
              if (sensor.factor):
                  value /= sensor.factor
              sensor.value = value
          else:
              notfound.append(sensor.key)

        if notfound:
            _LOGGER.info(
                "No values for sensors: %s",
                ",".join(notfound),
            )

        return True


    async def device_info(self) -> dict:
        """Read device info and return the results.

        Returns:
            dict: dict containing serial, name, type, manufacturer and sw_version
        """
        for i in range(0,4):
            data=self._decode(self._sock.recv(608))
            if data:
                break
        device_info = {
            "serial": data["serial"],
            "name": data["device"],
            "type": data["susyid"],
            "manufacturer": "SMA",
            "sw_version": data["sw_version"],
        }
        return device_info

    def _decode(self, p : bytes):
        """Decode a Speedwire-Packet

        Args:
            p: Network-Packet

        Returns:
            dict: Dict with all the decoded information
        """
        if p[0:4] != b"SMA\0":
            return None
        protocolID = int.from_bytes(p[16:18], byteorder="big")
        if (protocolID != 0x6069):
            _LOGGER.debug("Unknown protocoll " + str(protocolID))
            return None
        
        data = {}
        data["protocolID"] = protocolID
        data["susyid"] = int.from_bytes(p[18:20], byteorder="big")
        data["device"] = self._susyid.get(data["susyid"], "unknown")
        data["serial"] = int.from_bytes(p[20:24], byteorder="big")

        length = int.from_bytes(p[12:14], byteorder="big") + 16
        pos = 28
        while pos < length:
            value = None
            mchannel = int.from_bytes(p[pos: pos + 1], byteorder="big")
            mvalueindex = int.from_bytes(p[pos + 1: pos + 2], byteorder="big")
            mtyp = int.from_bytes(p[pos + 2: pos + 3], byteorder="big")
            mtariff = int.from_bytes(p[pos + 3: pos + 4], byteorder="big")
            obis = f'{mvalueindex}:{mtyp}:{mtariff}'
            if mtyp in [4,8]:
                # 4 actucal / current => 8 Bytes
                # 8 counter / sum => 12 Bytes
                value = int.from_bytes(p[pos + 4 : pos + 4 + mtyp], byteorder="big")
                pos += 4 + mtyp
            elif mchannel == 144 and mtyp == 0:
                value = f"{p[pos + 4]}.{p[pos + 5]}.{p[pos + 6]}.{chr(p[pos + 7])}"
                obis= "sw_version"
                pos += 4 + 4
            else:
                _LOGGER.debug("Unknown packet in speedwire: " + str(mchannel) + " " + str(mvalueindex) + " " + str(mtyp) + " " + str(mtariff))
                pos += 4 + 4
            data[obis] = value
        return data
