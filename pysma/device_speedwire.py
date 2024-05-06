# some parts are based on https://github.com/Wired-Square/sma-query/blob/main/src/sma_query_sw/protocol.py
# big parts rewritten
import logging
import time
import ctypes
import binascii
import copy
import collections
import struct

from typing import Any, Dict, Optional, List
from ctypes import LittleEndianStructure
from asyncio import DatagramProtocol
from typing import Annotated
import dataclasses_struct as dcs

from .helpers import version_int_to_string
from .definitions_speedwire import commands, responseDef

from .sensor import Sensor
from .const import SMATagList

from .exceptions import (
    SmaConnectionException,
    SmaReadException,
    SmaAuthenticationException,
)
from .sensor import Sensors
from .device import Device
import asyncio

_LOGGER = logging.getLogger(__name__)

APP_ID = 125
ANY_SERIAL = 0xFFFFFFFF
ANY_SUSYID = 0xFFFF

# Login Timeout in seconds
LOGIN_TIMEOUT = 900

# Create a reverse index based command lookup
# ril_index = {f"ril-{value['first']:X}": value for (key, value) in commands.items() if "first" in value}


def get_encoded_pw(password, installer=False):
    # user=0x88, installer=0xBB
    byte_password = bytearray(password.encode("ascii"))

    if installer:
        login_code = 0xBB
    else:
        login_code = 0x88

    encodedpw = bytearray(12)

    for index in range(0, 12):
        if index < len(byte_password):
            encodedpw[index] = (login_code + byte_password[index]) % 256
        else:
            encodedpw[index] = login_code

    return encodedpw


