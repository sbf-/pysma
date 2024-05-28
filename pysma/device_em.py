"""Interface for SMA Energy Meters and Sunny Home Manager 2 (SHM2)

see https://www.unifox.at/software/sma-em-daemon/
see https://cdn.sma.de/fileadmin/content/www.developer.sma.de/docs/EMETER-Protokoll-TI-en-10.pdf

"""

import asyncio
import base64
import copy
import logging
import socket
import struct
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List

from .const import SMATagList
from .definitions_em import obis2sensor
from .definitions_speedwire import speedwireHeader, speedwireHeader6069
from .device import Device, DiscoveryInformation
from .exceptions import SmaConnectionException, SmaReadException
from .sensor import Sensor, Sensors

_LOGGER = logging.getLogger(__name__)


@dataclass
class Debug_information_em:
    """Struct to store debug Information"""

    serial: set[int] = field(default_factory=set)
    protocol: set[str] = field(default_factory=lambda: set())
    last_packet: bytes | None = None
    last_data: dict[str, Any] | None = None
    last_valid_packet: bytes | None = None


class SMAspeedwireEM(Device):
    """Class for the detection of SMA Devices in the local network."""

    def __init__(self) -> None:
        """init"""
        self.loop = asyncio.get_event_loop()
        self._transport: asyncio.BaseTransport | None = None
        self._protocol: SMAspeedwireEM | None = None
        self.transport: asyncio.BaseTransport | None = None
        self._data_received: asyncio.Future | None = None
        self.di = Debug_information_em()

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

    async def new_session(self) -> bool:
        """Starts a new session"""
        sock = self._getDiscoverySocket()
        on_connection_lost = self.loop.create_future()
        self._transport, self._protocol = await self.loop.create_datagram_endpoint(
            lambda: self,  # type: ignore[type-var]
            sock=sock,
        )
        data = None
        try:
            data = await self._get_next_values()
        except TimeoutError as e:
            raise SmaConnectionException("No speedwire packet received!") from e
        if not data:
            raise SmaReadException("No usable data received!")
        return True

    async def _get_next_values(self, timeout: float = 2) -> dict:
        """Returns the next values received from the device."""
        self._data_received = asyncio.get_running_loop().create_future()
        await asyncio.wait_for(self._data_received, timeout=timeout)
        data = self._data_received.result()
        self._data_received = None
        return data

    async def device_info(self) -> dict:
        """Read device info and return the results.

        Returns:
            dict: dict containing serial, name, type, manufacturer and sw_version
        """
        data = await self._get_next_values()
        device_info = {
            "serial": data["serial"],
            "name": data["device"],
            "type": data["susyid"],
            "manufacturer": "SMA",
            "sw_version": data["sw_version"],
        }
        return device_info

    async def read(self, sensors: Sensors) -> bool:
        """Read a set of keys.

        Args:
            sensors (Sensors): Sensors object containing Sensor objects to read

        Returns:
            bool: reading was successful
        """
        notfound = []
        data = await self._get_next_values()
        for sensor in sensors:
            if sensor.key in data:
                value = data[sensor.key]
                if sensor.factor:
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

    async def close_session(self) -> None:
        """Closes the session"""
        if self._transport:
            self._transport.close()
        self._sock.close()

    async def detect(self, ip: str) -> List[DiscoveryInformation]:
        """Try to detect SMA devices"""
        discovered = []
        try:
            await self.new_session()
            start = time.time()
            while time.time() - start < 2.1:
                try:
                    data = await self._get_next_values()
                except TimeoutError:
                    continue
                if data["ip"].startswith(ip + ":"):
                    device = f'{data["device"]} ({data["serial"]})'
                    di = DiscoveryInformation(
                        data["ip"], "found", "speedwireem", None, "", device
                    )
                    if di not in discovered:
                        discovered.append(di)
        except (TimeoutError, SmaConnectionException):
            pass
        if len(discovered) == 0:
            discovered.append(
                DiscoveryInformation(
                    ip,
                    "failed",
                    "speedwireem",
                    None,
                    "no multicast packet received.",
                    "",
                )
            )
        return discovered

    async def get_debug(self) -> Dict[str, Any]:
        """Return a dict with all debug information."""
        debug_info = {
            "last_packet": (
                base64.b64encode(self.di.last_packet).decode("ascii")
                if self.di.last_packet is not None
                else ""
            ),
            "last_valid_packet": (
                base64.b64encode(self.di.last_valid_packet).decode("ascii")
                if self.di.last_valid_packet is not None
                else ""
            ),
            "last_data": self.di.last_data,
            "serial": list(self.di.serial),
            "protocol": list(self.di.protocol),
        }
        return debug_info

    def set_options(self, options: Dict[str, Any]) -> None:
        """Set options"""

    async def set_parameter(self, sensor: Sensor, value: int) -> None:
        """Set Parameters."""

    def _getDiscoverySocket(self) -> socket.socket:
        mcast_grp = "239.12.255.254"
        ipbind = "0.0.0.0"
        addrinfo = socket.getaddrinfo(mcast_grp, None)[0]
        self._sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("", 9522))
        try:
            mreq = struct.pack(
                "4s4s", socket.inet_aton(mcast_grp), socket.inet_aton(ipbind)
            )
            self._sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        except BaseException as exc:
            raise RuntimeError("Could not start multicast") from exc
        return self._sock

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Called if connection is made"""
        self.transport = transport

    def error_received(self, exc: Exception) -> None:
        """Called by error."""
        _LOGGER.error("%s error occurred: %s", type(exc), exc)

    def connection_lost(self, exc: Exception) -> None:
        """Called by connection lost."""
        _LOGGER.error("Socket closed, stop the event loop %s %s", type(exc), exc)

    def datagram_received(self, p: bytes, addr: tuple[str, int]) -> dict[str, Any]:
        """Decode a Speedwire-Packet

        Args:
            p: Network-Packet

        Returns:
            dict: Dict with all the decoded information
        """
        self.di.last_packet = p
        sw = speedwireHeader.from_packed(p[0:18])
        self.di.protocol.add(f"{sw.protokoll:04x}")
        if not sw.check6069():
            return {}
        sw6069 = speedwireHeader6069.from_packed(p[18:28])
        data: dict[str, Any] = {}
        data["protocolID"] = sw.protokoll
        data["susyid"] = sw6069.src_susyid
        data["device"] = SMATagList.get(data["susyid"], "unknown")
        data["serial"] = sw6069.src_serial
        data["ip"] = addr[0] + ":" + str(addr[1])
        length = sw.smanet2_length + 16
        pos = 28
        while pos < length:
            value: Any = None
            mchannel = int.from_bytes(p[pos : pos + 1], byteorder="big")
            mvalueindex = int.from_bytes(p[pos + 1 : pos + 2], byteorder="big")
            mtyp = int.from_bytes(p[pos + 2 : pos + 3], byteorder="big")
            mtariff = int.from_bytes(p[pos + 3 : pos + 4], byteorder="big")
            obis = f"{mvalueindex}:{mtyp}:{mtariff}"
            if mtyp in [4, 8]:
                # 4 actucal / current => 8 Bytes
                # 8 counter / sum => 12 Bytes
                value = int.from_bytes(p[pos + 4 : pos + 4 + mtyp], byteorder="big")
                pos += 4 + mtyp
            elif mchannel == 144 and mtyp == 0:
                value = f"{p[pos + 4]}.{p[pos + 5]}.{p[pos + 6]}.{chr(p[pos + 7])}"
                obis = "sw_version"
                pos += 4 + 4
            else:
                _LOGGER.debug(
                    "Unknown packet in speedwire: "
                    + str(mchannel)
                    + " "
                    + str(mvalueindex)
                    + " "
                    + str(mtyp)
                    + " "
                    + str(mtariff)
                )
                pos += 4 + 4
            data[obis] = value

        # Statistics & Co
        self.di.serial.add(data["serial"])
        self.di.last_valid_packet = p
        self.di.last_data = data
        if self._data_received is not None and not self._data_received.done():
            self._data_received.set_result(data)
        return data
