/**
 * Erstellt einen Link zu einem Markdown-Viewer
 * @param {string} dateiname - Der Name oder Pfad der Markdown-Datei
 * @param {string} titel - (Optional) Der Titel, der im Viewer angezeigt wird
 * @returns {HTMLAnchorElement} Link-Element mit korrektem Pfad und Ziel
 */
function erstelleMdViewerLink(dateiname, titel) {
  const url = new URL(window.location.href);
  const verzeichnis = url.pathname.substring(0, url.pathname.lastIndexOf("/") + 1);
  const vollstaendigerPfad = verzeichnis.replace(/^\/+/, "/") + dateiname;
  const title = titel || dateiname;
  
  const link = document.createElement("a");
  link.href = "/tools/md-viewer.html?file=" + encodeURIComponent(vollstaendigerPfad) + "&title=" + encodeURIComponent(title);
  link.textContent = dateiname;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  
  return link;
}
