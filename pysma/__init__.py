"""SMA WebConnect library for Python.

See: http://www.sma.de/en/products/monitoring-control/webconnect.html

Source: http://www.github.com/kellerza/pysma
"""

import logging
from typing import Optional
import asyncio
from aiohttp import ClientSession
from .device_webconnect import SMAwebconnect
from .device_ennexos import SMAennexos
from .device_speedwire import SMAspeedwireINV
from .device_em import SMAspeedwireEM
from .device import Device

_LOGGER = logging.getLogger(__name__)


# Backward compatibility
def SMA(session, url, password, group):
    return SMAwebconnect(session, url, password=password, group=group)


def getDevice(
    session: ClientSession,
    url: str,
    password: Optional[str] = None,
    groupuser: str = "user",
    accessmethod: str = "webconnect",
) -> Device:
    _LOGGER.debug(
        f"Device Called! Url: {url} User/Group: {groupuser} Accessmethod: {accessmethod}"
    )
    if accessmethod == "webconnect":
        return SMAwebconnect(session, url, password=password, group=groupuser)
    elif accessmethod == "ennexos":
        return SMAennexos(session, url, password=password, group=groupuser)
    elif (accessmethod == "speedwire") or (accessmethod == "speedwireem"):
        return SMAspeedwireEM()
    elif accessmethod == "speedwireinv":
        return SMAspeedwireINV(host=url, password=password, group=groupuser)
    else:
        return None


async def _runDetect(accessmethod: str, session: ClientSession, ip):
    sma = None
    if accessmethod == "webconnect":
        sma = SMAwebconnect(session, ip, password="", group="user")
    elif accessmethod == "ennexos":
        sma = SMAennexos(session, ip, password=None, group=None)
    elif accessmethod == "speedwireinv":
        sma = SMAspeedwireINV(host=ip, password="", group="user")
    ret = await sma.detect(ip)
    for i in ret:
        i["access"] = accessmethod
    try:
        await sma.close_session()
    except Exception:
        pass
    return ret


async def autoDetect(session: ClientSession, ip: str):
    ret = await asyncio.gather(
        _runDetect("ennexos", session, ip),
        _runDetect("speedwireinv", session, ip),
        _runDetect("webconnect", session, ip),
    )
    results = []
    for r in ret:
        results.extend(r)
    return results
