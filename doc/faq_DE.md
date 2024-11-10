Inhaltsverzeichnis
- [Welche Geräte werden unterstützt?](#welche-geräte-werden-unterstützt)
- [Die verschiedenen Zugriffsmethoden](#die-verschiedenen-zugriffsmethoden)
  - [Webconnect ("webconnect")](#webconnect-webconnect)
  - [EnnexOS ("ennexos")](#ennexos-ennexos)
  - [Speedwire 0x6065 ("speedwireinv")](#speedwire-0x6065-speedwireinv)
  - [Speedwire EM 0x6069 ("energymeter", vormals "speedwireem")](#speedwire-em-0x6069-energymeter-vormals-speedwireem)
  - [Modbus Sunny Home Manager 2 ("shm2")](#modbus-sunny-home-manager-2-shm2)
  - [Einschränkungen:](#einschränkungen)
- [Und welche Zugriffsmethode/Interface nehme ich nun?](#und-welche-zugriffsmethodeinterface-nehme-ich-nun)
- [Probleme](#probleme)
  - [Energy Meter (Sunny Home Manager 2) wird nicht gefunden](#energy-meter-sunny-home-manager-2-wird-nicht-gefunden)
- [Unterstützung](#unterstützung)

# Unterstützung

Da die Implementierung doch recht aufwendig war, würde ich mich über eine kleine Aufmerksamkeit freuen:
https://littleyoda.github.io/

# Welche Geräte werden unterstützt?
Es werde fast alle SMA Wechselrichter unterstützt, die über einen Netzwerkanschluss verfügen. 

Eine unvollständige Liste:

| Bereich | Gerät | Methode | Anmerkrungen |
|--|--|--|--|
| Wechselrichter | [Tripower X (STP XX-50)](https://www.sma.de/produkte/solar-wechselrichter/sunny-tripower-x)<br>(12,15,20,25) | ennexos, speedwire |
| Hybrid-Wechselrichter | [Sunny Tripower Smart Energy](https://www.sma.de/produkte/hybrid-wechselrichter/sunny-tripower-smart-energy)<br>(10.0)  | webconnect, speedwire |
| Hybrid-Wechselrichter | [Sunny Boy Storage](https://www.sma.de/produkte/batterie-wechselrichter/sunny-boy-storage-37-50-60)<br>(SBS3.7-10, SBS5.0-10) | webconnect, speedwire |
| Hybrid-Wechselrichter | [Sunny Boy Smart Energy](https://www.sma.de/produkte/hybrid-wechselrichter/sunny-boy-smart-energy)<br>(5.0)| ennexos- speediwre |
| | | |
| Batterie-Wechselrichter | [Sunny Island](https://www.sma.de/produkte/batterie-wechselrichter/sunny-island-44m-60h-80h) <br>(4.4M) | speedwire
| Energy Meter | [Energy Meter 2](https://www.sma.de/produkte/monitoring-control/sma-energy-meter)<br>(EMTER 20) | energymeter (speedwireEM) |
| Energy Meter | [Sunny Home Manager 2](https://www.sma.de/produkte/monitoring-control/sunny-home-manager)<br>(SHM2) | energymeter (speedwireEM) |
| | | |
| Wallbox | EVC22-3AC-10 | ennexos | Noch unvollständig implementiert

# Die verschiedenen Zugriffsmethoden
Da jedes Geräte unterschiedliche Intnerfaces zur Verfügung stellt, muss bei dieser Integration ausgewählt werden, welches Interface gentutz werden soll.

## Webconnect ("webconnect")
Obwohl diese Schnittstelle Webconnect heißt, wird das Webconnect-Protokoll *nicht* verwendet.
Webconnect beschreibt hier nur eine Gerätegeneration, die mit einem Webinterface ausgestattet ist.
Über dieses Webinterface werden die Daten abgefragt.

Geräte: z.B. Sunny Tripower Smart Energy , Sunny Boy Storage

Netzwerk-Protokoll: TCP/IP, je nach Generation http oder https

API-Interface-Name: webconnect 


## EnnexOS ("ennexos")

Die neuen Geräte (Tripower X und EVCharger) von SMA verwenden hauptsächlich das Ennox Betriebssystem. Ein Webserver, der die Werte liefert, ist vorhanden. Da sich das Webinterface im Vergleich zum Webconnect komplett geändert hat, musste ein neuer Adapter geschrieben werden, um die Daten abzurufen.

Geräte: z.B. Tripower X, EVCharger, Sunny Boy Smart Energy

Netzwerk-Protokoll: TCP/IP, https

API-Interface-Name: ennexos

## Speedwire 0x6065 ("speedwireinv")
Fast alle SMA Wechselrichter unterstützen standardmäßig die Kommunikation per Speedwire. Dieses Protokoll 0x6065 ist aber nicht offen gelegt und ein paar Personen haben versucht, zumindest die unverschlüsselte Version des Protokolls zu dekodieren. Stand heute (Q3 2024) ist es nur möglich, Werte auszulesen. Das Verändern von Werten ist über diesen Weg aktuell nicht möglich. 

Voraussetzungen: Die Speedwire-Verschlüsselung darf nicht aktiviert werden. Defaultmäßig ist dieser für die User-Gruppe auf 0000 und für die Installer-Gruppe auf 1111 eingestellt.

Geräte: alle, insbesondere Geräte, die von den anderen Interfaces nicht unterstützt werden z.B. Sunny Island. Jedoch nicht die Energymeter.


Netzwerk-Protokoll: UDP

API-Interface-Name: speedwireinv

## Speedwire EM 0x6069 ("energymeter", vormals "speedwireem")
Der SHM2 und die Engerymeter übermittelt von sich aus die Daten per Multicast im Speedwire 0x6069 Format. Die Programme müssen hierbei nur auf den Netzwerktraffik lauschen und können die Werte dann dekodieren. Das Format für dieses eine Nachrichten Format hat SMA mittlerweile offen gelegt.

Geräte: Energymeter + Sunny Home Manager 2

Netzwerk-Protokoll: Multicast

API-Interface-Name: speedwireem


[Protokoll-Definition](https://cdn.sma.de/fileadmin/content/www.developer.sma.de/docs/EMETER-Protokoll-TI-en-10.pdf?v=1699276024)


## Modbus Sunny Home Manager 2 ("shm2")
Dieses Interface sollte nur in ausgewählten Spezialfällen genutzt werden. In 99% der Fälle sollte das "enerymeter" Interface genutzt werden.

Zur Nutzung dieses Interfaces wird eine besondere Freigabe ("Grid Guard Code") von SMA benötigt, da dieser Weg normalerweise für Vierteilnetzbetreiber reserviert ist. Über "shm2" werden weniger Informationen als über "energymeter" geliefert, dafür ist aber die Einspeisung ins Netz steuerbar.

Geräte: Sunny Home Manager 2

Netzwerk-Protokoll: TCP/IP; Modbus/TCP

API-Interface-Name: shm2

[Protokoll-Definition](https://files.sma.de/downloads/HM-20-Modbus-NSD-TI-en-12.pdf)
## Einschränkungen:

Da alle Schnittstellen, außer Energy Meter, ohne offizielle Unterlagen von SMA entschlüsselt wurden, kann immer etwas falsch interpretiert werden. Außerdem sind die Schnittstellen im Zweifelsfall nicht vollständig. Insbesondere die Implementierung von Speedwire ist noch unvollständig.

Speedwire hat zur Zeit den kleinsten Umfang an Sensoren, so dass EnnexOS oder Speedwire bevorzugt verwendet werden sollte.
Speedwire ist für Geräte gedacht, die keine andere Schnittstelle unterstützen oder als Fallback.

# Und welche Zugriffsmethode/Interface nehme ich nun?

* Es soll ein Sunny Home Manager 2 oder ein Energymeter 10/20 angesprochen werden:
  
  => energymeter
* Das Gerät hat eine Weboberfläche und es stammt aus der Webconnect-Generation (ca. vor 2022):

  => webconnect
* Das Gerät hat eine Weboberfläche und es hat ein ennexos Betriebssystem (neue Produktserien seit ca. 2022; Tripower X, Sunny Boy Smart Energy)

  => ennexos 

* sonst
  
  => speedwireinv

# Probleme
## Energy Meter (Sunny Home Manager 2) wird nicht gefunden
Die Energy Meter (einschließlich Sunny Home Manager 2) versenden ihre Daten per [Multicast](https://de.wikipedia.org/wiki/Multicast#IP-Multicast). 

Wenn die Informationen nicht empfangen werden, gibt es verschiedene Gründe:
1.) Deshalb müssen diese Geräte und das Gerät, welches die Daten empfangen soll, im gleichen [Subnetz](https://de.wikipedia.org/wiki/Subnetz) liegen. Also z.B. in 192.168.2.X. Da die Daten nicht aktiv abgerufen werden können, kann keine Verbindung über die IP-Adresse aufgebaut werden.

2.) Teilweise werden die Pakete nicht empfangen, da es zu Inkompatbilitäten mit den Netzwerkgeräten (Router/Switches/AP) kommt.

3.) Im Falle einer virtuellen Umgebung muss sichergestellt sein, dass die Multicast Systeme auch an die virtuelle Umgebung weitergeleitet werden.

Experten können in diesen Fällen aber auch die Energy Meters von Multicast auf Unicast umstellen. Die Geräte senden dann die Daten nur noch an die ausgewählten IP Adressen und nicht mehr per Multicast an alle Geräte des Subnetzes. Hierdurch können Subnetzte überwunden und Probleme mit den Netzwerkgeräten vermieden werden. 

Es können jedoch nur 3 Geräte(=IP) eingetragen werden. Es muss aber sicher gestellt sein, dass alle Geräte eingetragen sind, die die Informationen der Energy Meter erhalten müssen. In der Regel sind dies die Wechselrichter, Batteriesystem und evtl. der SMA-EV-Charger. Dazu dann noch dein Smart-Home-System, falls dieses auch die SHM-Daten auswertet.

Diese Lösung funktioniert also nur, wenn du eine, von der Geräteanzahl her, kleine Anlage hast.

Merke:
* Solange es keine Probleme mit Multicast gibt, gibt es keinen Grund, auf Unicast zu wechseln.
* Ein Wechsel auf Unicast funktioniert nur, wenn du max. 3 Geräte hast, die auf die Daten des SHM angewiesen sind.
* Wenn du irgendein Gerät in der Liste vergisst, das die Information brauchst, werden komische Effekte auftreten.

Bitte vor der Änderung die Anleitung lesen und Änderungen auf eigene Gefahr.
Sunny Portal => Konfiguration => Geräteübersicht => Symbol Eigenschaft => Button Bearbeiten 


## Die verschiedenen Begrifflichkeiten verwirren mich
Die Begrifflichkeiten sind historisch gewachsen. Die folgende Tabelle soll helfen:

Beschreibung | API-Interface | Begriff für Userdialoge | Auch genutzte Namen
-- | -- | -- | --
Devices of the Webconnect generation | webconnect | webconnect |  
Devices of the ennexos generation | ennexos | ennexos |  
Energymeters | speedwireem | energymeter | speedwireem, speedwire, speedwire 0x6069
Devices with speedwire Interface | speedwireinv | speedwire | speedwireinv, speedwire, speedwire 0x6065
Sunny Home Manager with Grid Guard Code | shm2 | shm2 grid guard code |  

