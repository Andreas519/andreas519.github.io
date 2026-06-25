
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

    async function ladeMarkdown(datei) {
      const bereich = document.getElementById("markdown-inhalt");
      bereich.textContent = "Markdown wird geladen ...";

      try {
        const antwort = await fetch(datei);

        if (!antwort.ok) {
          throw new Error("Datei nicht gefunden: " + datei);
        }

        const markdownText = await antwort.text();

        // Markdown -> HTML
        const html = marked.parse(markdownText);

        // HTML bereinigen und einfügen
        bereich.innerHTML = DOMPurify.sanitize(html);

      } catch (fehler) {
        bereich.innerHTML = "<p><strong>Fehler:</strong> Markdown-Datei konnte nicht geladen werden.</p>";
        console.error(fehler);
      }
    }
   