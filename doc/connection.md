If there are initial connection problems, the following steps can be carried out for testing.

If a Python environment is available, the library can be downloaded and the network can be searched for SMA devices.

```git clone -b tripowerX https://github.com/littleyoda/pysma/
cd pysma
ln -s pysma/ pysmaplus
python -m venv venv
. venv/bin/activate
pip install -e .
```

The following command can then be used to search the network for SMA devices and then start an identification. Not all SMA devices are found or identified in this way.  

```python3 example.py discovery --identify```

The output could look like this, for example:
```Library version: 0.2.8
Discovery...

192.0.2.81:9522
192.0.2.80:9522

Trying to identify... (can take up to 30 seconds pre device)

192.0.2.81
         Access              Remarks
        ennexos     found    https STP-15-50
   speedwireinv     maybe    only unencrypted Speedwire is supported
     webconnect    failed    https://192.168.2.81
     webconnect    failed    http://192.168.2.81

192.0.2.80
         Access              Remarks
        ennexos    failed    https
        ennexos    failed    http
   speedwireinv    failed    
     webconnect    failed    https://192.168.2.80
     webconnect    failed    http://192.168.2.80
```

The output shows that the device 192.0.2.81 can be accessed using the method ennexos or possibly also with speedwireinv.
The device 192.0.2.80 was not recognized. It may be an energy meter or the sunny home manager 2 (shm2).


If the devices were not found automatically with the discovery command, individual IP addresses can be scaned with the identifiy command:
```python3 example.py identify 192.0.2.55```

Once it has been clarified which method can be used to retrieve the measured values, the following commands could be used to display the measured values.

| Access method | command |
| ----------- | ----------- |
| ennexos | ```python3 example.py ennexos joe "password" https://192.0.2.81 ```|
| speedwire | ```python3 example.py speedwire user password 192.0.2.81``` |
| webconnect | ```python3 example.py webconnect user password https://192.0.2.81``` |
