# Prompt 36 – Wo speichert Bash die Terminaleingaben?

## Prompt

Wo werden die Eingaben im Raspberry-Pi-Terminal gespeichert?

## Antwort

Verlauf anzeigen:

```bash
history
history 20
```

Datei:

```text
~/.bash_history
```

entspricht:

```text
/home/pi/.bash_history
```

Suchen:

```bash
history | grep mount
grep scp ~/.bash_history
```

Rückwärtssuche:

```text
Strg + R
```
