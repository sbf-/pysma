  

Um Werte von SMA-Geräten zu erhalten, werden verschiedene Wege beschritten. Die im Folgenden verwendeten Bezeichnungen sind teilweise von der Community geprägt und teilweise keine offiziellen Bezeichnungen von SMA.

  

  

# Unterstützte Schnittstellen

  

## Webconnect

  

Bei dieser Zugriffsart werden die Werte über die lokale Webseite des Wechselrichters abgerufen. Geräte, die den Webconnect-Standard unterstützen, verfügen in der Regel über einen lokalen Webserver. Dies ist bei vielen Geräten der Fall, die zwischen [Ende 2014](https://my.sma-service.com/s/article/Which-inverters-can-be-monitored-via-Webconnect?language=de) und 2023 veröffentlicht wurden.
* Voraussetzungen:<br>Zugangsdaten für die lokale Webseite müssen vorhanden sein (i.d.R. User- oder Installer-Account)
* Geräte:<br>z.B. Sunny Tripower Smart Energy, Sunny Boy Storage

  

  

## EnnoxOS

  

Neue Geräte ab ca. 2023 von SMA verwenden primär das Ennox Betriebssystem. Die Werte werden über die lokale Webseite abgerufen. Da sich das Webinterface im Vergleich zu Geräten mit Webconnect komplett geändert hat, wird ein neues Interface benötigt.

* Voraussetzungen:<br>Zugangsdaten für die lokale Webseite müssen vorhanden sein (Berechtigung User ist ausreichend).
* Hinweis:<br>Die Unterstützung des EVCharger konnte noch nicht getestet werden.
* Geräte:<br>Tripower X und EVCharger



## Speedwire Energymeter


Das SHM2 und die Engerymeter können nicht aktiv abgefragt werden, sondern übertragen die Daten selbstständig im Speedwire 0x6069 Format per Multicast  an alle Geräte des lokalen Netzwerkes. Die Programme müssen nur auf den Netzwerkverkehr hören und können dann die Werte dekodieren.

* Geräte:<br>Energymter 10 und 20 sowie Sunny Home Manager 2
*  Mehr Information:<br>[Spezifikation](https://cdn.sma.de/fileadmin/content/www.developer.sma.de/docs/EMETER-Protokoll-TI-en-10.pdf?v=1699276024)


## Speedwire

Fast alle SMA-Geräte mit einem Netzwerkanschluss unterstützen auch die Kommunikation über Speedwire.

Das genutze Protokoll 0x6065 ist jedoch nicht offen gelegt und die Implementierung beruht auf der Decodierung durch verschiedene Personen. Dabei wird nur unverschlüsselte Kommunikation unterstützt.

* Voraussetzungen:<br>Die Speedwire-Verschlüsselung darf nicht aktiviert sein.Außerdem kann es notwendig sein, das Passwort für den Benutzer "user" mit Hilfe des [Sunny Explorers](https://www.sma.de/produkte/monitoring-control/sunny-explorer) zu ändern. Standardmäßig ist dieses Passwort auf 0000 eingestellt.
* Hinweis:<br>Die Unterstützung ist noch nicht vollständig.<br>Falls möglich sollte auf die Webconnect oder Enneos-Schnittstelle zurückgegriffen werden.
* Geräte:<br>z.B. Sunny Island

  

# Nicht unterstützte Schnittstellen

## Modbus

Wird von den meisten Geräten unterstützt.Der Umfang der Unterstützung ist jedoch von Gerät zu Gerät sehr unterschiedlich. Erschwerend kommt hinzu, dass die Adressen, auf denen bestimmte Werte liegen, nicht einheitlich sind.

  

## Sunspec


(Sunspec)[https://sunspec.org/] ist ein herstellerunabhängiger Standard zur Bereitstellung bestimmter Werte von Wechselrichtern. Es basiert ebenfalls auf Modbus, jedoch sind hier die Adressen standardisiert. Je nach Gerät und Firmwarestand wird er unterstützt oder nicht.
