"""SMA WebConnect library for Python.

See: http://www.sma.de/en/products/monitoring-control/webconnect.html

Source: http://www.github.com/kellerza/pysma
"""
import asyncio
import copy
import json
import logging
from typing import Any, Dict, Optional

import jmespath  # type: ignore
from aiohttp import ClientSession, ClientTimeout, client_exceptions, hdrs
from .sensor import Sensor
from . import definitions
from .const import (
    DEFAULT_LANG,
    DEFAULT_TIMEOUT,
    DEVICE_INFO,
    ENERGY_METER_VIA_INVERTER,
    FALLBACK_DEVICE_INFO,
    GENERIC_SENSORS,
    OPTIMIZERS_VIA_INVERTER,
    URL_ALL_PARAMS,
    URL_ALL_VALUES,
    URL_DASH_LOGGER,
    URL_DASH_VALUES,
    URL_LOGGER,
    URL_LOGIN,
    URL_LOGOUT,
    URL_VALUES,
    USERS,
)
from .exceptions import (
    SmaAuthenticationException,
    SmaConnectionException,
    SmaReadException,
)
from .helpers import version_int_to_string
from .sensor import Sensors
from .smawebconnect import SMAwebconnect
from .smaennexos import SMAennexos
from .smaspeedwireem import SMAspeedwireEM
from .device import Device
_LOGGER = logging.getLogger(__name__)


# Backward compatibility
def SMA(session, url, password, group):
    return SMAwebconnect(session, url, password=password, group=group)


def getDevice(session: ClientSession,
        url: str,
        password: Optional[str] = None,
        groupuser: str = "user",
        accessmethod: str = "webconnect"
    ) -> Device:
        _LOGGER.debug(f"Device Called! Url: {url} User/Group: {groupuser} Accessmethod: {accessmethod}")
        if (accessmethod == "webconnect"):
            return SMAwebconnect(session, url, password=password, group=groupuser)
        elif (accessmethod == "ennexos"):
            return SMAennexos(session, url, password=password, group=groupuser)
        elif (accessmethod == "speedwire"):
              return SMAspeedwireEM()
        else:
             return None
