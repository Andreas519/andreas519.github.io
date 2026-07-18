# dobot-test-2.py
from pathlib import Path
import sys

# Übergeordneten Ordner "Dobot-Python" in den Python-Suchpfad aufnehmen
PROJEKTORDNER = Path(__file__).resolve().parent.parent

if str(PROJEKTORDNER) not in sys.path:
    sys.path.insert(0, str(PROJEKTORDNER))

from sdk64 import DobotDllType as dType
import dobot

api = dobot.init()
dobot.alarme_anzeigen(api)
dobot.alarme_loeschen(api)
dobot.position_anzeigen(api)


dobot.alarme_loeschen(api)# ;dobot.fahre_sofort_zu(api,10,10,10)


ccc
dobot.queue_starten(api)


while True:
    eing = input(" ? :").lower()
    x,y,z,r = dobot.position_lesen(api)
    x = round(x); y = round(y); z = round(z); r = round(r)
    if eing == "e":
        break
    elif eing == "X":
        dobot.alarme_loeschen(api)
    elif eing == "a":
        dobot.alarme_anzeigen(api)
    elif eing == "f":
        werte = input("x y z")
        x,y,z = werte.split(" ")
        dobot.fahre_zu(api,int(x),int(y),int(z),0)
    elif eing == "f":
        werte = input("x y z")
        x,y,z = werte.split("x y z = ")
        x = int(x); y = int(y) ; z = int(z)
        dobot.fahre_zu(api,x,y,z,0)
    elif eing == "x":
        wert = input("x = ")
        x = int(wert)
        dobot.fahre_zu(api,x,y,z,0)
    elif eing == "y":
        wert = input("y = ")
        y = int(wert)
        dobot.fahre_zu(api,x,y,z,0)
    elif eing == "z":
        wert = input("z = ")
        z = int(wert)
        dobot.fahre_zu(api,x,y,z,0)

    elif eing == "A":
        dobot.alarme_anzeigen(api)
        dobot.alarme_loeschen(api)
    elif eing == "A":
        dobot.alarme_anzeigen(api)
        dobot.alarme_loeschen(api)
    elif eing == "Z":
        dobot.alarme_anzeigen(api)
        dobot.test_z(api)

    else:
        pass
    
        
