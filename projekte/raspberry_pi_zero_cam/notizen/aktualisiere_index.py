from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INDEX_FILE = ROOT / "index.md"
START_MARKER = "<!-- BEGIN AUTO-GENERATED FILE LIST -->"
END_MARKER = "<!-- END AUTO-GENERATED FILE LIST -->"
LINK_PATTERN = re.compile(r"^- \[(.+)]\((.+\.md)\)$")


def read_existing_metadata(text: str) -> tuple[dict[str, str], dict[str, str]]:
    link_titles: dict[str, str] = {}
    section_titles: dict[str, str] = {}
    current_section = "Dateien"

    for line in text.splitlines():
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue

        match = LINK_PATTERN.match(line)
        if match is None:
            continue

        title, target = match.groups()
        link_titles[target] = title
        parent = Path(target).parent.as_posix()
        section_titles.setdefault(parent, current_section)

    return link_titles, section_titles


def title_from_file(path: Path) -> str:
    try:
        with path.open(encoding="utf-8-sig") as markdown_file:
            for line in markdown_file:
                if line.startswith("# "):
                    return line[2:].strip()
    except UnicodeDecodeError:
        pass

    return path.stem.replace("_", " ").replace("-", " ").strip().capitalize()


def section_title(folder: str) -> str:
    if folder == ".":
        return "Dateien"
    return Path(folder).name.replace("_", " ").replace("-", " ").title()


def build_file_list(
    link_titles: dict[str, str], section_titles: dict[str, str]
) -> str:
    groups: dict[str, list[Path]] = defaultdict(list)

    for path in ROOT.rglob("*.md"):
        if path != INDEX_FILE:
            relative_path = path.relative_to(ROOT)
            groups[relative_path.parent.as_posix()].append(relative_path)

    lines = [START_MARKER]
    for folder in sorted(groups, key=lambda value: (value != ".", value.casefold())):
        heading = section_titles.get(folder, section_title(folder))
        lines.extend(("", f"## {heading}", ""))

        for relative_path in sorted(
            groups[folder], key=lambda value: value.as_posix().casefold()
        ):
            target = relative_path.as_posix()
            title = link_titles.get(target, title_from_file(ROOT / relative_path))
            lines.append(f"- [{title}]({target})")

    lines.extend(("", END_MARKER))
    return "\n".join(lines)


def update_index() -> None:
    existing_text = INDEX_FILE.read_text(encoding="utf-8-sig")
    link_titles, section_titles = read_existing_metadata(existing_text)
    file_list = build_file_list(link_titles, section_titles)

    if START_MARKER in existing_text and END_MARKER in existing_text:
        prefix, remainder = existing_text.split(START_MARKER, maxsplit=1)
        _, suffix = remainder.split(END_MARKER, maxsplit=1)
        updated_text = f"{prefix.rstrip()}\n\n{file_list}{suffix}"
    else:
        first_section = existing_text.find("\n## ")
        prefix = existing_text[:first_section] if first_section >= 0 else existing_text
        updated_text = f"{prefix.rstrip()}\n\n{file_list}\n"

    INDEX_FILE.write_text(updated_text, encoding="utf-8", newline="\n")
    file_count = sum(1 for path in ROOT.rglob("*.md") if path != INDEX_FILE)
    print(f"{INDEX_FILE.name} wurde mit {file_count} Dateien aktualisiert.")


if __name__ == "__main__":
    update_index()