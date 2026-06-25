/* fetch("main.py")
  .then(response => response.text())
  .then(code => {
    const codefenster = document.getElementById("codefenster");
    codefenster.textContent = code;

    // Syntaxhighlighting nach dem Laden anwenden
    Prism.highlightElement(codefenster);
  })
  .catch(error => {
    document.getElementById("codefenster").textContent =
      "Fehler beim Laden der Datei: " + error;
  });
 */
  fetch("main.py")
  .then(response => {
    if (!response.ok) {
      throw new Error("HTTP-Fehler " + response.status + " beim Laden von " + response.url);
    }
    return response.text();
  })
  .then(code => {
    const codefenster = document.getElementById("codefenster");
    codefenster.textContent = code;

    Prism.highlightElement(codefenster);
  })
  .catch(error => {
    document.getElementById("codefenster").textContent =
      "Fehler beim Laden der Datei: " + error;
  });