"""Test pysma init."""
import asyncio
import logging
from unittest.mock import patch
import json

import aiohttp
import pytest
import base64
import time
from pysma.device_em import SMAspeedwireEM
from pysma.exceptions import (
    SmaAuthenticationException,
    SmaConnectionException,
    SmaReadException,
)

from . import MOCK_DEVICE, MOCK_L10N, mock_aioresponse

_LOGGER = logging.getLogger(__name__)

class Test_SMAEM_class:
    """Test the SMA class."""

    def fake_recv(self):
        time.sleep(0.6)
        with open("tests/testdata/SunnyHomeManager2.json", "r") as file:
            data = json.load(file)
            return base64.b64decode(data["packet"])

    @patch.object(SMAspeedwireEM, '_recv', fake_recv)
    async def test_json_timeout_error(self, mock_aioresponse):
         sma = SMAspeedwireEM()
         device_info = await sma.device_info()
         print(device_info)
         for key in ["manufacturer", "name", "serial", "sw_version", "type" ]:
            assert key in device_info 
            assert len(device_info[key]) > 0 if isinstance(device_info[key], str) else True
            assert device_info[key] > 0 if isinstance(device_info[key], int) else True
         sensors = await sma.get_sensors()
         assert len(sensors) >= 17
         await sma.read(sensors)

    async def test_debug(self):
         sma = SMAspeedwireEM()
         with open("tests/testdata/SunnyHomeManager2.json", "r") as file:
            data = json.load(file)
            packet = base64.b64decode(data["packet"])
            sma._last_packet = packet
            debug = await sma.get_debug()
            assert debug["packet"] == data["packet"]  

