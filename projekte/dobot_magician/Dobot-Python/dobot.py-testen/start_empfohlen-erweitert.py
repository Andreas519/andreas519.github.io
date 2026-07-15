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
            break   
        elif eingabe == "z":
            dobot.test_z(api)    
        elif eingabe == "?":
            print("Hilfetext")
        elif eingabe == "0":        
            dobot.fahre_sofort_zu(api, 0, 100, 50)
        elif eingabe == "a":        
            dobot.alarme_loeschen(api)            
        elif eingabe == "p":        
            dobot.position_anzeigen(api)
        elif eingabe == "h":        
            dobot.home(api)
        elif eingabe=="x":    
            dobot.alarme_loeschen(api)
            dobot.queue_starten(api)
        elif eingabe == "s":        
            if dobot.sauger_status(api):
                print("Sauger wird deaktiviert.")
                dobot.sauger_deaktivieren(api, 0)
            else:
                print("Sauger wird aktiviert.")
                dobot.sauger_aktivieren(api, 0)
        else:
            print("unbekannter Befehl")    
        

import dobot

print(dobot.version())

api = dobot.init("COM10")
dobot.alarme_loeschen(api)
#dobot.queue_starten(api)

try:
    # dobot.home(api)
    dobot.position_anzeigen(api)
    # weiter()
    
    
    # Optional: Lochrasterplatte kalibrieren
    # dobot.plattenkalibrierung_setzen(...)
finally:
    dobot.queue_stoppen(api)

