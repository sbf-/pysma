# Welche Geräte werden unterstützt?
Es werde fast alle SMA Wechselrichter unterstützt, die über einen Netzwerkanschluss verfügen. 

Eine unvollständige Liste:

| Bereich | Gerät | Methode | Anmerkrungen |
|--|--|--|--|
| Wechselrichter | Tripower X (STP XX-50)<br>(12,15,20,25) | ennexos, speedwire |
| Hybrid-Wechselrichter | Sunny Tripower Smart Energy<br>(10.0)  | webconnect, speedwire |
| Hybrid-Wechselrichter | Sunny Boy Storage<br>(SBS3.7-10, SBS5.0-10) | webconnect, speedwire |
| Hybrid-Wechselrichter | [Sunny Boy Smart Energy](https://www.sma.de/produkte/hybrid-wechselrichter/sunny-boy-smart-energy)<br>(5.0)| ennexos- speediwre | Messwerte der Batterie fehlen noch
| | | |
| Batterie-Wechselrichter | [Sunny Island](https://www.sma.de/produkte/batterie-wechselrichter/sunny-island-44m-60h-80h) <br>(4.4M) | speedwire
| Energy Meter | Energy Meter 2<br>(EMTER 20) | energymeter (speedwireEM) |
| Energy Meter | Sunny Home Manager 2<br>(SHM2) | energymeter (speedwireEM) |
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


## EnnexOS ("ennexos")

Die neuen Geräte (Tripower X und EVCharger) von SMA verwenden hauptsächlich das Ennox Betriebssystem. Ein Webserver, der die Werte liefert, ist vorhanden. Da sich das Webinterface im Vergleich zum Webconnect komplett geändert hat, musste ein neuer Adapter geschrieben werden, um die Daten abzurufen.

Geräte: z.B. Tripower X, EVCharger, Sunny Boy Smart Energy

Netzwerk-Protokoll: TCP/IP, https

## Speedwire 0x6065 ("speedwireinc")
Fast alle SMA Wechselrichter unterstützen standardmäßig die Kommunikation per Speedwire. Dieses Protokoll 0x6065 ist aber nicht offen gelegt und ein paar Personen haben versucht, zumindest die unverschlüsselte Version des Protokolls zu dekodieren.

Voraussetzungen: Die Speedwire-Verschlüsselung darf nicht aktiviert werden. Defaultmäßig ist dieser für die User-Gruppe auf 0000 und für die Installer-Gruppe auf 1111 eingestellt.

Geräte: alle, insbesondere Geräte, die von den anderen Interfaces nicht unterstützt werden z.B. Sunny Island. Jedoch nicht die Energymeter.


Netzwerk-Protokoll: UDP


## Speedwire EM 0x6069 ("energymeter", vormals "speedwireem")
Der SHM2 und die Engerymeter übermittelt von sich aus die Daten per Multicast im Speedwire 0x6069 Format. Die Programme müssen hierbei nur auf den Netzwerktraffik lauschen und können die Werte dann dekodieren. Das Format für dieses eine Nachrichten Format hat SMA mittlerweile offen gelegt.

Geräte: Energymeter + Sunny Home Manager 2

Netzwerk-Protokoll: Multicast


## Einschränkungen:

Da alle Schnittstellen, außer Energy Meter, ohne offizielle Unterlagen von SMA entschlüsselt wurden, kann immer etwas falsch interpretiert werden. Außerdem sind die Schnittstellen im Zweifelsfall nicht vollständig. Insbesondere die Implementierung von Speedwire ist noch unvollständig.

Speedwire hat zur Zeit den kleinsten Umfang an Sensoren, so dass EnnexOS oder Speedwire bevorzugt verwendet werden sollte.
Speedwire ist für Geräte gedacht, die keine andere Schnittstelle unterstützen oder als Fallback.


# Probleme
## Energy Meter (Sunny Home Manager 2) wird nicht gefunden
Die Energy Meter (einschließlich Sunny Home Manager 2) versenden ihre Daten per [Multicast](https://de.wikipedia.org/wiki/Multicast#IP-Multicast). Deshalb müssen diese Geräte und das Gerät, welches die Daten empfangen soll, im gleichen [Subnetz](https://de.wikipedia.org/wiki/Subnetz) liegen. Also z.B. in 192.168.2.X. Da die Daten nicht aktiv abgerufen werden können, kann keine Verbindung über die IP-Adresse aufgebaut werden.

Experten können die Energy Meters von Multicast auf Unicast umstellen. Die Geräte senden dann die Daten nur noch an die ausgewählten IP Adressen und nicht mehr per Multicast an alle Geräte des Subnetzes. Hierdurch können Subnetzte überwunden werden. Hierbei ist sicher zu stellen, dass man alle Geräte einträgt, die die Informationen der Energy Meter erhalten müssen. Bitte vor der Änderung die Anleitung lesen.

Sunny Portal => Konfiguration => Geräteübersicht => Symbol Eigenschaft => Button Bearbeiten 

# Unterstützung

Da die Implementierung doch recht aufwendig war, würde ich mich über eine kleine Aufmerksamkeit freuen:
https://littleyoda.github.io/
