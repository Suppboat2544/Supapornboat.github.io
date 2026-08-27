#!/usr/bin/env python3
"""Build src/ → docs/ with snippet injection (Python fallback for build.js)."""

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
SNIPPETS = SRC / "snippets"

SITE_BASE = "https://suppboat2544.github.io/Supapornboat.github.io"
OG_IMAGE = "https://avatars.githubusercontent.com/u/179722549?v=4"
COLLAB_EMAIL = "klabklaydee.s.aa@m.titech.ac.jp"

NAV_ITEMS = [
    ("home", "index.html", "Home"),
    ("about", "about.html", "About"),
    ("research", "research.html", "Research"),
    ("publications", "publications.html", "Publications"),
    ("talks", "talks.html", "Talks"),
    ("projects", "projects.html", "Projects"),
    ("cv", "cv.html", "CV"),
]
HIGHLIGHT_ITEMS = [
    ("cram", "cram.html", "CRAM"),
    ("gsat", "gsat.html", "GSAT"),
]

PAGE_META = {
    "index.html": {"active": "home", "ogTitle": "Supaporn Klabklaydee | Cheminformatics · Environmental Chemistry", "navVariant": "home"},
    "about.html": {"active": "about", "ogTitle": "About · Supaporn Klabklaydee"},
    "research.html": {"active": "research", "ogTitle": "Research · Supaporn Klabklaydee"},
    "publications.html": {"active": "publications", "ogTitle": "Publications · Supaporn Klabklaydee"},
    "talks.html": {"active": "talks", "ogTitle": "Talks & Presentations · Supaporn Klabklaydee"},
    "projects.html": {"active": "projects", "ogTitle": "Projects · Supaporn Klabklaydee"},
    "cv.html": {"active": "cv", "ogTitle": "CV · Supaporn Klabklaydee"},
    "cram.html": {"active": "cram", "ogTitle": "CRAM-GTransformer · Supaporn Klabklaydee", "highlight": "cram"},
    "gsat.html": {"active": "gsat", "ogTitle": "GSAT Model · Supaporn Klabklaydee", "highlight": "gsat"},
    "win95.html": {"active": None, "ogTitle": "BoatOS 95 · Supaporn Klabklaydee", "minimalNav": True},
    "404.html": {"active": None, "ogTitle": "Page not found · Supaporn Klabklaydee", "minimalNav": True},
}


def read_snippet(name: str) -> str:
    return (SNIPPETS / name).read_text(encoding="utf-8")


def nav_link(item_id, href, label, active_id, extra_class=""):
    is_active = item_id == active_id
    cls = " ".join(x for x in [extra_class, "active" if is_active else ""] if x)
    attrs = f' class="{cls}"' if cls else ""
    if is_active:
        attrs += ' aria-current="page"'
    return f'<li><a href="{href}"{attrs}>{label}</a></li>'


def build_nav(filename: str) -> str:
    meta = PAGE_META.get(filename, {})
    active = meta.get("active")
    if meta.get("minimalNav"):
        return (
            '  <nav class="nav nav-cinematic nav-cinematic-bar" id="nav" aria-label="Main navigation">\n'
            '    <div class="nav-cinematic-inner">\n'
            '      <a href="index.html" class="nav-cinematic-logo">\n'
            '        <span class="nav-logo-mark">SK</span>\n'
            '        <span class="nav-logo-sub">Cheminformatics</span>\n'
            '      </a>\n'
            '      <div class="nav-cinematic-actions">\n'
            '        <a href="index.html" class="nav-cinematic-cta">Home</a>\n'
            '      </div>\n'
            '    </div>\n'
            '  </nav>'
        )

    is_home = meta.get("navVariant") == "home"
    nav_class = "nav nav-cinematic" if is_home else "nav nav-cinematic nav-cinematic-bar"
    logo_current = ' aria-current="page"' if active == "home" else ""
    links = "\n          ".join(nav_link(i, h, l, active) for i, h, l in NAV_ITEMS)
    highlights = "\n          ".join(
        nav_link(i, h, l, meta.get("highlight"), "nav-cinematic-highlight") for i, h, l in HIGHLIGHT_ITEMS
    )
    burger = (
        '        <button class="nav-burger nav-cinematic-burger" type="button" aria-label="Toggle menu" '
        'aria-expanded="false" aria-controls="nav-links" onclick="toggleMenu()">\n'
        '          <span></span><span></span><span></span>\n'
        '        </button>'
    )
    actions = (
        f'        <a href="mailto:{COLLAB_EMAIL}" class="nav-cinematic-cta">Collaborate</a>\n'
        f'{burger}'
    )
    inner = (
        f'      <a href="index.html" class="nav-cinematic-logo"{logo_current}>\n'
        f'        <span class="nav-logo-mark">SK</span>\n'
        f'        <span class="nav-logo-sub">Cheminformatics</span>\n'
        f'      </a>\n'
        f'      <ul class="nav-links nav-cinematic-links" id="nav-links">\n'
        f'          {links}\n'
        f'          {highlights}\n'
        f'      </ul>\n'
        f'      <div class="nav-cinematic-actions">\n'
        f'{actions}\n'
        f'      </div>'
    )

    if is_home:
        return (
            f'      <nav class="{nav_class}" id="nav" aria-label="Main navigation">\n'
            f'        <div class="nav-cinematic-inner">\n'
            f'{inner}\n'
            f'        </div>\n'
            f'      </nav>'
        )

    return (
        f'  <a class="skip-link" href="#main-content">Skip to content</a>\n'
        f'  <nav class="{nav_class}" id="nav" aria-label="Main navigation">\n'
        f'    <div class="nav-cinematic-inner">\n'
        f'{inner}\n'
        f'    </div>\n'
        f'  </nav>'
    )


