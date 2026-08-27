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
SITE_ROOT = "/Supapornboat.github.io"  # absolute path prefix for GitHub project Pages
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
    """Absolute language switcher URLs (GitHub project Pages safe)."""
    # Prefer clean directory URLs for locale homes (…/th/ not …/th/index.html)
    if filename == "index.html":
        en = f"{SITE_ROOT}/"
        th = f"{SITE_ROOT}/th/"
        ja = f"{SITE_ROOT}/ja/"
    else:
        en = f"{SITE_ROOT}/{filename}"
        th = f"{SITE_ROOT}/th/{filename}"
        ja = f"{SITE_ROOT}/ja/{filename}"
    return {
        "lang_en": en,
        "lang_th": th,
        "lang_ja": ja,
    }


def page_href(filename: str, lang: str = "en") -> str:
    if lang == "en":
        return f"{SITE_ROOT}/" if filename == "index.html" else f"{SITE_ROOT}/{filename}"
    if filename == "index.html":
        return f"{SITE_ROOT}/{lang}/"
    return f"{SITE_ROOT}/{lang}/{filename}"


def prefix_href(href: str, prefix: str = "", lang: str = "en") -> str:
    if not href or href.startswith(("http://", "https://", "mailto:", "#", "data:", SITE_ROOT)):
        return href
    if href.startswith("../"):
        return href
    if href.endswith(".html"):
        return page_href(href, lang)
    return (prefix or "") + href


def inject_base_tag(html: str, lang: str = "en") -> str:
    """Ensure relative links resolve under the GitHub project Pages root."""
    base = f"{SITE_ROOT}/" if lang == "en" else f"{SITE_ROOT}/{lang}/"
    if re.search(r"<base\s", html, flags=re.I):
        return re.sub(r'<base\s+[^>]*>', f'<base href="{base}" />', html, count=1, flags=re.I)
    return re.sub(r"(<head[^>]*>)", rf'\1\n  <base href="{base}" />', html, count=1, flags=re.I)


def nav_link(item_id, href, label, active_id, extra_class="", i18n_key=None):
    is_active = item_id == active_id
    cls = " ".join(x for x in [extra_class, "active" if is_active else ""] if x)
    attrs = f' class="{cls}"' if cls else ""
    if is_active:
        attrs += ' aria-current="page"'
    if i18n_key:
        attrs += f' data-i18n-nav="{i18n_key}"'
    return f'<li><a href="{href}"{attrs}>{label}</a></li>'


def build_lang_switch(filename: str, lang: str = "en", extra_class: str = "") -> str:
    """EN / JP / THA switcher for header (and footer)."""
    # Error page should switch to each locale's home, not 404.html
    switch_file = "index.html" if filename in ("404.html",) else filename
    urls = lang_urls(switch_file, lang)
    cls = "lang-switch" + (f" {extra_class}" if extra_class else "")
    active = {
        "en": ' class="is-active" aria-current="page"' if lang == "en" else "",
        "ja": ' class="is-active" aria-current="page"' if lang == "ja" else "",
        "th": ' class="is-active" aria-current="page"' if lang == "th" else "",
    }
    return (
        f'<nav class="{cls}" aria-label="Language">'
        f'<a href="{urls["lang_en"]}" data-lang="en" hreflang="en"{active["en"]}>EN</a>'
        f'<a href="{urls["lang_ja"]}" data-lang="ja" hreflang="ja"{active["ja"]}>JP</a>'
        f'<a href="{urls["lang_th"]}" data-lang="th" hreflang="th"{active["th"]}>THA</a>'
        "</nav>"
    )


