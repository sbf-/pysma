# pysma2mqtt

Script which reads out the current measured values of an SMA device and makes them available via MQTT.

The Python script is a _proof of concept_.



## Usage
To install the libraries necessary for the script, the following instruction must be executed.

      python -m venv venv
      . venv/bin/activate
      pip install -r requirements.txt

To run it      

      python3 pysma2mqtt.py mqtt://username:password@hostname/pysma2mqtt ennexos usernameInverter passwordInverter ipInverter

      python3 pysma2mqtt.py mqtt://username:password@hostname/pysma2mqtt webconnect userORinstaller passwordInverter ipInverter

      python3 pysma2mqtt.py mqtt://username:password@hostname/pysma2mqtt speedwire userORinstaller passwordInverter ipInverter

      python3 pysma2mqtt.py mqtt://username:password@hostname/pysma2mqtt energymeter