class SpeedwireFrame:
    _frame_sequence = 1
    _id = (ctypes.c_ubyte * 4).from_buffer(bytearray(b"SMA\x00"))
    _tag0 = (ctypes.c_ubyte * 4).from_buffer(bytearray(b"\x00\x04\x02\xA0"))
    _group1 = (ctypes.c_ubyte * 4).from_buffer(bytearray(b"\x00\x00\x00\x01"))
    _eth_sig = (ctypes.c_ubyte * 4).from_buffer(bytearray(b"\x00\x10\x60\x65"))
    _ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x01"))
    _ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x01"))

    _data_length = 0  # Placeholder value
    _longwords = 0  # Placeholder value
    _ctrl = 0  # Placeholder value

    class FrameHeader(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("id", ctypes.c_ubyte * 4),
            ("tag0", ctypes.c_ubyte * 4),
            ("group1", ctypes.c_ubyte * 4),
            ("data_length", ctypes.c_uint16),
            ("eth_sig", ctypes.c_ubyte * 4),
            ("longwords", ctypes.c_ubyte),
            ("ctrl", ctypes.c_ubyte),
        ]

    class DataHeader(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("dst_sysyid", ctypes.c_uint16),
            ("dst_serial", ctypes.c_uint32),
            ("ctrl2_1", ctypes.c_ubyte * 2),
            ("app_id", ctypes.c_uint16),
            ("app_serial", ctypes.c_uint32),
            ("ctrl2_2", ctypes.c_ubyte * 2),
            ("preamble", ctypes.c_uint32),
            ("sequence", ctypes.c_uint16),
        ]

    class LogoutFrame(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("command", ctypes.c_uint32),
            ("data_start", ctypes.c_uint32),
            ("data_end", ctypes.c_uint32),
        ]

    class LoginFrame(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("command", ctypes.c_uint32),
            ("login_type", ctypes.c_uint32),
            ("timeout", ctypes.c_uint32),
            ("time", ctypes.c_uint32),
            ("data_start", ctypes.c_uint32),
            ("user_password", ctypes.c_ubyte * 12),
            ("data_end", ctypes.c_uint32),
        ]

    class QueryFrame(LittleEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("command", ctypes.c_uint32),
            ("first", ctypes.c_uint32),
            ("last", ctypes.c_uint32),
            ("data_end", ctypes.c_uint32),
        ]

    # def getLogoutFrame(self, inverter):
    #     frame_header = self.getFrameHeader()
    #     frame_data_header = self.getDataHeader(inverter)
    #     frame_data = self.LogoutFrame()

    #     frame_header.ctrl = 0xA0
    #     frame_data_header.dst_sysyid = 0xFFFF
    #     frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x03"))
    #     frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x03"))

    #     frame_data.command = commands["logoff"]["command"]
    #     frame_data.data_start = 0xFFFFFFFF
    #     frame_data.data_end = 0x00000000

    #     data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

    #     frame_header.data_length = int.from_bytes(data_length.to_bytes(2, "big"), "little")

    #     frame_header.longwords = (data_length // 4)

    #     return bytes(frame_header) + bytes(frame_data_header) + bytes(frame_data)

    def getLoginFrame(self, password, serial: int, installer: bool):
        frame_header = self.getFrameHeader()
        frame_data_header = self.getDataHeader(password, serial)
        frame_data = self.LoginFrame()

        frame_header.ctrl = 0xA0
        frame_data_header.dst_sysyid = 0xFFFF
        frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(
            bytearray(b"\x00\x01")
        )
        frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(
            bytearray(b"\x00\x01")
        )

        frame_data.command = commands["login"]["command"]
        frame_data.login_type = (0x07, 0x0A)[installer]
        frame_data.timeout = LOGIN_TIMEOUT
        frame_data.time = int(time.time())
        frame_data.data_start = 0x00000000  # Data Start
        frame_data.user_password = (ctypes.c_ubyte * 12).from_buffer(
            get_encoded_pw(password, installer)
        )
        frame_data.date_end = 0x00000000  # Packet End

        data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

        frame_header.data_length = int.from_bytes(
            data_length.to_bytes(2, "big"), "little"
        )

        frame_header.longwords = data_length // 4

        return bytes(frame_header) + bytes(frame_data_header) + bytes(frame_data)

    def getQueryFrame(self, password, serial: int, command_name: str):
        frame_header = self.getFrameHeader()
        frame_data_header = self.getDataHeader(password, serial)
        frame_data = self.QueryFrame()

        command = commands[command_name]

        frame_header.ctrl = 0xA0
        frame_data_header.dst_sysyid = 0xFFFF
        frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(
            bytearray(b"\x00\x00")
        )
        frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(
            bytearray(b"\x00\x00")
        )

        frame_data.command = command["command"]
        frame_data.first = command["first"]
        frame_data.last = command["last"]
        frame_data.date_end = 0x00000000

        data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

        frame_header.data_length = int.from_bytes(
            data_length.to_bytes(2, "big"), "little"
        )

        frame_header.longwords = data_length // 4

        return bytes(frame_header) + bytes(frame_data_header) + bytes(frame_data)

    def getFrameHeader(self):
        newFrameHeader = self.FrameHeader()
        newFrameHeader.id = self._id
        newFrameHeader.tag0 = self._tag0
        newFrameHeader.group1 = self._group1
        newFrameHeader.data_length = self._data_length
        newFrameHeader.eth_sig = self._eth_sig
        newFrameHeader.longwords = self._longwords
        newFrameHeader.ctrl = self._ctrl

        return newFrameHeader

    def getDataHeader(self, password, serial):
        newDataHeader = self.DataHeader()

        newDataHeader.dst_susyid = ANY_SUSYID
        newDataHeader.dst_serial = ANY_SERIAL
        newDataHeader.ctrl2_1 = self._ctrl2_1
        newDataHeader.app_id = APP_ID
        newDataHeader.app_serial = serial
        newDataHeader.ctrl2_2 = self._ctrl2_2
        newDataHeader.preamble = 0
        newDataHeader.sequence = self._frame_sequence | 0x8000

        self._frame_sequence += 1

        return newDataHeader


@dcs.dataclass(dcs.BIG_ENDIAN)
class speedwireHeader:
    sma: Annotated[bytes, 4]
    tag42_length: dcs.U16
    tag42_tag0x02A0: dcs.U16
    group1: dcs.U32
    smanet2_length: dcs.U16
    smanet2_tag0x10: dcs.U16
    protokoll: dcs.U16

    def check6065(self):
        return (
            self.sma == b"SMA\x00"
            and self.tag42_length == 4
            and self.tag42_tag0x02A0 == 0x02A0
            and self.group1 == 1
            and self.smanet2_tag0x10 == 0x10
            and self.protokoll == 0x6065
        )


