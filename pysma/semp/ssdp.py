import asyncio
import logging
import socket
from contextlib import suppress
from typing import cast

BROADCAST_PORT = 1900
BROADCAST_ADDR = "239.255.255.250"

_LOGGER = logging.getLogger(__name__)


class UPNPResponderProtocol(asyncio.Protocol):
    """Handle responding to UPNP/SSDP discovery requests."""

    def __init__(
        self,
        loop: asyncio.AbstractEventLoop,
        ssdp_socket: socket.socket,
        advertise_ip: str,
        advertise_port: int,
        uuid: str,
        boardcastTime: int,
    ) -> None:
        """Initialize the class."""
        self.transport: asyncio.DatagramTransport | None = None
        self._loop = loop
        self._sock = ssdp_socket
        self.advertise_ip = advertise_ip
        self.advertise_port = advertise_ip
        self.uuid = uuid
        self.boardcastTime = boardcastTime

        self.notifyMsg = "NOTIFY * HTTP/1.1\r\n"
        self.notifyMsg += "HOST: {ip}:{port}\r\n".format(
            ip=advertise_ip, port=advertise_port
        )
        self.notifyMsg += "CACHE-CONTROL: max-age = {:d}\r\n".format(boardcastTime * 3)
        self.notifyMsg += "SERVER: HomeassistantSempBinding-Gateway\r\n"
        self.notifyMsg += (
            "LOCATION: http://{ip}:{port}/uuid:{UUID}/description.xml\r\n".format(
                ip=advertise_ip, port=advertise_port, UUID=self.uuid
            )
        )
        self.nts = "alive"

    async def start(self):
        await asyncio.sleep(20)
        while True:
            # await the target
            print("Sending Broadcast")
            for msg in self.getBoardcastMsg("alive"):
                self.transport.sendto(msg.encode("utf-8"), ("239.255.255.250", 1900))
            await asyncio.sleep(self.boardcastTime)
            # wait an interval

    def getBoardcastMsg(self, nts: str):
        return [
            self.notifyMsg
            + "NTS: ssdp:{nts}\r\n".format(nts=self.nts)
            + "NT: upnp:rootdevice\r\n"
            + "USN: uuid:{UUID}::upnp:rootdevice\r\n \r\n".format(UUID=self.uuid),
            self.notifyMsg
            + "NTS: ssdp:{nts}\r\n".format(nts=self.nts)
            + "NT: uuid:{UUID}\r\n".format(UUID=self.uuid)
            + "USN: uuid:{UUID}\r\n \r\n".format(UUID=self.uuid),
            self.notifyMsg
            + "NTS: ssdp:{nts}\r\n".format(nts=self.nts)
            + "NT: urn:schemas-simple-energy-management-protocol:device:Gateway:1\r\n"
            + "USN: uuid:{UUID}::urn:schemas-simple-energy-management-protocol:device:Gateway:1\r\n \r\n".format(
                UUID=self.uuid
            ),
        ]

    def connection_made(self, transport: asyncio.BaseTransport) -> None:
        """Set the transport."""
        self.transport = cast(asyncio.DatagramTransport, transport)

    def connection_lost(self, exc: Exception | None) -> None:
        """Handle connection lost."""

    def datagram_received(self, data: bytes, addr: tuple[str, int]) -> None:
        assert self.transport is not None
        """Respond to msearch packets."""
        decoded_data = data.decode("utf-8", errors="ignore").rsplit("\r\n")
        if len(decoded_data) == 0 or not decoded_data[0].startswith("M-SEARCH "):
            return
        if 'MAN: "ssdp:discover"' in decoded_data:
            if (
                "ST: urn:schemas-simple-energy-management-protocol:device:Gateway:1"
                in decoded_data
            ):
                r = self.notifyMsg
                r += "NTS: ssdp:alive\r\n"
                r += "NT: urn:schemas-simple-energy-management-protocol:device:Gateway:1\r\n"
                r += "USN: uuid:{UUID}::urn:schemas-simple-energy-management-protocol:device:Gateway:1\r\n \r\n".format(
                    UUID=self.uuid
                )
                #                return bytes(r, "utf-8")
                #                print(r.encode("utf-8"))
                self.transport.sendto(r.encode("utf-8"), addr)

                # response = self.ssdp_messages.msg_SEMPGateway()
            #               print(decoded_data)
            #              print(addr)
            if "ST: ssdp:all" in decoded_data:
                for msg in self.getBoardcastMsg("alive"):
                    self.transport.sendto(
                        msg.encode("utf-8"), ("239.255.255.250", 1900)
                    )
        return

    def error_received(self, exc: Exception) -> None:
        """Log UPNP errors."""
        _LOGGER.error("UPNP Error received: %s", exc)

    def close(self) -> None:
        """Stop the server."""
        # TODO Deregister Messages
        _LOGGER.info("UPNP responder shutting down")
        if self.transport:
            self.transport.close()
        self._loop.remove_writer(self._sock.fileno())
        self._loop.remove_reader(self._sock.fileno())
        self._sock.close()


async def async_create_upnp_datagram_endpoint(
    host_ip_addr: str,
    upnp_bind_multicast: bool,
    advertise_ip: str,
    advertise_port: int,
    uuid: str,
    boardcastTime: int = 600,
) -> UPNPResponderProtocol:
    """Create the UPNP socket and protocol."""
    # Listen for UDP port 1900 packets sent to SSDP multicast address
    ssdp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ssdp_socket.setblocking(False)

    # Required for receiving multicast
    # Note: some code duplication from async_upnp_client/ssdp.py here.
    ssdp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    with suppress(AttributeError):
        ssdp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    ssdp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    ssdp_socket.setsockopt(
        socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host_ip_addr)
    )

    ssdp_socket.setsockopt(
        socket.SOL_IP,
        socket.IP_ADD_MEMBERSHIP,
        socket.inet_aton(BROADCAST_ADDR) + socket.inet_aton(host_ip_addr),
    )

    ssdp_socket.bind(("" if upnp_bind_multicast else host_ip_addr, BROADCAST_PORT))

    loop = asyncio.get_event_loop()

    p = UPNPResponderProtocol(
        loop, ssdp_socket, advertise_ip, advertise_port, uuid, boardcastTime
    )
    transport_protocol = await loop.create_datagram_endpoint(
        lambda: p,
        sock=ssdp_socket,
    )
    print("Starting")
    loop = asyncio.get_event_loop()
    loop.create_task(p.start())

    #    control.start
    #   await p.start()
    return transport_protocol[1]
