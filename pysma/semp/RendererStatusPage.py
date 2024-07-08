import html
import json

from aiohttp import web

from .const import debugHTML, hintsHTML, tabHTML


def getLastRequests(history, devices, devicesName):
    out = "<h2>Last SEMP-Requests from SHM</h2>"
    if len(history) == 0:
        out += "None<br>"
    else:
        out += "<table><thead><tr><th>Time</th>\n"
        for d in devices:
            out += f"<th>{d[11:23]}<br>{devicesName[d].deviceName}</th>\n"
        out += "<th>Request IP</th></thead>\n<tbody>"

        for row in reversed(history):
            out += f"<tr><td>{row.time}</td>"
            for d in devices:
                value = ""
                if row.deviceData and d in row.deviceData:
                    value = f"{row.deviceData[d].power} ({row.deviceData[d].status})"
                if row.cmdData and d in row.cmdData:
                    value = f"Request: Turn {row.cmdData[d]['status']}"
                out += "<td>" + value + "</td>"
            out += f"<td>{row.remote} {row.typ}</td>"
            out += "</tr>"
        out += "</tbody></table>"
    return out


def getDeviceTab(dev):
    name = html.escape(dev.deviceName)
    out = "<pre>"
    out += json.dumps(
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
        },
        indent=4,
    )
    out += "</pre>"
    return tabHTML.format(tabname="tab" + name, data=out, check="")


async def statusPageRenderer(request: web.Request, deviceInfo, history):
    devicesSet = set()
    devicesName = {}
    for dataTuple in history:
        if dataTuple.deviceData:
            for devId in dataTuple.deviceData.keys():
                devicesSet.add(devId)
                if devId not in devicesName:
                    devicesName[devId] = dataTuple.deviceData[devId]
    devices = list(devicesSet)
    out = debugHTML

    out += "<h2>Current Status</h2>"
    out += "Select the device for more information:<br>"
    out += """<div class="container"><nav role="tab-control"><ul>"""

    out += '<li><label for="overview">Overview</label></li>'
    for dev in deviceInfo.values():
        out += f'<li><label for="tab{html.escape(dev.deviceName)}">{html.escape(dev.deviceName)}</label></li>'

    out += """ </ul></nav>  """
    out += '<div role="tabs"><section>\n'

    out += tabHTML.format(
        check='checked="checked"',
        tabname="overview",
        data=getLastRequests(history, devices, devicesName),
    )
    for dev in deviceInfo.values():
        out += getDeviceTab(dev)

    out += "\n</section></div>\n"
    out += hintsHTML
    return web.Response(text=out, content_type="text/html")
