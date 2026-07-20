# tuerme-von-hanoi-01.py
POSITIONEN = ["A", "B", "C"]


def hanoi(anzahl, start, hilf, ziel, zuege):
    if anzahl == 1:
        zuege.append((1, start, ziel))
    else:
        hanoi(anzahl - 1, start, ziel, hilf, zuege)
        zuege.append((anzahl, start, ziel))
        hanoi(anzahl - 1, hilf, start, ziel, zuege)


def turm_von_hanoi_3(start, hilf, ziel):
    zuege = []
    hanoi(3, start, hilf, ziel, zuege)
    return zuege

start = "A"
hilf = "B"
ziel = "C"

zuege = turm_von_hanoi_3(start, hilf, ziel)

for nr, (scheibe, von, nach) in enumerate(zuege, start=1):
    print(f"{nr}. Scheibe {scheibe}: {von} -> {nach}")