#!/usr/bin/env python3
"""Build src/ → docs/ with snippet injection + EN/TH/JA locale pages."""

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "docs"
SNIPPETS = SRC / "snippets"
LOCALES = SRC / "locales"

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
    ("win95", "win95.html", "BoatOS"),
]
NAV_I18N_KEYS = {
    "home": "home",
    "about": "about",
    "research": "research",
    "publications": "publications",
    "talks": "talks",
    "projects": "projects",
    "cv": "cv",
    "cram": "cram",
    "gsat": "gsat",
    "win95": "boatos",
}

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

LOCALE_PAGES = ["index.html", "about.html", "research.html", "publications.html", "cv.html", "projects.html", "talks.html", "cram.html", "gsat.html"]


def read_snippet(name: str) -> str:
    return (SNIPPETS / name).read_text(encoding="utf-8")


def load_locale(lang: str) -> dict:
    path = LOCALES / f"{lang}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def lang_urls(filename: str, lang: str) -> dict:
    """Relative language switcher URLs for a page in a given locale folder."""
    if lang == "en":
        return {
            "lang_en": filename,
            "lang_th": f"th/{filename}",
            "lang_ja": f"ja/{filename}",
        }
    return {
        "lang_en": f"../{filename}",
        "lang_th": f"../th/{filename}" if lang != "th" else filename,
        "lang_ja": f"../ja/{filename}" if lang != "ja" else filename,
    }


def prefix_href(href: str, prefix: str) -> str:
    if not prefix:
        return href
    if href.startswith(("http://", "https://", "mailto:", "#", "data:")):
        return href
    return prefix + href


def nav_link(item_id, href, label, active_id, extra_class="", i18n_key=None):
    is_active = item_id == active_id
    cls = " ".join(x for x in [extra_class, "active" if is_active else ""] if x)
    attrs = f' class="{cls}"' if cls else ""
    if is_active:
        attrs += ' aria-current="page"'
    if i18n_key:
        attrs += f' data-i18n-nav="{i18n_key}"'
    return f'<li><a href="{href}"{attrs}>{label}</a></li>'


