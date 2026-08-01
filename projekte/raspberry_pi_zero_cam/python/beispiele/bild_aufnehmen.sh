#!/usr/bin/env bash
set -euo pipefail

BREITE="${1:-1296}"
HOEHE="${2:-972}"
DATEI="${3:-/home/pi/test.jpg}"

rpicam-still --nopreview --width "$BREITE" --height "$HOEHE" -o "$DATEI"
ls -lh "$DATEI"
