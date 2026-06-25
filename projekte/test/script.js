fetch("main.py")
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