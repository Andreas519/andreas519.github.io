import pathlib, re
root = pathlib.Path('.')
html_files = [p for p in root.rglob('*.html') if p.is_file()]
for p in html_files:
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    for href in re.findall(r'href=["\']([^"\']+)["\']', text):
        if href.startswith(('http://','https://','mailto:','#','javascript:')):
            continue
        target = (p.parent / href.split('#',1)[0].split('?',1)[0]).resolve()
        if not target.exists():
            print(f'{p}\t{href}\tMISSING')
