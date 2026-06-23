# Programme auf dem ESP32 über WLAN starten

Auf einem ESP32 können mehrere Programme gespeichert sein. Beim Einschalten führt MicroPython normalerweise zunächst `boot.py` und anschließend `main.py` aus. Möchte man ein anderes Programm starten, muss man es zum Beispiel mit Thonny auswählen oder über ein kleines Auswahlmenü in `main.py` aufrufen.

Das vorgestellte Programm richtet auf dem ESP32 einen eigenen Access Point ein. Dadurch kann der ESP32 per Handy, Tablet oder PC direkt angesprochen werden. Eine vom ESP32 bereitgestellte Webseite dient als Bedienoberfläche zur Programmauswahl und ermöglicht gegebenenfalls die Interaktion mit dem aktuell laufenden Programm.

Der Ablauf ist dabei:

1. Der ESP32 erzeugt ein eigenes WLAN.
2. Handy, Tablet oder PC verbinden sich mit diesem WLAN.
3. Eine Webseite dient als Bedienoberfläche.
4. Über diese Webseite kann ein Programm ausgewählt und gestartet werden.

[main.py](dateien/main.py)

[ADC_Messung.py](dateien/ADC_Messung.py)

[Digitaloszilloskop.py](dateien/Digitaloszilloskop.py)

