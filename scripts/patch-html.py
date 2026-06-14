#!/usr/bin/env python3
"""Convert src HTML pages to use build markers for nav, footer, mol-layer."""

import re
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"

NAV_RE = re.compile(
    r'<nav class="nav nav-cinematic[^"]*"[^>]*>.*?</nav>',
    re.DOTALL,
)

FOOTER_RE = re.compile(
    r'<footer class="site-footer">.*?</footer>',
    re.DOTALL,
)

MOL_RE = re.compile(
    r'<div class="page-mol-layer"[^>]*>.*?</div>\s*(?=<div class="container">)',
    re.DOTALL,
)

INNER_PAGES = [
    "about.html", "research.html", "publications.html", "projects.html",
    "cv.html", "cram.html", "gsat.html", "talks.html", "404.html",
]


def add_head_icons(content: str) -> str:
    if "<!-- SITE_HEAD_ICONS -->" in content or 'rel="icon"' in content:
        return content
    return content.replace(
        '<link rel="stylesheet" href="styles.css" />',
        '<!-- SITE_HEAD_ICONS -->\n  <link rel="stylesheet" href="styles.css" />',
        1,
    )


def add_main_wrapper(content: str) -> str:
    if "<!-- SITE_MAIN_START -->" in content:
        return content
    # After page-hero closing (inner pages)
    content = re.sub(
        r'(</div>\s*</div>\s*)(\n\s*<section)',
        r'\1\n\n  <!-- SITE_MAIN_START -->\2',
        content,
        count=1,
    )
    content = re.sub(
        r'(\n\s*)(<!-- SITE_FOOTER -->|<footer class="site-footer">)',
        r'\n  <!-- SITE_MAIN_END -->\1\2',
        content,
        count=1,
    )
    return content


def process_inner_page(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    content = add_head_icons(content)

    # Remove duplicate skip link if nav will include it
    content = re.sub(r'\s*<a class="skip-link"[^>]*>.*?</a>\s*', '\n', content, count=1)

    content, n = NAV_RE.subn("<!-- SITE_NAV -->", content, count=1)
    content, n2 = FOOTER_RE.subn("<!-- SITE_FOOTER -->", content, count=1)
    content, n3 = MOL_RE.subn("<!-- SITE_MOL_LAYER -->\n", content, count=1)

    content = add_main_wrapper(content)
    path.write_text(content, encoding="utf-8")
    print(f"  {path.name}: nav={n} footer={n2} mol={n3}")


def process_index(path: Path) -> None:
    content = path.read_text(encoding="utf-8")
    content = add_head_icons(content)

    # Update nav links to include Talks - replace nav section with marker inside cinematic wrap
    nav_match = NAV_RE.search(content)
    if nav_match:
        content = content[: nav_match.start()] + "<!-- SITE_NAV -->" + content[nav_match.end() :]

    content, n2 = FOOTER_RE.subn("<!-- SITE_FOOTER -->", content, count=1)

    # Add aria-current to home link in source won't matter - build handles it
    path.write_text(content, encoding="utf-8")
    print(f"  index.html: footer={n2}")


def main():
    print("Updating HTML source files...")
    process_index(SRC / "index.html")
    for name in INNER_PAGES:
        process_inner_page(SRC / name)
    print("Done.")


if __name__ == "__main__":
    main()
