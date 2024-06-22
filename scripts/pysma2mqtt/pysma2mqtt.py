#!/usr/bin/env python
"""Basic usage example and testing of pysma."""
import argparse
import asyncio
import logging
import queue
import signal
import sys
from typing import Any
from urllib.parse import urlparse

import aiohttp
from aiomqtt import Client, ProtocolVersion

import pysmaplus as pysma
from pysmaplus.sensor import Sensors

# This example will work with Python 3.9+

_LOGGER = logging.getLogger(__name__)

VAR: dict[str, Any] = {}
log_queue: queue.Queue = queue.Queue()


def print_table(sensors: Sensors) -> None:
    """Print sensors formatted as table."""
    if len(sensors) == 0:
        print("No Sensors found!")
    for sen in sensors:
        if sen.value is None:
            print("{:>25}".format(sen.name))
        else:
            name = sen.name
            if sen.key:
                name = sen.key
            print(
                "{:>25}{:>15} {} {} {}".format(
                    name,
                    str(sen.value),
                    sen.unit if sen.unit else "",
                    sen.mapped_value if sen.mapped_value else "",
                    sen.range if sen.range else "",
                )
            )


async def setup_mqtt(config):
    if "://" not in config:
        config = "mqtt://" + config
    return urlparse(config)


async def main_loop(args: argparse.Namespace) -> None:
    """Run main loop."""
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        user = args.user
        password = args.password
        url = args.url
        accessmethod = args.accessmethod
        delay = args.delay
        options = (
            dict(map(lambda s: s.split("="), args.options)) if args.options else {}
        )

        mqtt_config = await setup_mqtt(args.mqtt)

        _LOGGER.debug(
            f"MainLoop called! Url: {url} User/Group: {user} Accessmethod: {accessmethod}"
        )
        VAR["sma"] = pysma.getDevice(session, url, password, user, accessmethod)
        assert VAR["sma"]
        VAR["sma"].set_options(options)
        try:
            await VAR["sma"].new_session()
        except pysma.exceptions.SmaAuthenticationException:
            _LOGGER.error("Authentication failed!")
            return
        except pysma.exceptions.SmaConnectionException:
            _LOGGER.error("Unable to connect to device at %s", url)
            return
        # We should not get any exceptions, but if we do we will close the session.
        try:
            VAR["running"] = True
            devicelist = await VAR["sma"].device_list()
            for deviceId, deviceData in devicelist.items():
                for name, value in deviceData.asDict().items():
                    if type(value) in [str, float, int]:
                        print("{:>17}{:>25}".format(name, value))
                print()

            sensors: dict[str, Sensors] = {}
            for deviceId in devicelist.keys():
                sensors[deviceId] = await VAR["sma"].get_sensors(deviceId)
                for sensor in sensors[deviceId]:
                    sensor.enabled = True
            print("Sending to MQTT...")
            async with Client(
                mqtt_config.hostname,
                port=mqtt_config.port if mqtt_config.port else 1883,
                username=mqtt_config.username,
                password=mqtt_config.password,
                identifier="12312312312",
                protocol=ProtocolVersion.V31,
                timeout=10,
            ) as client:
                while VAR.get("running"):
                    for deviceId in devicelist.keys():
                        try:
                            await VAR["sma"].read(sensors[deviceId], deviceId)
                            for sen in sensors[deviceId]:
                                name = sen.name if sen.name is not None else sen.key
                                if name is None:
                                    continue
                                await client.publish(
                                    f"{mqtt_config.path}/{deviceId}/{name}",
                                    payload=sen.value,
                                )
                        #                        print_table(sensors[deviceId])
                        except TimeoutError as e:
                            print("Timeout", e)
                    await asyncio.sleep(delay)
        finally:
            _LOGGER.info("Closing Session...")
            await VAR["sma"].close_session()


def getVersion() -> str:
    versionstring = "unknown"
    from importlib.metadata import PackageNotFoundError, version

    try:
        versionstring = version("pysma-plus")
    except PackageNotFoundError:
        pass
    return versionstring


async def main() -> None:
    print("Library version: " + getVersion())
    parser = argparse.ArgumentParser(
        prog="python pysma2mqtt.py",
        description="Export the device data to mqtt.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-d",
        "--delay",
        type=float,
        default=2,
        help="Delay between two requests [seconds]",
    )

    parser.add_argument(
        "mqtt",
        help="MQTT Configuration (e.g. mqtt://username:pwd@localhost:1883/topic)",
    )

    subparsers = parser.add_subparsers(help="Supported devices", required=True)

    parser_a = subparsers.add_parser(
        "webconnect", help="Devices with Webconnect interface"
    )
    parser_a.add_argument("user", choices=["user", "installer"], help="Login username")
    parser_a.add_argument("password", help="Login password")
    parser_a.add_argument("url", type=str, help="Url or IP-Address")
    parser_a.set_defaults(accessmethod="webconnect")

    parser_b = subparsers.add_parser(
        "speedwire", help="Devices with Speedwire interface (unencrypted only)"
    )
    parser_b.add_argument("user", choices=["user", "installer"], help="Login username")
    parser_b.add_argument("password", help="Login password")
    parser_b.add_argument("url", type=str, help="Url or IP-Address")
    parser_b.set_defaults(accessmethod="speedwireinv")

    parser_c = subparsers.add_parser("ennexos", help="EnnexOs based Devices")
    parser_c.set_defaults(accessmethod="ennexos")
    parser_c.add_argument("user", help="Username")
    parser_c.add_argument("password", help="Login password")
    parser_c.add_argument("url", type=str, help="Hostname or IP-Address")

    parser_d = subparsers.add_parser("energymeter", help="Energy Meters")
    parser_d.set_defaults(user="")
    parser_d.set_defaults(password="")
    parser_d.set_defaults(url="")
    parser_d.set_defaults(accessmethod="speedwireem")

    parser_h = subparsers.add_parser(
        "shm2", help="Sunny Home Manager with Grid Guard Code"
    )
    parser_h.set_defaults(user="")
    parser_h.set_defaults(password="")
    parser_h.add_argument("url", type=str, help="IP-Address")
    parser_h.add_argument("password", type=str, help="Grid Guard Code")
    parser_h.set_defaults(accessmethod="shm2")

    for p in [parser_a, parser_b, parser_c, parser_d, parser_h]:
        p.add_argument(
            "-o",
            "--options",
            metavar="KEY=VALUE",
            nargs="+",
            help="Set module specific options",
        )
    args = parser.parse_args(args=None if sys.argv[1:] else ["--help"])

    def _shutdown(*_):
        VAR["running"] = False

    signal.signal(signal.SIGINT, _shutdown)
    await main_loop(args)


if __name__ == "__main__":
    asyncio.run(main())
