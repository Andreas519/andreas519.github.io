from pathlib import Path
import sys

HAUPTORDNER = Path(__file__).resolve().parent.parent
if str(HAUPTORDNER) not in sys.path:
    sys.path.insert(0, str(HAUPTORDNER))

def weiter():
    eingabe=""
    while eingabe!="e":
        eingabe = input("Befehle: ?, e, p : ")
        if eingabe == "e":
            pass    
        elif eingabe == "?":
            pass    
        elif eingabe == "?":
            print("Hilfetext")
        elif eingabe == "p":        
            dobot.position_anzeigen(api)
        elif eingabe == "x":        
            pass    
        elif eingabe == "y":        
            pass    
        elif eingabe == "z":
            pass
        else:
            print("unbekannter Befehl")    
        

import dobot

print(dobot.version())

api = dobot.init("COM10")
dobot.alarme_loeschen(api)
dobot.queue_starten(api)

try:
    dobot.home(api)
    dobot.position_anzeigen(api)
    weiter()
    # Optional: Lochrasterplatte kalibrieren
    # dobot.plattenkalibrierung_setzen(...)
finally:
    dobot.queue_stoppen(api)

