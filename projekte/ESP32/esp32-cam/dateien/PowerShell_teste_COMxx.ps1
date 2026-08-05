$port = [System.IO.Ports.SerialPort]::new(
    "COM6",
    115200,
    [System.IO.Ports.Parity]::None,
    8,
    [System.IO.Ports.StopBits]::One
)

$port.Handshake = [System.IO.Ports.Handshake]::None
$port.ReadTimeout = 1000
$port.WriteTimeout = 1000
$port.NewLine = "`n"

try {
    $port.Open()
    Write-Host "COM6 wurde geöffnet."

    Start-Sleep -Seconds 2

    $port.WriteLine("STATUS")
    Write-Host "Gesendet: STATUS"

    Start-Sleep -Milliseconds 500

    $antwort = $port.ReadExisting()

    if ($antwort.Length -gt 0) {
        Write-Host "Empfangen:"
        Write-Host $antwort
    }
    else {
        Write-Host "Keine Antwort empfangen."
    }
}
catch {
    Write-Host "Fehler: $($_.Exception.Message)"
}
finally {
    if ($port.IsOpen) {
        $port.Close()
    }

    $port.Dispose()
    Write-Host "Serielle Verbindung geschlossen."
}
pause