def build_nav(filename: str, lang: str = "en", asset_prefix: str = "") -> str:
    meta = PAGE_META.get(filename, {})
    active = meta.get("active")
    loc = load_locale(lang)
    nav_labels = loc.get("nav", {})

    def label_for(item_id, fallback):
        key = NAV_I18N_KEYS.get(item_id, item_id)
        return nav_labels.get(key, fallback)

    if meta.get("minimalNav"):
        home = page_href("index.html", lang if lang in ("th", "ja") else "en")
        lang_sw = "        " + build_lang_switch(filename, lang, "lang-switch-nav") + "\n"
        return (
            '  <nav class="nav nav-cinematic nav-cinematic-bar" id="nav" aria-label="Main navigation">\n'
            '    <div class="nav-cinematic-inner">\n'
            f'      <a href="{home}" class="nav-cinematic-logo">\n'
            '        <span class="nav-logo-mark">SK</span>\n'
            '        <span class="nav-logo-sub">BoatOS 95</span>\n'
            '      </a>\n'
            '      <div class="nav-cinematic-actions">\n'
            f'{lang_sw}'
            f'        <a href="{home}" class="nav-cinematic-cta" data-i18n-nav="home">{label_for("home", "Home")}</a>\n'
            '      </div>\n'
            '    </div>\n'
            '  </nav>'
        )

    is_home = meta.get("navVariant") == "home"
    nav_class = "nav nav-cinematic" if is_home else "nav nav-cinematic nav-cinematic-bar"
    logo_current = ' aria-current="page"' if active == "home" else ""
    links = "\n          ".join(
        nav_link(i, page_href(h, "en" if not asset_prefix else lang), label_for(i, l), active, i18n_key=NAV_I18N_KEYS.get(i))
        for i, h, l in NAV_ITEMS
    )
    highlights = "\n          ".join(
        nav_link(
            i,
            # BoatOS desktop stays EN-only (no locale copy)
            page_href(h, "en" if i == "win95" else ("en" if not asset_prefix else lang)),
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
    lang_sw = "        " + build_lang_switch(filename, lang, "lang-switch-nav") + "\n"
    collab = nav_labels.get("collaborate", "Collaborate")
    actions = (
        f'{lang_sw}'
        f'        <a href="mailto:{COLLAB_EMAIL}" class="nav-cinematic-cta nav-cinematic-cta-desk" data-i18n-nav="collaborate">{collab}</a>\n'
        f'{burger}'
    )
    home_href = page_href("index.html", "en")
    # Locale pages should still land on translated home when available
    if asset_prefix and lang in ("th", "ja"):
        home_href = page_href("index.html", lang)
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


def rewrite_root_assets(html: str, prefix: str = "../") -> str:
    """Point relative assets to parent for locale subfolders."""
    # Do not rewrite absolute site paths (starting with /) or protocols
    out = re.sub(
        r'(href|src)="(?!https?:|mailto:|#|data:|\.\./|/)([^"]+)"',
        rf'\1="{prefix}\2"',
        html,
    )
    out = out.replace(f"{prefix}th/", "../th/")
    out = out.replace(f"{prefix}ja/", "../ja/")
    return out


def apply_i18n_build(html: str, loc: dict) -> str:
    """Replace text/HTML of elements that have data-i18n / data-i18n-html at build time."""

    def repl_html(match):
        key = match.group(3)
        val = get_by_path(loc, key)
        if val is None:
            return match.group(0)
        return f"<{match.group(1)}{match.group(2)}>{val}</{match.group(1)}>"

    def repl_text(match):
        key = match.group(3)
        val = get_by_path(loc, key)
        if val is None:
            return match.group(0)
        # plain text — escape nothing special beyond keeping string
        return f"<{match.group(1)}{match.group(2)}>{val}</{match.group(1)}>"

    # HTML first so nested tags in values are preserved
    html = re.sub(
        r'<([a-zA-Z0-9]+)([^>]*\sdata-i18n-html="([^"]+)"[^>]*)>(.*?)</\1>',
        repl_html,
        html,
        flags=re.S,
    )
    html = re.sub(
        r'<([a-zA-Z0-9]+)([^>]*\sdata-i18n="([^"]+)"[^>]*)>(.*?)</\1>',
        repl_text,
        html,
        flags=re.S,
    )
    return html


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
        # Rewrite footer HTML links to absolute site paths (same language)
        footer = re.sub(
            r'href="(?!https?:|mailto:|#|/|\{)([^"]+\.html)"',
            lambda m: f'href="{page_href(m.group(1), lang)}"',
            footer,
        )
        song = read_snippet("song-dock.html")
        if asset_prefix:
            song = rewrite_root_assets(song, asset_prefix)
            footer = rewrite_root_assets(footer, asset_prefix)
            footer = fix_locale_lang_switch(footer, filename, lang)
        footer = footer.replace("<!-- SITE_SONG_DOCK -->", song)
        out = out.replace("<!-- SITE_FOOTER -->", footer)

    if "<!-- SITE_MOL_LAYER -->" in out:
        out = out.replace("<!-- SITE_MOL_LAYER -->", read_snippet("page-mol-layer.html"))

    if "<!-- SITE_MAIN_START -->" in out:
        after = out.split("<!-- SITE_MAIN_START -->", 1)[1]
        needs_main = not re.match(r"^\s*<main[\s>]", after)
        out = out.replace("<!-- SITE_MAIN_START -->", "<main id=\"main-content\">" if needs_main else "")
        out = out.replace("<!-- SITE_MAIN_END -->", "</main>" if needs_main else "")

    out = out.replace("mailto:suppaporn.2544@gmail.com", f"mailto:{COLLAB_EMAIL}")
    out = inject_base_tag(out, lang)

    page_i18n_ns = {
        "about.html": "about",
        "research.html": "research",
        "publications.html": "publications",
        "talks.html": "talks",
        "projects.html": "projects",
        "cv.html": "cv",
        "cram.html": "cram",
        "gsat.html": "gsat",
    }

    if lang != "en":
        out = re.sub(r'<html\s+lang="[^"]*"', f'<html lang="{lang}"', out, count=1)
        loc = load_locale(lang)
        # Localize document title + meta description when keys exist
        ns = page_i18n_ns.get(filename)
        if ns:
            title = get_by_path(loc, f"{ns}.title")
            if title:
                out = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", out, count=1, flags=re.S)
            desc = get_by_path(loc, f"{ns}.desc")
            if desc:
                safe = (
                    desc.replace("&", "&amp;")
                    .replace('"', "&quot;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                out = re.sub(
                    r'(<meta name="description" content=")[^"]*(")',
                    rf"\1{safe}\2",
                    out,
                    count=1,
                )
        out = apply_i18n_build(out, loc)
        out = rewrite_root_assets(out, asset_prefix or "../")
        out = fix_locale_lang_switch(out, filename, lang)
        # After asset rewrite, re-assert base for this locale
        out = inject_base_tag(out, lang)

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
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("Build complete. Output in docs/ (en) + docs/th + docs/ja")


if __name__ == "__main__":
    main()
