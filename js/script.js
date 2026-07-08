
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

  document.querySelectorAll('pre > code[class*="language-"]').forEach((codeElement, index) => {
    const preElement = codeElement.parentElement;

    if (!preElement || preElement.dataset.codeEnhanced === "true") {
      return;
    }

    preElement.dataset.codeEnhanced = "true";
    preElement.classList.add("codeblock");

    const codeText = codeElement.textContent.replace(/\n$/, "");
    const lineCount = codeText === "" ? 1 : codeText.split("\n").length;
    const lineNumbers = document.createElement("span");
    lineNumbers.className = "line-numbers-rows";

    for (let lineIndex = 0; lineIndex < lineCount; lineIndex += 1) {
      lineNumbers.appendChild(document.createElement("span"));
    }

    preElement.appendChild(lineNumbers);

    const wrapper = document.createElement("div");
    wrapper.className = "codeblock-wrapper";

    const toolbar = document.createElement("div");
    toolbar.className = "codeblock-toolbar";

    const label = document.createElement("span");
    label.className = "codeblock-language";
    const languageClass = Array.from(codeElement.classList).find(cssClass => cssClass.startsWith("language-")) || "language-text";
    const languageName = languageClass.replace("language-", "");
    label.textContent = languageName.toUpperCase();

    toolbar.appendChild(label);

    preElement.parentNode.insertBefore(wrapper, preElement);
    wrapper.appendChild(toolbar);
    wrapper.appendChild(preElement);

    if (window.Prism) {
      Prism.highlightElement(codeElement);
    }
  });

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
   
    function openFileInPrismTab(fileUrl, language = 'python', title = 'Code anzeigen') {
  const resolvedUrl = new URL(fileUrl, window.location.href).href;
  const tab = window.open('about:blank', '_blank');
  if (!tab) {
    alert('Neuer Tab blockiert. Erlaube Popups für diese Seite.');
    return;
  }

  const html = `
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <title>${title}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs/themes/prism.css">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/prismjs/plugins/line-numbers/prism-line-numbers.css">
  <style>
    body { margin: 1rem; font-family: sans-serif; background: #f5f5f5; }
    .line-numbers { white-space: pre-wrap; word-break: break-word; }
  </style>
</head>
<body>
  <pre class="line-numbers"><code id="codeblock" class="language-${language}">Lade Datei …</code></pre>

  <script src="https://cdn.jsdelivr.net/npm/prismjs/prism.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs/plugins/line-numbers/prism-line-numbers.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/prismjs/components/prism-${language}.min.js"></script>
  <script>
    fetch(${JSON.stringify(resolvedUrl)})
      .then(response => {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        return response.text();
      })
      .then(code => {
        const codeEl = document.getElementById('codeblock');
        codeEl.textContent = code;
        if (window.Prism) {
          Prism.highlightElement(codeEl);
        }
      })
      .catch(error => {
        document.getElementById('codeblock').textContent =
          'Fehler beim Laden der Datei: ' + error;
      });
  </script>
</body>
</html>
`;

  tab.document.write(html);
  tab.document.close();
}
// Marker