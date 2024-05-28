""" Speedwire Discovery  """

import asyncio
import logging
import socket
import struct

from .definitions_speedwire import speedwireHeader

_LOGGER = logging.getLogger(__name__)


class Discovery:
    """Class for the detection of SMA Devices in the local network."""

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        """init"""
        self.loop = loop
        self.transport: asyncio.BaseTransport
        self.addr = "239.12.255.254"
        self.port = 9522
        self.discovered: list[tuple[str, int]] = []

    def getDiscoverySocket(self) -> socket.socket:
        addrinfo = socket.getaddrinfo(self.addr, None)[0]
        sock = socket.socket(addrinfo[0], socket.SOCK_DGRAM)
        sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("@i", 1)
        )
        return sock

    async def run(self) -> list:
        """Start the Task"""
        sock = self.getDiscoverySocket()
        on_connection_lost = self.loop.create_future()
        connect = await self.loop.create_datagram_endpoint(
            lambda: self,  # type: ignore[type-var]
            sock=sock,
        )
        for i in range(0, 3):
            await asyncio.sleep(0.5)
            self.sendDiscoveryRequest()
        await asyncio.sleep(0.5)
        return self.discovered

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport
        self.sendDiscoveryRequest()

    def sendDiscoveryRequest(self) -> None:
        """Send a discovery Request"""
        _LOGGER.warn("Sending Discovery Request")
        self.transport.sendto(  # type: ignore[attr-defined]
            bytes.fromhex("534d4100000402a0ffffffff0000002000000000"),
            (self.addr, self.port),
        )

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        """Datagram received"""
        msg = speedwireHeader.from_packed(data[0:18])
        if not msg.isDiscoveryResponse():
            _LOGGER.warning("Ignoring %s", msg)
            return
        if addr not in self.discovered:
            self.discovered.append(addr)

    def error_received(self, exc: Exception) -> None:
        """Called by error."""
        _LOGGER.error("%s error occurred: %s", type(exc), exc)

    def connection_lost(self, exc: Exception) -> None:
        """Called by connection lost."""
        _LOGGER.error("Socket closed, stop the event loop %s %s", type(exc), exc)
