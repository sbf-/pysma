
# pysma-plus library

Python 3 library to retrieve data from various SMA](https://www.sma.de/) devices.
Based on a fork of the [pysma lib from kellerza](https://github.com/kellerza/pysma).
The long-term goal is to integrate the change into the original library.

SMA Webconnect library for Python 3. The library was created
to integrate SMA inverters with HomeAssistant

* Devices with Webconnect-Interface
* Devices based on  ennexOS
e.g. the Tripower X series released in 2022
* SMA Energy Meter (EMETER-10, EMETER-20) und ### Sunny Home Manager 2.0 (shm2)


## Example usage

See [example.py](./example.py) for a basic usage and tests

## Successfully tested devices

| Bereich | Gerät | Methode |
|--|--|--|
| Wechselrichter | Tripower X (STP XX-50)<br>(15,25) | ennexos |
| Hybrid-Wechselrichter | Sunny Tripower Smart Energy<br>(10.0)  | webconnect |
| Hybrid-Wechselrichter | Sunny Boy Storage<br>(SBS3.7-10, SBS5.0-10) | webconnect |
| | | |
| Energy Meter | Energy Meter 2<br>(EMTER 20) | speedwireEM |
| Energy Meter | Sunny Home Manager 2<br>(SHM2) | speedwireEM |
| | | |
 

