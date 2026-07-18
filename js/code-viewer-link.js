// Funktion zum Generieren von Code-Viewer-Links
function erstelleCodeViewerLink(dateiname, sprache, titel) {
  const url = new URL(window.location.href);
  const verzeichnis = url.pathname.substring(
    0,
    url.pathname.lastIndexOf("/") + 1
  );
  const vollstaendigerPfad = verzeichnis.replace(/^\/+/, "/") + dateiname;
  const lang = sprache || "python";
  const title = titel || dateiname;
  
  const link = document.createElement("a");
  link.href = "/tools/code-viewer.html?file=" + encodeURIComponent(vollstaendigerPfad) + "&lang=" + lang + "&title=" + encodeURIComponent(title);
  link.textContent = dateiname;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  
  return link;
}