# https://github.com/RalfOGit/libspeedwire
@dcs.dataclass(dcs.LITTLE_ENDIAN)
class speedwireHeader6065:
    # dest_susyid: dcs.U16 #2
    # dest_serial: dcs.U32 # 2+ 4 = 6
    # dest_control: dcs.U16 # 2 4 + 2 = 8
    # src_susyid: dcs.U16 # 2 4 2 2 = 10
    # src_serial: dcs.U32 # 2 4 2 2 4 = 14
    # src_control: dcs.U16 # 2 4 2 2 4 2 = 16

    # unknown1: dcs.U16 # 2
    # susyid: dcs.U16  # 2 +2 = 4
    # serial: dcs.U32  # 2 + 2 + 4 = 8
    # unknown2: Annotated[bytes, 10] # 18

    unknown2: Annotated[bytes, 18]  # 18
    error: dcs.U16
    fragment: dcs.U16
    pktId: dcs.U16
    cmdid: dcs.U32
    firstRegister: dcs.U32
    lastRegister: dcs.U32

    def isLoginResponse(self):
        return self.cmdid == 0xFFFD040D


class SMAClientProtocol(DatagramProtocol):

    debug = {
        "msg": collections.deque(maxlen=len(commands) * 3),
        "data": {},
        "unfinished": set(),
        "ids": set(),
    }

    def __init__(self, password, on_connection_lost):
        self.speedwire = SpeedwireFrame()
        self.transport = None
        self.password = password
        self.on_connection_lost = on_connection_lost
        self.cmds = []
        self.cmdidx = 0
        self.future = None
        self.dataValues = {}
        self.sensors = {}

        self.allCmds = []
        self.allCmds.extend(commands.keys())
        self.allCmds.remove("login")
        self.allCmds.remove("logoff")

    def connection_made(self, transport):
        self.transport = transport

    def start_query(self, cmds: List, future, group: str):
        self.cmds = cmds
        self.future = future
        self.cmdidx = 0
        self.dataValues = {}
        self.sensors = {}
        _LOGGER.debug("Sending login")
        self.debug["msg"].append(["SEND", "login"])
        groupidx = ["user", "installer"].index(group)
        self._send_command(self.speedwire.getLoginFrame(self.password, 0, groupidx))

    def connection_lost(self, exc):
        _LOGGER.debug(f"Connection lost: {exc}")
        self.on_connection_lost.set_result(True)

    def _send_command(self, cmd):
        _LOGGER.debug(
            f"Sending command [{len(cmd)}] -- {binascii.hexlify(cmd).upper()}"
        )
        self.transport.sendto(cmd)

    def _send_next_command(self):
        if not self.future:
            return
        if self.cmdidx >= len(self.cmds):
            # All commands send. Clean up.
            self.debug["data"] = self.dataValues
            self.future.set_result(True)
            self.cmds = []
            self.cmdidx = 0
            self.future = None
        else:
            # Send the next command
            self.debug["msg"].append(["SEND", self.cmds[self.cmdidx]])
            _LOGGER.debug("Sending " + self.cmds[self.cmdidx])
            self._send_command(
                self.speedwire.getQueryFrame(self.password, 0, self.cmds[self.cmdidx])
            )
            self.cmdidx += 1

    def _getFormat(self, handler):
        converter = None
        format = handler.get("format", "")
        if format == "int":
            format = "<l"
        elif format == "" or format == "uint":
            format = "<L"
        elif format == "version":
            format = "<L"
            converter = version_int_to_string
        else:
            raise ValueError(f"Unknown Format {format}")
        size = struct.calcsize(format)
        return (format, size, converter)

    def handle_login(self, msg):
        _LOGGER.debug("Login repsonse received!")
        self.sensors = {}
        self.dataValues = {"error": msg.error}
        if msg.error == 256:
            _LOGGER.error("Login failed!")
            self.future.set_exception(
                SmaAuthenticationException(
                    "Login failed! Credentials wrong (user/install or password)"
                )
            )

    def handle_newvalue(self, sensor: Sensor, value: Any):
        if value is None:
            return
        sen = copy.copy(sensor)
        if sen.factor and sen.factor != 1:
            value /= sen.factor
        sen.value = value
        if sen.key in self.sensors:
            oldValue = self.sensors[sen.key].value
            if oldValue != value:
                _LOGGER.warning(
                    f"Overwriting sensors {sen.key} {sen.name} {oldValue} with new values {sen.value}"
                )
        self.sensors[sen.key] = sen
        self.dataValues[sen.key] = value

    def extractvalues(self, handler: Dict, subdata):
        (formatdef, size, converter) = self._getFormat(handler)
        values = []
        for idx in range(8, len(subdata), size):
            v = struct.unpack(formatdef, subdata[idx : idx + size])[0]
            if v in [0xFFFFFFFF, 0x80000000, 0xFFFFFFEC]:
                v = None
            else:
                if converter:
                    v = converter(v)
                if "mask" in handler:
                    v = v & handler["mask"]
            values.append(v)
        return values

    def handle_register(self, subdata):
        code = int.from_bytes(subdata[0:4], "little")
        # c = f"{(code & 0xFFFFFFFF):08X}"
        c = f"{code:08X}"
        msec = int.from_bytes(subdata[4:8], "little")  # noqa: F841

        # Fix for strange Codes
        self.debug["ids"].add(c[6:])
        if c.endswith("07"):
            c = c[:7] + "1"

        # Handle unknown Responses
        if c not in responseDef:
            values = []
            valuesPos = []
            for idx in range(8, len(subdata), 4):
                v = struct.unpack("<l", subdata[idx : idx + 4])[0]
                values.append(v)
                valuesPos.append(f"{idx + 54}")
            _LOGGER.warning(f"No Handler for {c}: {values} @ {valuesPos}")
            self.debug["unfinished"].add(f"{c}")
            return

        # Handle known repsones
        for handler in responseDef[c]:

            values = self.extractvalues(handler, subdata)
            if "sensor" not in handler:
                continue
            v = values[handler["idx"]]

            self.handle_newvalue(handler["sensor"], v)

    # Unfortunately, there is no known method of determining the size of the registers
    # from the message. Therefore, the register size is determined from the number of
    # registers and the size of the payload.
    def calcRegister(self, data, msg: speedwireHeader6065):
        cntRegisters = msg.lastRegister - msg.firstRegister + 1
        sizDataPayload = len(data) - 54 - 4
        sizeRegisters = (
            sizDataPayload // cntRegisters if sizDataPayload % cntRegisters == 0 else -1
        )
        return (cntRegisters, sizeRegisters)

    # Main routine for processing received messages.
    def datagram_received(self, data, addr):
        _LOGGER.debug(f"RECV: {addr} Len:{len(data)} {binascii.hexlify(data).upper()}")
        self.debug["msg"].append(
            ["RECV", len(data), binascii.hexlify(data).upper().decode("utf-8")]
        )

        # Check if message is a 6065 protocol
        msg = speedwireHeader.from_packed(data[0:18])
        if not msg.check6065():
            _LOGGER.debug("Ignoring non 6065 Response.")
            return

        # If the requested information is not available, send the next command,
        if len(data) < 58:
            _LOGGER.debug(f"NACK [{len(data)}] -- {data}")
            self._send_next_command()
            return

        # Handle Login Responses
        msg6065 = speedwireHeader6065.from_packed(data[18 : 18 + 36])
        if msg6065.isLoginResponse():
            self.handle_login(msg6065)
            self._send_next_command()
            return

        # Filter out non matching responses
        (cntRegisters, sizeRegisters) = self.calcRegister(data, msg6065)
        code = int.from_bytes(data[54:58], "little")
        codem = code & 0x00FFFF00
        if sizeRegisters <= 0 or sizeRegisters not in [16, 28, 40]:
            _LOGGER.warning(
                f"Skipping message. --- Len {data} Ril {codem} {cntRegisters} x {sizeRegisters} bytes"
            )
            self._send_next_command()
            return

        # Extract the values for each register
        for idx in range(0, cntRegisters):
            start = idx * sizeRegisters + 54
            self.handle_register(data[start : start + sizeRegisters])

        # Send new command
        self._send_next_command()


