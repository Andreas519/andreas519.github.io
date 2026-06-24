
function ladeDatei(datei, elementId) {
  fetch(datei)
    .then(response => {
      if (!response.ok) {
        throw new Error("HTTP-Fehler " + response.status);
      }
      return response.text();
    })
    .then(text => {
      document.getElementById(elementId).textContent = text;
    })
    .catch(error => {
      document.getElementById(elementId).textContent =
        "Datei konnte nicht geladen werden: " + datei;
    });
}

  const datum = new Date(document.lastModified);

  document.getElementById("lastModified").textContent =
    datum.toLocaleString("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    }) + " Uhr";