def build_nav(filename: str, lang: str = "en", asset_prefix: str = "") -> str:
    meta = PAGE_META.get(filename, {})
    active = meta.get("active")
    loc = load_locale(lang)
    nav_labels = loc.get("nav", {})

    def label_for(item_id, fallback):
        key = NAV_I18N_KEYS.get(item_id, item_id)
        return nav_labels.get(key, fallback)

    if meta.get("minimalNav"):
        home = prefix_href("index.html", asset_prefix)
        return (
            '  <nav class="nav nav-cinematic nav-cinematic-bar" id="nav" aria-label="Main navigation">\n'
            '    <div class="nav-cinematic-inner">\n'
            f'      <a href="{home}" class="nav-cinematic-logo">\n'
            '        <span class="nav-logo-mark">SK</span>\n'
            '        <span class="nav-logo-sub">BoatOS 95</span>\n'
            '      </a>\n'
            '      <div class="nav-cinematic-actions">\n'
            f'        <a href="{home}" class="nav-cinematic-cta" data-i18n-nav="home">{label_for("home", "Home")}</a>\n'
            '        <nav class="lang-switch lang-switch-nav" aria-label="Language">'
            f'<a href="{lang_urls(filename, lang)["lang_en"]}" data-lang="en">EN</a>'
            f'<a href="{lang_urls(filename, lang)["lang_th"]}" data-lang="th">ไทย</a>'
            f'<a href="{lang_urls(filename, lang)["lang_ja"]}" data-lang="ja">日本語</a></nav>\n'
            '      </div>\n'
            '    </div>\n'
            '  </nav>'
        )

    is_home = meta.get("navVariant") == "home"
    nav_class = "nav nav-cinematic" if is_home else "nav nav-cinematic nav-cinematic-bar"
    logo_current = ' aria-current="page"' if active == "home" else ""
    links = "\n          ".join(
        nav_link(i, prefix_href(h, asset_prefix), label_for(i, l), active, i18n_key=NAV_I18N_KEYS.get(i))
        for i, h, l in NAV_ITEMS
    )
    highlights = "\n          ".join(
        nav_link(
            i,
            prefix_href(h, asset_prefix),
            label_for(i, l),
            meta.get("highlight"),
            "nav-cinematic-highlight",
            i18n_key=NAV_I18N_KEYS.get(i),
        )
        for i, h, l in HIGHLIGHT_ITEMS
    )
    burger = (
        '        <button class="nav-burger nav-cinematic-burger" type="button" aria-label="Toggle menu" '
        'aria-expanded="false" aria-controls="nav-links" onclick="toggleMenu()">\n'
        '          <span></span><span></span><span></span>\n'
        '        </button>'
    )
    urls = lang_urls(filename, lang)
    lang_switch = (
        '        <nav class="lang-switch lang-switch-nav" aria-label="Language">'
        f'<a href="{urls["lang_en"]}" data-lang="en" hreflang="en">EN</a>'
        f'<a href="{urls["lang_th"]}" data-lang="th" hreflang="th">ไทย</a>'
        f'<a href="{urls["lang_ja"]}" data-lang="ja" hreflang="ja">日本語</a></nav>\n'
    )
    collab = label_for("collaborate", "Collaborate") if False else nav_labels.get("collaborate", "Collaborate")
    actions = (
        f'        <a href="mailto:{COLLAB_EMAIL}" class="nav-cinematic-cta" data-i18n-nav="collaborate">{collab}</a>\n'
        f'{lang_switch}'
        f'{burger}'
    )
    home_href = prefix_href("index.html", asset_prefix)
    inner = (
        f'      <a href="{home_href}" class="nav-cinematic-logo"{logo_current}>\n'
        f'        <span class="nav-logo-mark">SK</span>\n'
        f'        <span class="nav-logo-sub">BoatOS 95</span>\n'
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


def build_og_tags(filename: str, content: str, lang: str = "en") -> str:
    meta = PAGE_META.get(filename, {})
    if not meta.get("ogTitle") or 'property="og:title"' in content:
        return content
    desc_m = re.search(r'<meta name="description" content="([^"]*)"', content)
    desc = desc_m.group(1) if desc_m else ""
    if lang == "en":
        url = SITE_BASE + "/" if filename == "index.html" else SITE_BASE + "/" + filename
    else:
        url = f"{SITE_BASE}/{lang}/{filename}"
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


def get_by_path(obj, path: str):
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def apply_i18n_build(html: str, loc: dict) -> str:
    """Replace text of elements that have data-i18n at build time (best-effort)."""

    def replacer(match):
        full = match.group(0)
        key = match.group(1)
        val = get_by_path(loc, key)
        if val is None:
            return full
        # replace innermost text only for simple tags
        return re.sub(r">(.*?)</", f">{val}</", full, count=1, flags=re.S)

    return re.sub(
        r'<([a-zA-Z0-9]+)([^>]*\sdata-i18n="([^"]+)"[^>]*)>(.*?)</\1>',
        lambda m: (
            f"<{m.group(1)}{m.group(2)}>{get_by_path(loc, m.group(3))}</{m.group(1)}>"
            if get_by_path(loc, m.group(3)) is not None
            else m.group(0)
        ),
        html,
        flags=re.S,
    )


def rewrite_root_assets(html: str, prefix: str = "../") -> str:
    """Point relative assets to parent for locale subfolders."""
    out = re.sub(
        r'(href|src)="(?!https?:|mailto:|#|data:|\.\./)([^"]+)"',
        rf'\1="{prefix}\2"',
        html,
    )
    out = out.replace(f"{prefix}th/", "../th/")
    out = out.replace(f"{prefix}ja/", "../ja/")
    return out


def fix_locale_lang_switch(html: str, filename: str, lang: str) -> str:
    """Restore correct language switcher targets after asset rewriting."""
    urls = lang_urls(filename, lang)
    # Replace any mangled data-lang anchors
    html = re.sub(
        r'<a href="[^"]*" data-lang="en"',
        f'<a href="{urls["lang_en"]}" data-lang="en"',
        html,
    )
    html = re.sub(
        r'<a href="[^"]*" data-lang="th"',
        f'<a href="{urls["lang_th"]}" data-lang="th"',
        html,
    )
    html = re.sub(
        r'<a href="[^"]*" data-lang="ja"',
        f'<a href="{urls["lang_ja"]}" data-lang="ja"',
        html,
    )
    return html


def process_html(content: str, filename: str, lang: str = "en", asset_prefix: str = "") -> str:
    year = __import__("datetime").datetime.now().year
    out = content.replace("{{year}}", str(year))
    urls = lang_urls(filename, lang)
    for k, v in urls.items():
        out = out.replace("{{" + k + "}}", v)

    if "<!-- SITE_HEAD_ICONS -->" in out:
        icons = read_snippet("head-icons.html")
        if asset_prefix:
            icons = rewrite_root_assets(icons, asset_prefix)
        out = out.replace("<!-- SITE_HEAD_ICONS -->", icons)
    elif 'rel="icon"' not in out:
        icons = read_snippet("head-icons.html")
        if asset_prefix:
            icons = rewrite_root_assets(icons, asset_prefix)
        out = out.replace("</head>", icons + "\n</head>")

    out = build_og_tags(filename, out, lang)

    if "<!-- SITE_NAV -->" in out:
        out = out.replace("<!-- SITE_NAV -->", build_nav(filename, lang, asset_prefix))

    if "<!-- SITE_FOOTER -->" in out:
        footer = read_snippet("footer.html").replace("{{year}}", str(year))
        for k, v in urls.items():
            footer = footer.replace("{{" + k + "}}", v)
        if asset_prefix:
            # footer internal links need prefix except lang switch already set
            footer = re.sub(
                r'href="(?!https?:|mailto:|#|\.\./|th/|ja/)([^"]+\.html)"',
                rf'href="{asset_prefix}\1"',
                footer,
            )
        out = out.replace("<!-- SITE_FOOTER -->", footer)

    if "<!-- SITE_MOL_LAYER -->" in out:
        out = out.replace("<!-- SITE_MOL_LAYER -->", read_snippet("page-mol-layer.html"))

    if "<!-- SITE_MAIN_START -->" in out:
        after = out.split("<!-- SITE_MAIN_START -->", 1)[1]
        needs_main = not re.match(r"^\s*<main[\s>]", after)
        out = out.replace("<!-- SITE_MAIN_START -->", "<main id=\"main-content\">" if needs_main else "")
        out = out.replace("<!-- SITE_MAIN_END -->", "</main>" if needs_main else "")

    out = out.replace("mailto:suppaporn.2544@gmail.com", f"mailto:{COLLAB_EMAIL}")

    if lang != "en":
        out = re.sub(r'<html\s+lang="[^"]*"', f'<html lang="{lang}"', out, count=1)
        loc = load_locale(lang)
        out = apply_i18n_build(out, loc)
        out = rewrite_root_assets(out, asset_prefix or "../")
        out = fix_locale_lang_switch(out, filename, lang)

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
        elif src.suffix.lower() in {".css", ".js", ".txt", ".json"}:
            text = src.read_text(encoding="utf-8").replace("{{year}}", str(__import__("datetime").datetime.now().year))
            dest.write_text(text, encoding="utf-8")
        else:
            shutil.copy2(src, dest)


def build_locale_site(lang: str):
    dest_root = OUT / lang
    dest_root.mkdir(parents=True, exist_ok=True)
    for name in LOCALE_PAGES:
        src_file = SRC / name
        if not src_file.exists():
            continue
        html = process_html(src_file.read_text(encoding="utf-8"), name, lang=lang, asset_prefix="../")
        (dest_root / name).write_text(html, encoding="utf-8")
    # tiny locale landing note
    readme = dest_root / "README.txt"
    readme.write_text(f"BoatOS locale: {lang}\nAssets load from parent ../\n", encoding="utf-8")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    copy_tree(SRC, OUT)
    build_locale_site("th")
    build_locale_site("ja")
    print("Build complete. Output in docs/ (en) + docs/th + docs/ja")


if __name__ == "__main__":
    main()
