# pysma-plus library

Unofficial and unaffiliated Python 3 library to retrieve data from various [SMA](https://www.sma.de/) devices.
Based on the Webconnect implementation of the [pysma lib from kellerza](https://github.com/kellerza/pysma), the number of supported devices has been massively increased by this implementation.

This library is the basis for:
* [HA-pySmaPlus -- Home Assistant Integration](https://github.com/littleyoda/ha-pysmaplus)
* [LoxBerry SMA Plugin](https://wiki.loxberry.de/plugins/sma2loxone/start)

Supported Devices:
* Devices with Webconnect-Interface
* Devices based on ennexOS e.g. the Tripower X series released in 2022
* SMA Energy Meter (EMETER-10, EMETER-20) und Sunny Home Manager 2.0 (hm-20/shm2)
* Almost all SMA devices through the use of Speedwire (sometimes with a reduced range of measured values compared to the other interfaces)

The long-term goal is to integrate the change into the original library.


## Example usage

See [example.py](./example.py) for a basic usage and tests

## Successfully tested devices

| Bereich | Gerät | Method |
|--|--|--|
| Wechselrichter | Tripower X (STP XX-50)<br>(12,15,25) | ennexos |
| Wechselrichter | Tripower (STP XX)<br>(8,10) | speedwireINV |
| Hybrid-Wechselrichter | Sunny Tripower Smart Energy<br>(10.0)  | webconnect |
| Hybrid-Wechselrichter | Sunny Boy Storage<br>(SBS3.7-10, SBS5.0-10) | webconnect |
| Hybrid-Wechselrichter | Sunny Boy Smart Energy 5.0 | ennexos |
| Batterie-Wechselrichter | Sunny Island 8.0H (SI 8.0H-12) | webconnect |
| Energy Meter | Energy Meter 2<br>(EMTER 20) | speedwireEM |
| Energy Meter | Sunny Home Manager 2<br>(SHM2) | speedwireEM |
| | | |
 
