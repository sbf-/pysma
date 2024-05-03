# based on https://github.com/Wired-Square/sma-query/blob/main/src/sma_query_sw/protocol.py
import logging
import time
import ctypes
import binascii
import copy
import collections
import struct

from typing import Any, Dict, Optional,List
from ctypes import LittleEndianStructure
from asyncio import DatagramProtocol

from .helpers import version_int_to_string
from .definitions_speedwire import commands

from .sensor import Sensor
from .const import Identifier
from .const import SMATagList

from .exceptions import (
    SmaConnectionException,
    SmaReadException,
    SmaAuthenticationException
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
ril_index = {f"ril-{value['first']:X}": value for (key, value) in commands.items() if "first" in value}


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
            ("data_end", ctypes.c_uint32)
        ]

    def getLogoutFrame(self, inverter):
        frame_header = self.getFrameHeader()
        frame_data_header = self.getDataHeader(inverter)
        frame_data = self.LogoutFrame()

        frame_header.ctrl = 0xA0
        frame_data_header.dst_sysyid = 0xFFFF
        frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x03"))
        frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x03"))

        frame_data.command = commands["logoff"]["command"]
        frame_data.data_start = 0xFFFFFFFF
        frame_data.data_end = 0x00000000

        data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

        frame_header.data_length = int.from_bytes(data_length.to_bytes(2, "big"), "little")

        frame_header.longwords = (data_length // 4)

        return bytes(frame_header) + bytes(frame_data_header) + bytes(frame_data)

    def getLoginFrame(self, inverter, installer):
        frame_header = self.getFrameHeader()
        frame_data_header = self.getDataHeader(inverter)
        frame_data = self.LoginFrame()

        frame_header.ctrl = 0xA0
        frame_data_header.dst_sysyid = 0xFFFF
        frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x01"))
        frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x01"))

        frame_data.command = commands["login"]["command"]
        frame_data.login_type = (0x07, 0x0A)[installer]
        frame_data.timeout = LOGIN_TIMEOUT
        frame_data.time = int(time.time())
        frame_data.data_start = 0x00000000  # Data Start
        frame_data.user_password = (ctypes.c_ubyte * 12).from_buffer(get_encoded_pw(inverter["user_password"], installer))
        frame_data.date_end = 0x00000000 # Packet End

        data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

        frame_header.data_length = int.from_bytes(data_length.to_bytes(2, "big"), "little")

        frame_header.longwords = (data_length // 4)

        return bytes(frame_header) + bytes(frame_data_header) + bytes(frame_data)

    def getQueryFrame(self, inverter, command_name):
        frame_header = self.getFrameHeader()
        frame_data_header = self.getDataHeader(inverter)
        frame_data = self.QueryFrame()

        command = commands[command_name]

        frame_header.ctrl = 0xA0
        frame_data_header.dst_sysyid = 0xFFFF
        frame_data_header.ctrl2_1 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x00"))
        frame_data_header.ctrl2_2 = (ctypes.c_ubyte * 2).from_buffer(bytearray(b"\x00\x00"))

        frame_data.command = command["command"]
        frame_data.first = command["first"]
        frame_data.last = command["last"]
        frame_data.date_end = 0x00000000

        data_length = ctypes.sizeof(frame_data_header) + ctypes.sizeof(frame_data)

        frame_header.data_length = int.from_bytes(data_length.to_bytes(2, "big"), "little")

        frame_header.longwords = (data_length // 4)

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

    def getDataHeader(self, inverter):
        newDataHeader = self.DataHeader()

        newDataHeader.dst_susyid = ANY_SUSYID
        newDataHeader.dst_serial = ANY_SERIAL
        newDataHeader.ctrl2_1 = self._ctrl2_1
        newDataHeader.app_id = APP_ID
        newDataHeader.app_serial = (inverter["serial"])
        newDataHeader.ctrl2_2 = self._ctrl2_2
        newDataHeader.preamble = 0
        newDataHeader.sequence = (self._frame_sequence | 0x8000)

        self._frame_sequence += 1

        return newDataHeader


class SMAClientProtocol(DatagramProtocol):

    useDummyData = False
    debug = {
        "msg": collections.deque(maxlen=30),
        "data": {},
        "unfinished": set()
    }

    def __init__(self, inverter, on_connection_lost):
        self.speedwire = SpeedwireFrame()
        self.transport = None
        self.inverter = inverter
        self.on_connection_lost = on_connection_lost
        self.cmds = []
        self.cmdidx = 0
        self.future = None

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
        self.inverter["data"] = {}
        self.inverter["sensors"] = {}
        _LOGGER.debug(f"""Sending login for {self.inverter["serial"]:#08X}""")
        if self.useDummyData:
            self.inverter["data"] = {}
            self.inverter["sensors"] = {}
            self.cmds = []
            self._send_next_command()
        else:
            groupidx = ["user", "installer"].index(group)
            self._send_command(self.speedwire.getLoginFrame(self.inverter, groupidx))
    
    def connection_lost(self, exc):
        _LOGGER.debug(f"Connection lost: {exc}")
        self.on_connection_lost.set_result(True)

    def _send_command(self, cmd):
        _LOGGER.debug(f"Sending command [{len(cmd)}] -- {binascii.hexlify(cmd).upper()}")
        self.transport.sendto(cmd)

    def _get_code(self, data):
        code = int.from_bytes(data[42:46], "little")
        return code

    def _get_ril(self, data):
        code = int.from_bytes(data[54:58], "little")
        return code & 0x00FFFF00

    def _get_value(self, data, offset, format, invalid):
        if format == "int":
            format = "<l"
        elif format == "uint":
            format = "<L"
        size = struct.calcsize(format)
        if (size + offset >= len(data)):
            return None
        v = struct.unpack(format, data[offset:offset+size])[0]
        if (v in [0x80000000, 0xFFFFFFFF, -0x80000000 ] or (invalid and invalid == v)):
            v = None
        return v

    def _get_long_value(self, data, offset):
         value = int.from_bytes(data[offset:offset + 4], "little")
         return value

    def _send_next_command(self):
        if not self.future:
            return
        if self.cmdidx >= len(self.cmds):
            if self.useDummyData:
                f = self.future
                self.future = None
                self.addDummyData()
                self.future = f
            self.debug["data"] = self.inverter["data"]
            self.future.set_result(True)
            self.cmds = []
            self.cmdidx = 0
            self.future = None
        else:
            self.debug["msg"].append(["SEND", self.cmds[self.cmdidx]])
            _LOGGER.debug("Sending "+ self.cmds[self.cmdidx])
            self._send_command(self.speedwire.getQueryFrame(self.inverter,
                                               self.cmds[self.cmdidx]))
            self.cmdidx += 1

    def _getvalue(self, register, data):
            format = register.get("format", "uint")
            value = None
            if format == "list":
                i = register.get("offset")
                while (int.from_bytes(data[i:i+4], byteorder="little") != 0x00FFFFFE) and i+4 <= len(data):
                        temp = int.from_bytes(data[i:i+4], byteorder="little")
                        if (temp & 0xFF000000) == 0x01000000:
                                value = temp & 0x00FFFFFF
                        i += 4
            elif format == "version":
#                        value = self._get_value(data, register["offset"], format, register.get("invalid"))
                value = self._get_long_value(data, register["offset"])
                value = version_int_to_string(value)
            else:
                if register["offset"] >= len(data):
                    _LOGGER.debug(f'Value for {register["name"]} not found in this message type')
                    return None
                value = self._get_value(data, register["offset"], format, register.get("invalid"))
                if value and register.get("mask"):
                    value = value & register.get("mask")
            return value

    def datagram_received(self, data, addr):
        code = self._get_code(data)
        ril = self._get_ril(data)
        ril_key = f"ril-{ril:X}"
        shortcode = (f"{ril:X}")[0:4]

        _LOGGER.debug(f"{addr} -- [{len(data)}] [{code:X}] [{ril:X}] -- {binascii.hexlify(data).upper()}")
        self.debug["msg"].append(["RECV", len(data), (f"{ril:X}")[0:4], binascii.hexlify(data).upper().decode("utf-8")])

        if code == commands["login"]["response"]:
            _LOGGER.debug("Login repsonse received!")
            self.inverter["data"] = {}
            self.inverter["sensors"] = {}
            for r in commands["login"]["registers"]:
                value = self._getvalue(r, data)
                self.inverter["data"][r['name']] = value
            if (self.inverter["data"]["error"] == 256):
                _LOGGER.error("Login failed!")
                self.future.set_exception(SmaAuthenticationException("Login failed! Credentials wrong (user/install or password)"))

        if len(data) <= 58:
            _LOGGER.debug(f"Short datagram received: [{len(data)}] -- {data}")
            self._send_next_command()
            return
        
        if ril_key not in ril_index:
            shortcode = (f"{ril:X}")[0:4]
            _LOGGER.debug(f"No Definition for {ril_key} {code:X} {shortcode}")
            self.debug["unfinished"].add(f"No Definition for {ril_key} {code:X} {shortcode}")
            self._send_next_command()
            return
        
        if ril_key in ril_index:
            command = ril_index[ril_key]
            short = f"{command['first']:#08X}"[2:6]
            if "registers" in command:
                if len(command["registers"]) == 0:
                    self.debug["unfinished"].add(f"Command Response: {ril_key} {short} {code:X}")
                    _LOGGER.error(f"Message but no registers definied. {command}")
                for register in command["registers"]:
                    value = self._getvalue(register, data)
                    if value is not None:
                        if "sensor" in register:
                            sen = copy.copy(register["sensor"])
                            v = value
                            if (sen.factor and sen.factor != 1):
                                v /= sen.factor
                            sen.value = v
                            self.inverter["sensors"][sen.key] = sen
                        else:
                             _LOGGER.debug(f'Value but no sensor: {register["name"]} {value}')
                             pass
                    self.inverter["data"][register["name"]] = value
            else:
                if self.useDummyData:
                    _LOGGER.debug(f" {shortcode} [{len(data)}] [{code:X}] [{ril:X}]")
                    print("======================================================================================================")
                    print("======================================================================================================")
                    raise RuntimeError()
            self._send_next_command()

    def addDummyData(self):
        for pp in []:
            self.datagram_received(bytes.fromhex(pp), ('10.10.10.10', 9522))


class SMAspeedwireINV(Device):

    _transport = None
    _protocol = None
    _deviceinfo = {}

    def __init__(
        self,
        host: str,
        group: str,
        password: Optional[str]
    ):
        self._host = host
        self._group = group
        if group not in ["user", "installer"]:
            raise KeyError(f"Invalid user type: {group} (user or installer)")

        self._inverter = {
            "serial": 0,
            "user_password": password,
        }
    #     self.check()

    # def check(self) -> None:
    #     keysname = {}
    #     sensorname = {}
    #     for x in commands.items():
    #         if "registers" in x[1]:
    #             for r in x[1]["registers"]:
    #                 if "name" in r:
    #                     name = r["name"]
    #                     if (name in keysname):
    #                         print("Doppelter Keyname " + name)
    #                         raise RuntimeError("Doppelter Keyname " + name)
    #                     keysname[name] = 1
    #                 if "sensor" in r:
    #                     sensor = r["sensor"]
    #                     if (sensor.key in sensorname):
    #                         print("Doppelter Sensorname " + sensor.key)
    #                         raise RuntimeError("Doppelter Sensorname " + sensor.key)

    #                     sensorname[name] = 1


    async def get_sensors(self) -> Sensors:
        fut = asyncio.get_running_loop().create_future()
        c = self._protocol.allCmds
        if self._protocol.useDummyData:
            c = []
        self._protocol.start_query(c, fut, self._group)
        await asyncio.wait_for(fut, timeout=5)
        device_sensors = Sensors()
        for s in self._inverter["sensors"].values():
            device_sensors.add(s)
        return device_sensors
    
    async def new_session(self) -> bool:
        loop = asyncio.get_running_loop()
        on_connection_lost = loop.create_future()

        self._transport, self._protocol = await loop.create_datagram_endpoint(
             lambda: SMAClientProtocol(self._inverter, on_connection_lost), 
             remote_addr=(self._host, 9522))

    async def device_info(self) -> dict:
        fut = asyncio.get_running_loop().create_future()
        self._protocol.start_query(["TypeLabel", "Firmware"], fut, self._group)
        try:
            await asyncio.wait_for(fut, timeout=5)
        except TimeoutError:
            _LOGGER.warning("Timeout in device_info")
            if "error" in self._protocol.inverter["data"] and self._protocol.inverter["data"]["error"] == 0:
                raise SmaReadException("Reply for request not received")
            else:
                raise SmaConnectionException("No connection to device")
        print(self._protocol.inverter["data"])
        data = self._inverter["data"]

        invcnr = self._inverter["data"].get("inverter_class",0)
        invc = SMATagList.get(invcnr, "Unknown device")

        invtnr = self._inverter["data"].get("inverter_type",0)
        invt = SMATagList.get(invtnr, "Unknown type")
        self._deviceinfo = {
            "serial": data.get("serial", ""),
            "name": str(invt) + " (" + str(invtnr) + ")",
            "type": str(invc) + " (" + str(invcnr) + ")",
            "manufacturer": "SMA",
            "sw_version": data.get("Firmware",""),
        }
        return self._deviceinfo


    async def read(self, sensors: Sensors) -> bool:
        fut = asyncio.get_running_loop().create_future()
        c = self._protocol.allCmds
        if self._protocol.useDummyData:
            c = []
        self._protocol.start_query(c, fut, self._group)
        await asyncio.wait_for(fut, timeout=5)
        sensorReadings = self._inverter["sensors"]
        for sen in sensors:
            if sen.enabled:
                if sen.key in sensorReadings:
                    value = sensorReadings[sen.key].value
                    if (sen.mapper):
                        sen.mapped_value = sen.mapper.get(value, str(value))
                    sen.value = value


    async def close_session(self) -> None:
        self._transport.close()

    async def get_debug(self) -> Dict:
        return {
            "msg": list(self._protocol.debug["msg"]),
            "data": self._protocol.debug["data"],
            "device_info": self._deviceinfo,
            "unfinished": list(self._protocol.debug["unfinished"])
       }


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
                _LOGGER.warning("Timeout in device_info")
            if "error" in self._protocol.inverter["data"] and self._protocol.inverter["data"]["error"] == 0:
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