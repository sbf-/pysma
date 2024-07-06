import collections
import copy
import html
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Awaitable, Callable

import untangle  # type: ignore
import xmlschema
from aiohttp import web

from pysmaplus.semp.const import callbackAction

from .const import (
    debugHTML,
    descriptionXML,
    deviceInfoXML,
    deviceStatusXML,
    hintsHTML,
    sempXMLend,
    sempXMLstart,
    timeFrameXml,
)
from .device import sempDevice
from .sempxsd import sempxsd

_LOGGER = logging.getLogger(__name__)


@dataclass
class historyData:
    time: str
    timemsec: float
    typ: str
    remote: str
    deviceData: dict[str, sempDevice]
    cmdData: dict


class SEMPhttpServer:
    routes = web.RouteTableDef()
    devices: dict[str, sempDevice] = {}
    history: collections.deque[historyData] = collections.deque(maxlen=180)

    def __init__(
        self,
        addr,
        port,
        uuid,
        timezone,
        callback: Callable[[callbackAction], Awaitable[None]] | None = None,
    ):
        """Initialize the instance of the view."""
        print("Init HTTP-Server")
        self.port = port
        self.addr = addr
        self.lastip = addr.split(".")[-1]
        self.uuid = uuid
        self.timezone = timezone
        self.sempSchema = None
        self.callback = callback

    def loadSempSchema(self):
        self.sempSchema = xmlschema.XMLSchema(sempxsd)

    async def getUUIDPage(self, request):

        msg = descriptionXML.format(
            friendly_name=self.lastip + " HA-GW",
            manufacturer="Home Assistant",
            manufacturer_url="https://www.home-assistant.io/",
            model_description="SEMP-to-Home-Assistant-Gateway",
            model_name="HA_SEMP",
            model_number="1.0.0",
            model_url="https://www.home-assistant.io/",
            serial_number="123",  # TODO
            uuid="53-4D-41-53-4D-43",  # TODO
            presentation_url=f"http://{self.addr}:{self.port}",
        )
        return web.Response(text=msg, content_type="text/xml")

    async def getStatusPage(self, request):
        devices = set()
        devicesName = {}
        for dataTuple in self.history:
            if dataTuple.deviceData:
                for devId in dataTuple.deviceData.keys():
                    devices.add(devId)
                    if devId not in devicesName:
                        devicesName[devId] = dataTuple.deviceData[devId]
        devices = list(devices)
        out = debugHTML
        out += "<h2>Last SEMP-Requests from SHM</h2>"
        if len(self.history) == 0:
            out += "None<br>"
        else:
            out += "<table><thead><tr><th>Time</th>\n"
            for d in devices:
                out += f"<th>{d[11:23]}<br>{devicesName[d].deviceName}</th>\n"
            out += "<th>Request IP</th></thead>\n<tbody>"

            for row in reversed(self.history):
                out += f"<tr><td>{row.time}</td>"
                for d in devices:
                    value = ""
                    if row.deviceData and d in row.deviceData:
                        value = (
                            f"{row.deviceData[d].power} ({row.deviceData[d].status})"
                        )
                    if row.cmdData and d in row.cmdData:
                        value = f"Request: Turn {row.cmdData[d]['status']}"
                    out += "<td>" + value + "</td>"
                out += f"<td>{row.remote} {row.typ}</td>"
                out += "</tr>"
            out += "</tbody></table>"

        out += "<h2>Current Status</h2><pre>"
        ret = []
        for dev in self.devices.values():
            ret.append(
                {
                    "deviceId": dev.deviceId,
                    "deviceName": html.escape(dev.deviceName),
                    "deviceType": dev.deviceType,
                    "deviceSerial": html.escape(dev.deviceSerial),
                    "deviceVendor": html.escape(dev.deviceVendor),
                    "power": dev.power,
                    "status": dev.status,
                    "optionalEnergy": dev.optionalEnergy,
                    "interruptionsAllowed": dev.interruptionsAllowed,
                    "Max Consumption": dev.deviceMaxConsumption,
                }
            )
        out += json.dumps(ret, indent=4)
        out += "</pre>"
        out += hintsHTML
        return web.Response(text=out, content_type="text/html")

    def bool2str(self, b):
        return str(b).lower()

    async def postSemp(self, request):
        buffer = b""
        async for data, end_of_http_chunk in request.content.iter_chunks():
            buffer += data
            # if end_of_http_chunk:
            #     print(buffer)
        #        try:
        _LOGGER.info(buffer)
        print(buffer)
        #  '<EM2Device xmlns="http://www.sma.de/communication/schema/SEMP/v1"><DeviceControl>
        # <DeviceId>F-00000001-000000000002-00</DeviceId>
        # <On>true</On>
        # </DeviceControl></EM2Device>
        # b'<?xml version="1.0" encoding="UTF-8"?>\n<EM2Device xmlns="http://www.sma.de/communication/schema/SEMP/v1">\n\t<DeviceControl>\n\t\t<DeviceId>F-11223344-223529992949-00</DeviceId>\n\t\t<On>true</On>\n\t\t<RecommendedPowerConsumption>0</RecommendedPowerConsumption>\n\t\t<Timestamp>0</Timestamp>\n\t</DeviceControl>\n</EM2Device>'

        obj = untangle.parse(buffer.decode("utf-8"))
        assert (
            obj.children[0]["xmlns"] == "http://www.sma.de/communication/schema/SEMP/v1"
        )
        devId = obj.EM2Device.DeviceControl.DeviceId.cdata
        onoff = obj.EM2Device.DeviceControl.On.cdata.lower()
        if onoff == "true":
            onoffStr = "on"
        else:
            onoffStr = "off"
        data = {}
        data[devId] = {}
        data[devId]["devid"] = devId
        data[devId]["status"] = onoffStr
        h = historyData(
            datetime.now().isoformat()[0:19],
            datetime.now().timestamp(),
            "COMMAND",
            str(request.remote),
            None,
            data,
        )
        self.history.append(h)
        assert onoff in ["true", "false"]
        onoffBool = onoff == "true"
        print(devId, onoffBool)
        if devId.startswith("F-11223344-") and devId.endswith("-00"):
            devId = devId[2 + 8 + 1 : -3]
        else:
            _LOGGER.warning(f"Unknown device id received {devId}")
        if self.callback:
            await self.callback(callbackAction(devId, onoffBool))
        return web.Response(text="", content_type="text/xml")

    def Now(self) -> datetime:
        if self.timezone:
            return datetime.now(tz=self.timezone)
        else:
            return datetime.now()

    async def getSemp(self, request):
        now = self.Now()

        msg = sempXMLstart
        data = {}
        for dev in self.devices.values():
            dev.update()
            data[dev.deviceId] = copy.copy(dev)
            msg += deviceInfoXML.format(
                deviceId=dev.deviceId,
                deviceName=html.escape(dev.deviceName),
                deviceType=dev.deviceType,
                deviceSerial=dev.deviceSerial,
                deviceVendor=html.escape(dev.deviceVendor),
                maxPowerConsumption=int(dev.deviceMaxConsumption),
                minPowerConsumption=int(dev.deviceMinConsumption),
                interruptionsAllowed=self.bool2str(dev.interruptionsAllowed),
                optionalEnergy=self.bool2str(dev.optionalEnergy),
                minOnTime=int(dev.minOnTime),
                minOffTime=int(dev.minOffTime),
            )
        now = self.Now()
        h = historyData(
            now.isoformat()[0:19],
            now.timestamp(),
            "STATUS",
            str(request.remote),
            data,
            None,
        )
        self.history.append(h)
        timeframeExists = False
        for dev in self.devices.values():
            msg += deviceStatusXML.format(
                power=dev.power,
                deviceName=html.escape(dev.deviceName),
                status=dev.status,
                deviceId=dev.deviceId,
                emSignalsAccepted=self.bool2str(dev.emSignalsAccepted),
            )
            if len(dev.timeframes) > 0:
                timeframeExists = True

        if timeframeExists:
            msg += "<PlanningRequest>"
            for dev in self.devices.values():
                for tf in dev.timeframes:
                    msg += timeFrameXml.format(
                        deviceId=dev.deviceId,
                        deviceName=dev.deviceName,
                        minrunningtime=tf.minRunningTime,
                        maxrunningtime=tf.maxRunningTime,
                        start=tf.start,
                        stop=tf.stop,
                        startSec=max(0, int((tf.start - now).total_seconds())),
                        stopSec=max(0, int((tf.stop - now).total_seconds())),
                    )
            msg += "</PlanningRequest>"
        msg += sempXMLend
        self.sempSchema.validate(msg)
        return web.Response(text=msg, content_type="text/xml")

    async def startWebserver(self):
        async def middleware_factory(app, handler):
            async def middleware_handler(request):
                print(request)
                print(
                    f"Request: {request.method} {request.rel_url} {request.remote} {request.raw_headers}"
                )
                return await handler(request)

            return middleware_handler

        #        logging.basicConfig(level=logging.ERROR)
        app = web.Application(middlewares=[middleware_factory])

        # TODO
        # Request all information (DeviceInfo, DeviceStatus, PlanningRequests of all devices):
        # o HTTP GET: <baseURL>/
        # Request DeviceInfo of all devices:
        # o HTTP GET: <baseURL>/DeviceInfo
        # Request DeviceInfo of specific device:
        # o HTTP GET: <baseURL>/DeviceInfo?DeviceId=<DeviceID>
        # Request DeviceStatus of all devices:
        # o HTTP GET: <baseURL>/DeviceStatus
        # Request DeviceStatus of specific device:
        # o HTTP GET: <baseURL>/DeviceStatus?DeviceId=<DeviceID>
        # Request PlanningRequest of all devices:
        # o HTTP GET: <baseURL>/PlanningRequest
        # Request PlanningRequest of specific device:
        # o HTTP GET: <baseURL>/PlanningRequest?DeviceId=<DeviceID>
        app.add_routes(
            [
                web.get("/", self.getStatusPage),
                web.get("/uuid:" + self.uuid + "/description.xml", self.getUUIDPage),
                web.get("/semp/", self.getSemp),
                web.post("/semp/", self.postSemp),
            ]
        )
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.addr, self.port)
        await site.start()

    def addDevice(self, device: sempDevice):
        self.devices[device.deviceId] = device

    def removeDevice(self, deviceId: str):
        del self.devices[sempDevice.deviceId]

    def getDevice(self, deviceId: str):
        print(self.devices, deviceId)
        return self.devices.get(deviceId, None)


# sempXMLend
