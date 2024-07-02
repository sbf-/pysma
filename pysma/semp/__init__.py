import random
import uuid
from datetime import datetime
from typing import Awaitable, Callable, Union
from zoneinfo import ZoneInfo

from pysmaplus.semp.const import callbackAction

from .device import sempDevice
from .SEMPhttpd import SEMPhttpServer
from .ssdp import async_create_upnp_datagram_endpoint


class semp:
    def __init__(
        self,
        ip: str,
        port: int,
        timezone: ZoneInfo | None = None,
        callback: Callable[[callbackAction], Awaitable[None]] | None = None,
    ):
        self.ip = ip
        self.port = port
        self.uuid = self.getUUID()
        self.http = SEMPhttpServer(self.ip, self.port, self.uuid, timezone, callback)

    def getUUID(self) -> str:
        """Generate a UUID based on the IP and the used port"""
        rnd = random.Random()
        rnd.seed(self.ip + str(self.port))
        return str(uuid.UUID(int=rnd.getrandbits(128), version=4))

    async def start(self):
        await self.http.start()
        await async_create_upnp_datagram_endpoint(
            self.ip, True, self.ip, self.port, self.uuid
        )

    def addDevice(self, dev: sempDevice):
        self.http.addDevice(dev)

    def removeDevice(self, dev: Union[str | sempDevice]):
        if isinstance(dev, sempDevice):
            self.http.removeDevice(dev.deviceId)
        else:
            self.http.removeDevice(dev)

    def getDevice(self, deviceId: Union[str | sempDevice]) -> sempDevice:
        if isinstance(deviceId, sempDevice):
            return self.getDevice(deviceId.deviceId)
        return self.http.getDevice(deviceId)

    def getStatus(self) -> str:
        if len(self.http.history) == 0:
            return "Not Connected"
        r = self.http.history[-1]
        diff = datetime.now().timestamp() - r.timemsec
        if diff < 130:
            return "Connected"
        return "Connection lost"