def build_og_tags(filename: str, content: str) -> str:
    meta = PAGE_META.get(filename, {})
    if not meta.get("ogTitle") or 'property="og:title"' in content:
        return content
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', content)
    desc = desc_m.group(1) if desc_m else ""
    url = SITE_BASE + "/" if filename == "index.html" else SITE_BASE + "/" + filename
    og = "\n".join([
        '  <meta property="og:type" content="website" />',
        f'  <meta property="og:url" content="{url}" />',
        f'  <meta property="og:title" content="{meta["ogTitle"]}" />',
        f'  <meta property="og:description" content="{desc}" />',
        f'  <meta property="og:image" content="{OG_IMAGE}" />',
        '  <meta name="twitter:card" content="summary" />',
        f'  <meta name="twitter:title" content="{meta["ogTitle"]}" />',
        f'  <meta name="twitter:description" content="{desc}" />',
        f'  <meta name="twitter:image" content="{OG_IMAGE}" />',
    ])
    return re.sub(r'(<link rel="canonical"[^>]*>)', r"\1\n" + og, content, count=1)


def process_html(content: str, filename: str) -> str:
    year = __import__("datetime").datetime.now().year
    out = content.replace("{{year}}", str(year))

    if "<!-- SITE_HEAD_ICONS -->" in out:
        out = out.replace("<!-- SITE_HEAD_ICONS -->", read_snippet("head-icons.html"))
    elif 'rel="icon"' not in out:
        out = out.replace("</head>", read_snippet("head-icons.html") + "\n</head>")

    out = build_og_tags(filename, out)

    if "<!-- SITE_NAV -->" in out:
        out = out.replace("<!-- SITE_NAV -->", build_nav(filename))

    if "<!-- SITE_FOOTER -->" in out:
        footer = read_snippet("footer.html").replace("{{year}}", str(year))
        out = out.replace("<!-- SITE_FOOTER -->", footer)

    if "<!-- SITE_MOL_LAYER -->" in out:
        out = out.replace("<!-- SITE_MOL_LAYER -->", read_snippet("page-mol-layer.html"))

    if "<!-- SITE_MAIN_START -->" in out:
        after = out.split("<!-- SITE_MAIN_START -->", 1)[1]
        needs_main = not re.match(r"^\s*<main[\s>]", after)
        out = out.replace("<!-- SITE_MAIN_START -->", "<main id=\"main-content\">" if needs_main else "")
        out = out.replace("<!-- SITE_MAIN_END -->", "</main>" if needs_main else "")

    out = out.replace("mailto:suppaporn.2544@gmail.com", f"mailto:{COLLAB_EMAIL}")
    return out


def copy_tree(src: Path, dest: Path):
    if src.is_dir():
        if src.name == "snippets":
            return
        dest.mkdir(parents=True, exist_ok=True)
        for child in src.iterdir():
            copy_tree(child, dest / child.name)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in {".html", ".htm"}:
            dest.write_text(process_html(src.read_text(encoding="utf-8"), src.name), encoding="utf-8")
        elif src.suffix.lower() in {".css", ".js", ".txt"}:
            text = src.read_text(encoding="utf-8").replace("{{year}}", str(__import__("datetime").datetime.now().year))
            dest.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(src, dest)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    copy_tree(SRC, OUT)
    print("Build complete. Output in docs/")


if __name__ == "__main__":
    main()
