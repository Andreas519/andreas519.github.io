# main.py

import network
import socket
import time
import gc

import webseite
import programme


# ------------------------------------------------------------
# WLAN Access Point starten
# ------------------------------------------------------------

def starte_access_point():
    ssid = "ESP32-Datenlogger"
    password = "12345678"   # mindestens 8 Zeichen

    ap = network.WLAN(network.AP_IF)
    ap.active(True)

    # Offenes WLAN
    ap.config(essid=ssid, authmode=network.AUTH_OPEN)

    # Verschlüsseltes WLAN, falls später gewünscht:
    # ap.config(essid=ssid, password=password, authmode=network.AUTH_WPA_WPA2_PSK)

    while not ap.active():
        time.sleep(0.1)

    print("Access Point aktiv")
    print(ap.ifconfig())

    return ap


# ------------------------------------------------------------
# HTTP-Antworten senden
# ------------------------------------------------------------

def sende_html(conn, html):
    conn.send("HTTP/1.1 200 OK\r\n")
    conn.send("Content-Type: text/html; charset=utf-8\r\n")
    conn.send("Connection: close\r\n")
    conn.send("\r\n")
    conn.sendall(html.encode())


def sende_json(conn, json_text):
    conn.send("HTTP/1.1 200 OK\r\n")
    conn.send("Content-Type: application/json\r\n")
    conn.send("Connection: close\r\n")
    conn.send("\r\n")
    conn.sendall(json_text.encode())


# ------------------------------------------------------------
# Webserver
# ------------------------------------------------------------

def webserver():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print("Webserver läuft auf:")
    print("http://192.168.4.1")

    while True:
        conn, addr = s.accept()
        print("\nVerbindung von", addr)

        try:
            request = conn.recv(1024).decode()
            erste_zeile = request.split("\r\n")[0]
            print("Erste Zeile:", erste_zeile)

            meldung = ""

            # ------------------------------------------------
            # ADC-Messung per JavaScript/fetch
            # Beispiel:
            # GET /adc HTTP/1.1
            # ------------------------------------------------
            if erste_zeile.startswith("GET /adc "):
                print("ADC-Messung wird ausgeführt")
                response = programme.adc_json()
                sende_json(conn, response)
                continue

            # ------------------------------------------------
            # Programmauswahl per Button
            # Beispiel:
            # GET /start?prog=blink HTTP/1.1
            # ------------------------------------------------
            if erste_zeile.startswith("GET /start?prog="):
                start = len("GET /start?prog=")
                ende = erste_zeile.find(" ", start)
                prog = erste_zeile[start:ende]

                print("Gewähltes Programm:", prog)
                meldung = programme.starte_programm(prog)

            # ------------------------------------------------
            # Webseite senden
            # ------------------------------------------------
            response = webseite.html_seite(meldung)
            sende_html(conn, response)

        except Exception as e:
            print("Fehler:", e)

        finally:
            conn.close()
            gc.collect()


# ------------------------------------------------------------
# Start
# ------------------------------------------------------------

starte_access_point()
webserver()