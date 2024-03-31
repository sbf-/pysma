from pysma.definitions_speedwire import commands, responseDef
from typing import List, Tuple
from pysma.device_speedwire import SMAspeedwireINV
import json
import base64
import logging
import sys
import asyncio

class Test_speedwire_class:
    """Test the Speedwire class."""

    async def test_basics(self) -> None:
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        sma = SMAspeedwireINV(host="192.0.2.1", password="xyz", group="user")
        await sma._createEndpoint()
        with open("tests/testdata/SW-Tripower.json", "r") as file:
            msgcounter = 0
            data = json.load(file)
            for t in data["msg"]:
                if t[0] != "RECV":
                    continue
                data = bytes.fromhex(t[2])
                sma._protocol._commandFuture = asyncio.get_running_loop().create_future()
                sma._protocol.datagram_received(data, ("192.0.2.1", 4711))
                msgcounter += 1
            debug = await sma.get_debug()
            assert len(sma._protocol.sensors)
            assert len(debug["msg"]) == msgcounter

    async def test_unique_responses(self) -> None:
        """ Test if no command is overlapping """
        ll:List[Tuple] = []
        for r in commands.values():
            if ("first" not in r or "last" not in r):
                continue
            t = (r["command"], r["first"], r["last"])
            for e in ll:
                if t[0] == e[0]:
                    overlap = list(set(range(t[1],t[2])) & set(range(e[1],e[2])))
                    if (len(overlap) > 0):
                        print("\n======================")
                        print(t)
                        print(e)
                        print(min(overlap),max(overlap))
                        for i in range(min(overlap), max(overlap)):
                            code = f"{i:08x}"
                            if code in responseDef:
                                print(f'   {responseDef[code]}')
            ll.append(t)


    # async def test_unique_command(self):
    #     cmds = set()
    #     duplicates = set()
    #     for r in commands.values():
    #       #  print(r)
    #         resp = f'{r["command"]:X}'
    #         if  resp in cmds:
    #             duplicates.add(resp)
    #         else:
    #             cmds.add(resp)
    #     print(duplicates)
    #     assert len(duplicates) == 0



    # def check(self) -> None:
    #     keysname = {}
    #     sensorname = {}
    #     for responses in responseDef.values():
    #         for response in responses:
    #             if "sensor" not in response or not isinstance(
    #                 response["sensor"], Sensor
    #             ):
    #                 continue
    #             sensor = response["sensor"]
    #             if sensor.key in keysname:
    #                 print("Doppelter SensorKey " + sensor.key)
    #                 raise RuntimeError("Doppelter SensorKey " + sensor.key)
    #             keysname[sensor.key] = 1
    #             if sensor.name in sensorname:
    #                 print("Doppelter SensorName " + sensor.name)
    #                 raise RuntimeError("Doppelter Sensorname " + sensor.name)
    #             sensorname[sensor.name] = 1

    #     keysname = {}
    #     sensorname = {}
    #     for x in commands.items():
    #         if "registers" not in x[1]:
    #             continue
    #         for r in x[1]["registers"]:
    #             if "name" in r:
    #                 name = r["name"]
    #                 if name in keysname:
    #                     print("Doppelter Keyname " + name)
    #                     raise RuntimeError("Doppelter Keyname " + name)
    #                 keysname[name] = 1
    #             if "sensor" in r:
    #                 sensor = r["sensor"]
    #                 if isinstance(sensor, Sensor) and sensor.key in sensorname:
    #                     print("Doppelter Sensorname " + sensor.key)
    #                     raise RuntimeError("Doppelter Sensorname " + sensor.key)
    #                 sensorname[name] = 1
