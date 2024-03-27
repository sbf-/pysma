import asyncio
import copy
import json
import logging
from typing import Any, Dict, Optional


#import jmespath  # type: ignore
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
from .device import Device

_LOGGER = logging.getLogger(__name__)
class SMAennexos(Device):
    """Class to connect to the ennexos based SMA inverters. (e.g. Tripower X Devices)"""

    # pylint: disable=too-many-instance-attributes
    _aio_session: ClientSession
    _new_session_data: Optional[dict]
    _url: str
    _token: str
    _authorization_header: str


    def __init__(
        self,
        session: ClientSession,
        url: str,
        password: Optional[str],
        group: str,
    ):
        """Init SMA connection.

        Args:
            session (ClientSession): aiohttp client session
            url (str): Url or IP address of device
            password (str, optional): Password to use during login.
            group (str, optional): Username to use during login. 

        """
        self._url = url.rstrip("/")
        if not url.startswith("http"):
            self._url = "http://" + self._url
        self._new_session_data = {"user": group, "pass": password}
        self._aio_session = session



    async def _jsonrequest(
        self, url: str, parameters: Dict[str, Any], method: str = hdrs.METH_POST
    ) -> dict:
        """Request json data for requests.

        Args:
            url (str): URL to do request to
            parameters (Dict[str, Any]): parameters
            method (str): Post or Get-Request

        Raises:
            SmaConnectionException: Connection to device failed
            SmaAuthenticationException: Authentication failed

        Returns:
            dict: json returned by device
        """

        _LOGGER.debug("Sending Request to %s: %s", url, parameters)

        try:
                async with self._aio_session.request(
                    method,
                    url,
                    timeout=ClientTimeout(total=DEFAULT_TIMEOUT),
                    **parameters
                ) as res:
                    if ("Content-Length" in res.headers and res.headers["Content-Length"] == '0'):
                        raise SmaAuthenticationException(
                            f"Login failed!"
                        )
                    res = await res.json()
                    _LOGGER.debug("Received reply %s", res)
                    return res
        except SmaAuthenticationException as e:
                raise e
        except (client_exceptions.ContentTypeError, json.decoder.JSONDecodeError):
            _LOGGER.warning("Request to %s did not return a valid json.", url)
        except client_exceptions.ServerDisconnectedError as exc:
            raise SmaConnectionException(
                f"Server at {self._url} disconnected."
            ) from exc
        except (
            client_exceptions.ClientError,
            asyncio.exceptions.TimeoutError,
        ) as exc:
            raise SmaConnectionException(
                f"Could not connect to SMA at {self._url}: {exc}"
            ) from exc
        return {}

    def unit_of_measurement(self, name):
        if (name.endswith("TmpVal")):
            return "°C"
        if (".W." in name):
            return "W"
        if (".TotWh" in name):
            return "Wh"
        if (name.endswith(".TotW")):
            return "W"
        if (name.endswith(".TotW.Pv")):
            return "W"
        if (name.endswith(".Watt")):
            return "W"
        if (".A." in name):
            return "A"
        if (name.endswith(".Amp")):
            return "A"
        if (name.endswith(".Vol")):
            return "V"
        if (name.endswith(".VA.")):
            return "VA"
        _LOGGER.debug("No unit of measurement for " + name)
        return ""


    async def new_session(self) -> bool:
        """Establish a new session.

        Returns:
            bool: authentication successful
        """

        loginurl = self._url + '/api/v1/token'
        postdata = {'data':{'grant_type': 'password',
                'username': self._new_session_data["user"],
                'password': self._new_session_data["pass"],
                }}
        ret = await self._jsonrequest(loginurl,postdata)
        self._token = ret["access_token"]
        self._authorization_header = { "Authorization" : "Bearer " + self._token } 

        _LOGGER.debug("Login successfull")
        return True

    async def _get_livedata(self) -> Dict:
        liveurl = self._url + '/api/v1/measurements/live'
        postdata = { 
             'data': '[{"componentId":"IGULD:SELF"}]',
             'headers': self._authorization_header
        }
        ret = await self._jsonrequest(liveurl,postdata)
        device_sensors = Sensors()
        data = {}
        for d in ret:
            dname = d["channelId"].replace("Measurement.","").replace("[]", "")
            if "value" in d["values"][0]:
                v = d["values"][0]["value"]
                if self._isfloat(v):
                     v = round(v,2)
                data[dname] = {
                        "name": dname,
                        "value": v,
                        "origname": d["channelId"] 
                    }
            elif "values" in d["values"][0]:
                # Split Value-Arrays
                for idx in range(0, len(d["values"][0]["values"])):
                    v = d["values"][0]["values"][idx]
                    if self._isfloat(v):
                        v = round(v,2)
                    idxname = dname + "." + str(idx + 1)
                    data[idxname] = {
                            "name": idxname,
                            "value": v,
                            "origname": d["channelId"] 
                    }
            else:
                # Value current not available // night?
                # TODO
                pass
        return data
    


    async def get_sensors(self) -> Sensors:
        """Get the sensors that are present on the device.

        Returns:
            Sensors: Sensors object containing Sensor objects
        """
        device_sensors = Sensors()
        ret = await self._get_livedata()
        for s in ret.items():
            #TODO Create correct Sensor Instances
            device_sensors.add(Sensor(
                s[1]["origname"], 
                s[1]["name"], 
                unit = self.unit_of_measurement(s[1]["origname"]), 
                enabled = False))
        return device_sensors


    async def close_session(self) -> None:
        """Close the session login."""
        # TODO
        pass

    def _isfloat(self,num):
        try:
            float(num)
            return True
        except ValueError:
            return False


    async def read(self, sensors: Sensors) -> bool:
        """Read a set of keys.

        Args:
            sensors (Sensors): Sensors object containing Sensor objects to read

        Returns:
            bool: reading was successful
        """
        notfound = []
        data = await self._get_livedata()
        for sen in sensors:
            if sen.enabled:
                if sen.name in data:
                    sen.value = data[sen.name]["value"]
                    continue
                notfound.append(f"{sen.name} [{sen.key}]")

        if notfound:
            _LOGGER.info(
                "No values for sensors: %s",
                ",".join(notfound),
            )

        return True



    async def device_info(self) -> dict:
        """Read device info and return the results.

        Returns:
            dict: dict containing serial, name, type, manufacturer and sw_version
        """
        url = self._url + '/api/v1/plants/Plant:1/devices/IGULD:SELF'
        requestdata = { 
             'headers': self._authorization_header
        }
        dev = await self._jsonrequest(url,requestdata, hdrs.METH_GET)
        device_info = {
            "serial": dev["serial"],
            "name": dev["product"],
            "type": dev["name"],
            "manufacturer": dev["vendor"],
            "sw_version": dev["firmwareVersion"],
        }
        return device_info
