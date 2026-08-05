# ESP32-CAM Fotoabruf für Windows

Das Programm fordert über den Endpunkt `/photo-capture` eine neue Aufnahme vom
ESP32-CAM an. Das empfangene JPEG wird direkt angezeigt und kann anschließend
mit einem Datums- und Zeitstempel im Dateinamen gespeichert werden.

## Start

`ESP32-CAM-Fotoabruf starten.bat` doppelt anklicken.

Die im Webserver-Modus angezeigte IP-Adresse eintragen und auf **Neues Foto
aufnehmen** klicken. Erfolgreich verwendete Adressen merkt sich das Programm in
der Auswahlliste.

Voraussetzungen sind Python 3 mit Tkinter und das Python-Paket `Pillow`.
