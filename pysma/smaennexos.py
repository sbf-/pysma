import asyncio
import copy
import json
import logging
from typing import Any, Dict, Optional


from aiohttp import ClientSession, ClientTimeout, client_exceptions, hdrs
from .sensor import Sensor
from . import definitions
from .const import (
    DEFAULT_TIMEOUT,
)
from .exceptions import (
    SmaAuthenticationException,
    SmaConnectionException,
    SmaReadException,
)
from .sensor import Sensors
from .device import Device
from .const import Identifier


# TODO Identifier.voltage_l1
ennexosSensors = [

    Sensor("Coolsys.Inverter.TmpVal.1", Identifier.temp_a, factor=1, unit="°C"),
    Sensor("Coolsys.Inverter.TmpVal.2", Identifier.temp_b, factor=1, unit="°C"),
    Sensor("Coolsys.Inverter.TmpVal.3", Identifier.temp_c, factor=1, unit="°C"),
    Sensor("DcMs.Amp.1", Identifier.pv_current_a, factor=1, unit="A"),
    Sensor("DcMs.Amp.2", Identifier.pv_current_b, factor=1, unit="A"),
    Sensor("DcMs.Amp.3", Identifier.pv_current_c, factor=1, unit="A"),
    Sensor("DcMs.TotDcEnCntWh.1", None, factor=1, unit=None),
    Sensor("DcMs.TotDcEnCntWh.2", None, factor=1, unit=None),
    Sensor("DcMs.TotDcEnCntWh.3", None, factor=1, unit=None),
    Sensor("DcMs.Vol.1", Identifier.pv_voltage_a, factor=1, unit="V"),
    Sensor("DcMs.Vol.2", Identifier.pv_voltage_b, factor=1, unit="V"),
    Sensor("DcMs.Vol.3", Identifier.pv_voltage_c, factor=1, unit="V"),
    Sensor("DcMs.Watt.1", Identifier.pv_power_a, factor=1, unit="W"),
    Sensor("DcMs.Watt.2", Identifier.pv_power_b, factor=1, unit="W"),
    Sensor("DcMs.Watt.3", Identifier.pv_power_c, factor=1, unit="W"),
    Sensor("GridGuard.Cntry", None, factor=1, unit=None),
    Sensor("GridMs.A.phsA", Identifier.current_l1, factor=1, unit="A"),
    Sensor("GridMs.A.phsB", Identifier.current_l2, factor=1, unit="A"),
    Sensor("GridMs.A.phsC", Identifier.current_l3, factor=1, unit="A"),
    Sensor("GridMs.GriTyp", None, factor=1, unit=None),
    Sensor("GridMs.Hz", Identifier.frequency, factor=1, unit="Hz"),
    Sensor("GridMs.PhV.phsA", Identifier.voltage_l1, factor=1, unit="V"), 
    Sensor("GridMs.PhV.phsA2B", None, factor=1, unit=None),
    Sensor("GridMs.PhV.phsB", Identifier.voltage_l2, factor=1, unit="V"),
    Sensor("GridMs.PhV.phsB2C", None, factor=1, unit=None),
    Sensor("GridMs.PhV.phsC", Identifier.voltage_l3, factor=1, unit="V"),
    Sensor("GridMs.PhV.phsC2A", None, factor=1, unit=None),
    Sensor("GridMs.TotA", Identifier.current_total, factor=1, unit="A"),
    Sensor("GridMs.TotPFEEI", None, factor=1, unit=None),
    Sensor("GridMs.TotPFExt", None, factor=1, unit=None),
    Sensor("GridMs.TotPFPrc", None, factor=1, unit=None),
    Sensor("GridMs.TotVA", Identifier.grid_apparent_power, factor=1, unit="VA"),
    Sensor("GridMs.TotVAr", Identifier.grid_reactive_power, factor=1, unit="var"),
    Sensor("GridMs.TotW", Identifier.grid_power, factor=1, unit="W"),
    Sensor("GridMs.TotW.Pv", Identifier.pv_power, factor=1, unit="W"),
    Sensor("GridMs.VA.phsA", Identifier.grid_apparent_power_l1, factor=1, unit="VA"),
    Sensor("GridMs.VA.phsB", Identifier.grid_apparent_power_l2, factor=1, unit="VA"),
    Sensor("GridMs.VA.phsC", Identifier.grid_apparent_power_l3, factor=1, unit="VA"),
    Sensor("GridMs.VAr.phsA", Identifier.grid_reactive_power_l1, factor=1, unit="var"),
    Sensor("GridMs.VAr.phsB", Identifier.grid_reactive_power_l2, factor=1, unit="var"),
    Sensor("GridMs.VAr.phsC", Identifier.grid_reactive_power_l3, factor=1, unit="var"),
    Sensor("GridMs.W.phsA", Identifier.power_l1, factor=1, unit="W"),
    Sensor("GridMs.W.phsB", Identifier.power_l2, factor=1, unit="W"),
    Sensor("GridMs.W.phsC", Identifier.power_l3, factor=1, unit="W"),
    Sensor("InOut.GI1", None, factor=1, unit=None),
    Sensor("Inverter.VArModCfg.PFCtlVolCfg.Stt", None, factor=1, unit=None),
    Sensor("Isolation.FltA", Identifier.insulation_residual_current, factor=1000, unit="mA"),
    Sensor("Isolation.LeakRis", None, factor=1, unit="kOhm"), # TODO "pv_isolation_resistance"
    Sensor("Metering.TotFeedTms", None, factor=1, unit=None),
    Sensor("Metering.TotOpTms", None, factor=1, unit=None),
    Sensor("Metering.TotWhOut", Identifier.total_yield, factor=1000, unit="kWh"),
    Sensor("Metering.TotWhOut.Pv", Identifier.pv_gen_meter, factor=1000, unit="kWh"),
    Sensor("Operation.BckStt", None, factor=1, unit=None),
    Sensor("Operation.DrtStt", None, factor=1, unit=None),
    Sensor("Operation.Evt.Dsc", None, factor=1, unit=None),
    Sensor("Operation.Evt.EvtNo", None, factor=1, unit=None),
    Sensor("Operation.Evt.Msg", None, factor=1, unit=None),
    Sensor("Operation.EvtCntIstl", None, factor=1, unit=None),
    Sensor("Operation.EvtCntUsr", None, factor=1, unit=None),
    Sensor("Operation.GriSwCnt", None, factor=1, unit=None),
    Sensor("Operation.GriSwStt", None, factor=1, unit=None),
    Sensor("Operation.Health", None, factor=1, unit=None),
    Sensor("Operation.HealthStt.Alm", None, factor=1, unit=None),
    Sensor("Operation.HealthStt.Ok", None, factor=1, unit=None),
    Sensor("Operation.HealthStt.Wrn", None, factor=1, unit=None),
    Sensor("Operation.OpStt", None, factor=1, unit=None),
    Sensor("Operation.PvGriConn", None, factor=1, unit=None),
    Sensor("Operation.RstrLokStt", None, factor=1, unit=None),
    Sensor("Operation.RunStt", None, factor=1, unit=None),
    Sensor("Operation.StandbyStt", None, factor=1, unit=None),
    Sensor("Operation.VArCtl.VArModAct", None, factor=1, unit=None),
    Sensor("Operation.VArCtl.VArModStt", None, factor=1, unit=None),
    Sensor("Operation.WMaxLimSrc", None, factor=1, unit=None),
    Sensor("Operation.WMinLimSrc", None, factor=1, unit=None),
    Sensor("PvGen.PvW", None, factor=1, unit=None),
    Sensor("PvGen.PvWh", None, factor=1, unit=None),
    Sensor("Spdwr.ComSocA.Stt", None, factor=1, unit=None),
    Sensor("SunSpecSig.SunSpecTx.1", None, factor=1, unit=None),
    Sensor("Upd.Stt", None, factor=1, unit=None),
    Sensor("WebConn.Stt", None, factor=1, unit=None),
    Sensor("Wl.AcqStt", None, factor=1, unit=None),
    Sensor("Wl.AntMod", None, factor=1, unit=None),
    Sensor("Wl.ConnStt", None, factor=1, unit=None),
    Sensor("Wl.SigPwr", None, factor=1, unit=None),
    Sensor("Wl.SoftAcsConnStt", None, factor=1, unit=None),
    Sensor("Setpoint.PlantControl.InOut.GO1", None, factor=1, unit=None)
]
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

        #_LOGGER.debug("Sending Request to %s: %s", url, parameters)

        try:
                async with self._aio_session.request(
                    method,
                    url,
                    timeout=ClientTimeout(total=DEFAULT_TIMEOUT),
                    **parameters
                ) as res:
                    if (res.status == 401):
                        raise SmaAuthenticationException(
                            f"Token failed!"
                        )
                    res = await res.json()
                   # _LOGGER.debug("Received reply %s", res)
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
        if "access_token" not in ret:
            raise SmaAuthenticationException(f"Login failed!")
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
        for s in ennexosSensors:
            if s.name:
                device_sensors.add(copy.copy(s))
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
        data = None
        try:
            data = await self._get_livedata()
        except SmaAuthenticationException as e:
            # Relogin
            _LOGGER.debug("Re-login .. Starting new Session")
            await self.new_session()
            data = await self._get_livedata()

        for sen in sensors:
            if sen.enabled:
                if sen.key in data:
                    value = data[sen.key]["value"]
                    if (sen.factor):
                        value = round(value/sen.factor,4)
                    sen.value = value
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
