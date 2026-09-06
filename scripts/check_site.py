#!/usr/bin/env python3
"""Check basic HTML structure and local links without third-party packages."""

from html.parser import HTMLParser
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REQUIRED = {"title"}


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: set[str] = set()
        self.references: list[str] = []
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        self.tags.add(tag)
        if tag == "meta" and attributes.get("name") == "viewport":
            self.has_viewport = "width=device-width" in (attributes.get("content") or "")
        for name in ("href", "src"):
            if value := attributes.get(name):
                self.references.append(value)


def main() -> int:
    errors: list[str] = []
    pages = sorted(DOCS.rglob("*.html"))
    if not pages:
        errors.append("docs/ に HTML ファイルがありません")

    for page in pages:
        parser = PageParser()
        parser.feed(page.read_text(encoding="utf-8"))
        label = page.relative_to(ROOT)
        for tag in REQUIRED - parser.tags:
            errors.append(f"{label}: <{tag}> がありません")
        if not parser.has_viewport:
            errors.append(f"{label}: mobile viewport がありません")
        for reference in parser.references:
            if reference.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = (page.parent / reference.split("#", 1)[0]).resolve()
            if not target.exists():
                errors.append(f"{label}: リンク先がありません: {reference}")

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"OK: {len(pages)} HTML files checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
