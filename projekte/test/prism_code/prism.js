document.addEventListener("DOMContentLoaded", () => {
  const codebloecke = document.querySelectorAll("code[data-src]");

  codebloecke.forEach(codeblock => {
    const datei = codeblock.dataset.src;

    fetch(datei)
      .then(response => {
        if (!response.ok) {
          throw new Error("HTTP-Fehler " + response.status + " beim Laden von " + datei);
        }
        return response.text();
      })
      .then(code => {
        codeblock.textContent = code;

        if (window.Prism) {
          Prism.highlightElement(codeblock);
        }
      })
      .catch(error => {
        codeblock.textContent = "Fehler beim Laden der Datei: " + error;
      });
  });
});

/* fetch("main.py")
  .then(response => {
    if (!response.ok) {
      throw new Error("HTTP-Fehler " + response.status + " beim Laden von " + response.url);
    }
    return response.text();
  })
  .then(code => {
    const codefenster = document.getElementById("codefenster");
    codefenster.textContent = code;

    // Syntaxhighlighting nach dem Laden anwenden
    Prism.highlightElement(codefenster);
  })
  .catch(error => {
    document.getElementById("codefenster").textContent =
      "Fehler beim Laden der Datei: " + error;
  }); */
