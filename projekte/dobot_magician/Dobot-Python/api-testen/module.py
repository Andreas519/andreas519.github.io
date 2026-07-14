# module.py

# ============================================================
# SYSTEMINFORMATIONEN
# ============================================================
def systeminfo():
    print("=" * 60)
    print("DOBOT MAGICIAN - START UND HOME-FAHRT")
    print("=" * 60)

    print()

    print(
        "Python-Version:    ",
        platform.python_version()
    )

    print(
        "Python-Architektur:",
        platform.architecture()[0]
    )

    print(
        "SDK-Verzeichnis:   ",
        sdk_verzeichnis
    )

    print(
        "DLL-Datei:         ",
        dll_datei
    )

    print(
        "DLL vorhanden:     ",
        dll_datei.exists()
    )



# ============================================================
# HILFSFUNKTION: ALARM-IDs LESEN
# ============================================================