class SMAspeedwireINV(Device):

    _transport = None
    _protocol = None
    _deviceinfo = {}

    def __init__(self, host: str, group: str, password: Optional[str]):
        self._host = host
        self._group = group
        self._password = password
        if group not in ["user", "installer"]:
            raise KeyError(f"Invalid user type: {group} (user or installer)")

        self.check()

    def check(self) -> None:
        keysname = {}
        sensorname = {}
        for responses in responseDef.values():
            for response in responses:
                if "sensor" not in response:
                    continue
                sensor = response["sensor"]
                if sensor.key in keysname:
                    print("Doppelter SensorKey " + sensor.key)
                    raise RuntimeError("Doppelter SensorKey " + sensor.key)
                keysname[sensor.key] = 1
                if sensor.name in sensorname:
                    print("Doppelter SensorName " + sensor.name)
                    raise RuntimeError("Doppelter Sensorname " + sensor.name)
                sensorname[sensor.name] = 1

        keysname = {}
        sensorname = {}
        for x in commands.items():
            if "registers" not in x[1]:
                continue
            for r in x[1]["registers"]:
                if "name" in r:
                    name = r["name"]
                    if name in keysname:
                        print("Doppelter Keyname " + name)
                        raise RuntimeError("Doppelter Keyname " + name)
                    keysname[name] = 1
                if "sensor" in r:
                    sensor = r["sensor"]
                    if sensor.key in sensorname:
                        print("Doppelter Sensorname " + sensor.key)
                        raise RuntimeError("Doppelter Sensorname " + sensor.key)
                    sensorname[name] = 1

    async def new_session(self) -> bool:
        loop = asyncio.get_running_loop()
        on_connection_lost = loop.create_future()

        self._transport, self._protocol = await loop.create_datagram_endpoint(
            lambda: SMAClientProtocol(self._password, on_connection_lost),
            remote_addr=(self._host, 9522),
        )

    async def device_info(self) -> dict:
        fut = asyncio.get_running_loop().create_future()
        self._protocol.start_query(["TypeLabel", "Firmware"], fut, self._group)
        try:
            await asyncio.wait_for(fut, timeout=5)
        except TimeoutError:
            _LOGGER.warning("Timeout in device_info")
            if (
                "error" in self._protocol.dataValues
                and self._protocol.dataValues["error"] == 0
            ):
                raise SmaReadException("Reply for request not received")
            else:
                raise SmaConnectionException("No connection to device")
        data = self._protocol.dataValues

        invcnr = data.get("inverter_class", 0)
        invc = SMATagList.get(invcnr, "Unknown device")

        invtnr = data.get("inverter_type", 0)
        invt = SMATagList.get(invtnr, "Unknown type")
        self._deviceinfo = {
            "serial": data.get("serial", ""),
            "name": str(invt) + " (" + str(invtnr) + ")",
            "type": str(invc) + " (" + str(invcnr) + ")",
            "manufacturer": "SMA",
            "sw_version": data.get("Firmware", ""),
        }
        return self._deviceinfo

    async def get_sensors(self) -> Sensors:
        fut = asyncio.get_running_loop().create_future()
        c = self._protocol.allCmds
        self._protocol.start_query(c, fut, self._group)
        await asyncio.wait_for(fut, timeout=5)
        device_sensors = Sensors()
        for s in self._protocol.sensors.values():
            device_sensors.add(s)
        return device_sensors

    async def read(self, sensors: Sensors) -> bool:
        fut = asyncio.get_running_loop().create_future()
        c = self._protocol.allCmds
        self._protocol.start_query(c, fut, self._group)
        await asyncio.wait_for(fut, timeout=5)
        self._updateSensors(sensors, self._protocol.sensors)

    def _updateSensors(self, sensors, sensorReadings):
        for sen in sensors:
            if sen.enabled and sen.key in sensorReadings:
                value = sensorReadings[sen.key].value
                if sen.mapper:
                    sen.mapped_value = sen.mapper.get(value, str(value))
                sen.value = value

    async def close_session(self) -> None:
        self._transport.close()

    async def get_debug(self) -> Dict:
        return {
            "msg": list(self._protocol.debug["msg"]),
            "data": self._protocol.debug["data"],
            "device_info": self._deviceinfo,
            "unfinished": list(self._protocol.debug["unfinished"]),
            "ids": list(self._protocol.debug["ids"]),
        }

    # Send a typelabel Command to the Ip-Address and
    # wait for a response or a timeout
    async def detect(self, ip) -> bool:
        ret = await super().detect(ip)
        try:
            ret[0]["testedEndpoints"] = str(ip) + ":9522"
            await self.new_session()
            fut = asyncio.get_running_loop().create_future()
            self._protocol.start_query(["TypeLabel"], fut, self._group)
            try:
                await asyncio.wait_for(fut, timeout=5)
            except TimeoutError:
                _LOGGER.warning("Timeout in detect")
            if (
                "error" in self._protocol.dataValues
                and self._protocol.dataValuess["error"] == 0
            ):
                raise SmaReadException("Reply for request not received")
            else:
                raise SmaConnectionException("No connection to device")
        except SmaAuthenticationException as e:
            ret[0]["status"] = "maybe"
            ret[0]["exception"] = e
            ret[0]["remark"] = "only unencrypted Speedwire is supported"
        except Exception as e:
            ret[0]["status"] = "failed"
            ret[0]["exception"] = e
        return ret
