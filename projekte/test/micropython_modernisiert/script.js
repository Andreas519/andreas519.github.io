// Lädt alle Codeblöcke mit <code data-src="..."> und hebt sie mit Prism hervor.
// Lokal nicht per file:// öffnen, sondern z. B. mit: python -m http.server 8000

document.addEventListener('DOMContentLoaded', () => {
  const codeBlocks = document.querySelectorAll('code[data-src]');

  codeBlocks.forEach(async (code) => {
    const src = code.dataset.src;
    code.textContent = `Lade ${src} ...`;
    code.classList.add('code-status');

    try {
      const response = await fetch(src);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const text = await response.text();
      code.classList.remove('code-status');
      code.textContent = text;

      if (window.Prism) {
        Prism.highlightElement(code);
      }

      const pre = code.closest('pre');
      if (pre && !pre.nextElementSibling?.classList?.contains('code-download')) {
        const link = document.createElement('a');
        link.className = 'code-download';
        link.href = src;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = 'Quelltext öffnen';
        pre.insertAdjacentElement('afterend', link);
      }
    } catch (err) {
      code.textContent = `Fehler beim Laden von ${src}: ${err.message}`;
      code.classList.add('code-status');
    }
  });
});
