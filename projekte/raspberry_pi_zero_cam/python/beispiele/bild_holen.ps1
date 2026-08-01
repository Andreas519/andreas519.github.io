$ErrorActionPreference = "Stop"

$PiHost = "raspi-zero-xx"
$PiUser = "pi"
$Breite = 1296
$Hoehe = 972
$RemoteDatei = "/home/pi/test.jpg"
$ZielOrdner = "D:\Kamera\Bilder"
$ZielDatei = Join-Path $ZielOrdner "test.jpg"

New-Item -ItemType Directory -Force -Path $ZielOrdner | Out-Null

Write-Host "1. Aufnahme auf dem Raspberry Pi ..."
ssh "${PiUser}@${PiHost}" "rpicam-still --nopreview --width $Breite --height $Hoehe -o $RemoteDatei"
if ($LASTEXITCODE -ne 0) {
    throw "Die Bildaufnahme auf dem Raspberry Pi ist fehlgeschlagen."
}

Write-Host "2. Bild wird auf den Windows-PC übertragen ..."
scp "${PiUser}@${PiHost}:${RemoteDatei}" "$ZielDatei"
if ($LASTEXITCODE -ne 0) {
    throw "Die Bildübertragung ist fehlgeschlagen."
}

Write-Host "Bild gespeichert: $ZielDatei"
Start-Process "$ZielDatei"
