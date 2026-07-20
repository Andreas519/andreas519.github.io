def scheibe_umsetzen(staebe, von, nach):
    scheibe = staebe[von].pop()
    staebe[nach].append(scheibe)
    print(f"Scheibe {scheibe}: {von} -> {nach}")
    print("Zustand:", staebe)


def hanoi_real(anzahl, start, hilf, ziel, staebe):
    if anzahl == 1:
        scheibe_umsetzen(staebe, start, ziel)
    else:
        hanoi_real(anzahl - 1, start, ziel, hilf, staebe)
        scheibe_umsetzen(staebe, start, ziel)
        hanoi_real(anzahl - 1, hilf, start, ziel, staebe)


staebe = {
    "A": [3, 2, 1],
    "B": [],
    "C": [],
}

hanoi_real(3, "A", "B", "C", staebe)