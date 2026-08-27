const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const SRC = path.join(ROOT, 'src');
const OUT = path.join(ROOT, 'docs');
const SNIPPETS = path.join(SRC, 'snippets');

const SITE_BASE = 'https://suppboat2544.github.io/Supapornboat.github.io';
const OG_IMAGE = 'https://avatars.githubusercontent.com/u/179722549?v=4';
const COLLAB_EMAIL = 'klabklaydee.s.aa@m.titech.ac.jp';

const NAV_ITEMS = [
  { id: 'home', href: 'index.html', label: 'Home' },
  { id: 'about', href: 'about.html', label: 'About' },
  { id: 'research', href: 'research.html', label: 'Research' },
  { id: 'publications', href: 'publications.html', label: 'Publications' },
  { id: 'talks', href: 'talks.html', label: 'Talks' },
  { id: 'projects', href: 'projects.html', label: 'Projects' },
  { id: 'cv', href: 'cv.html', label: 'CV' },
];

const HIGHLIGHT_ITEMS = [
  { id: 'cram', href: 'cram.html', label: 'CRAM' },
  { id: 'gsat', href: 'gsat.html', label: 'GSAT' },
  { id: 'win95', href: 'win95.html', label: 'BoatOS' },
];

const PAGE_META = {
  'index.html': {
    active: 'home',
    ogTitle: 'Supaporn Klabklaydee | Cheminformatics · Environmental Chemistry',
    navVariant: 'home',
  },
  'about.html': { active: 'about', ogTitle: 'About · Supaporn Klabklaydee' },
  'research.html': { active: 'research', ogTitle: 'Research · Supaporn Klabklaydee' },
  'publications.html': { active: 'publications', ogTitle: 'Publications · Supaporn Klabklaydee' },
  'talks.html': { active: 'talks', ogTitle: 'Talks & Presentations · Supaporn Klabklaydee' },
  'projects.html': { active: 'projects', ogTitle: 'Projects · Supaporn Klabklaydee' },
  'cv.html': { active: 'cv', ogTitle: 'CV · Supaporn Klabklaydee' },
  'cram.html': { active: 'cram', ogTitle: 'CRAM-GTransformer · Supaporn Klabklaydee', highlight: 'cram' },
  'gsat.html': { active: 'gsat', ogTitle: 'GSAT Model · Supaporn Klabklaydee', highlight: 'gsat' },
  'win95.html': { active: null, ogTitle: 'BoatOS 95 · Supaporn Klabklaydee', minimalNav: true },
  '404.html': { active: null, ogTitle: 'Page not found · Supaporn Klabklaydee', minimalNav: true },
};

function readSnippet(name) {
  return fs.readFileSync(path.join(SNIPPETS, name), 'utf8');
}

function navLink(item, activeId, extraClass = '') {
  const isActive = item.id === activeId;
  const cls = [extraClass, isActive ? 'active' : ''].filter(Boolean).join(' ');
  const attrs = isActive ? ' class="' + cls + '" aria-current="page"' : (cls ? ' class="' + cls + '"' : '');
  return '<li><a href="' + item.href + '"' + attrs + '>' + item.label + '</a></li>';
}

function buildNav(filename) {
  const meta = PAGE_META[filename] || {};
  const active = meta.active;
  const isHome = meta.navVariant === 'home';

  if (meta.minimalNav) {
    return (
      '  <nav class="nav nav-cinematic nav-cinematic-bar" id="nav" aria-label="Main navigation">\n' +
      '    <div class="nav-cinematic-inner">\n' +
      '      <a href="index.html" class="nav-cinematic-logo">\n' +
      '        <span class="nav-logo-mark">SK</span>\n' +
      '        <span class="nav-logo-sub">BoatOS 95</span>\n' +
      '      </a>\n' +
      '      <div class="nav-cinematic-actions">\n' +
      '        <a href="index.html" class="nav-cinematic-cta">Home</a>\n' +
      '      </div>\n' +
      '    </div>\n' +
      '  </nav>'
    );
  }

  const navClass = isHome ? 'nav nav-cinematic' : 'nav nav-cinematic nav-cinematic-bar';
  const logoCurrent = active === 'home' ? ' aria-current="page"' : '';
  const links = NAV_ITEMS.map((item) => navLink(item, active)).join('\n          ');
  const highlights = HIGHLIGHT_ITEMS.map((item) =>
    navLink(item, meta.highlight || null, 'nav-cinematic-highlight')
  ).join('\n          ');

  if (isHome) {
    return (
      '      <nav class="' + navClass + '" id="nav" aria-label="Main navigation">\n' +
      '        <div class="nav-cinematic-inner">\n' +
      '      <a href="index.html" class="nav-cinematic-logo"' + logoCurrent + '>\n' +
      '        <span class="nav-logo-mark">SK</span>\n' +
      '        <span class="nav-logo-sub">BoatOS 95</span>\n' +
      '      </a>\n' +
      '      <ul class="nav-links nav-cinematic-links" id="nav-links">\n' +
      '          ' + links + '\n' +
      '          ' + highlights + '\n' +
      '      </ul>\n' +
      '      <div class="nav-cinematic-actions">\n' +
      '        <a href="mailto:' + COLLAB_EMAIL + '" class="nav-cinematic-cta">Collaborate</a>\n' +
      '        <button class="nav-burger nav-cinematic-burger" type="button" aria-label="Toggle menu" aria-expanded="false" aria-controls="nav-links" onclick="toggleMenu()">\n' +
      '          <span></span><span></span><span></span>\n' +
      '        </button>\n' +
      '      </div>\n' +
      '        </div>\n' +
      '      </nav>'
    );
  }

  return (
    '  <a class="skip-link" href="#main-content">Skip to content</a>\n' +
    '  <nav class="' + navClass + '" id="nav" aria-label="Main navigation">\n' +
    '    <div class="nav-cinematic-inner">\n' +
    '      <a href="index.html" class="nav-cinematic-logo">\n' +
    '        <span class="nav-logo-mark">SK</span>\n' +
    '        <span class="nav-logo-sub">BoatOS 95</span>\n' +
    '      </a>\n' +
    '      <ul class="nav-links nav-cinematic-links" id="nav-links">\n' +
    '          ' + links + '\n' +
    '          ' + highlights + '\n' +
    '      </ul>\n' +
    '      <div class="nav-cinematic-actions">\n' +
    '        <a href="mailto:' + COLLAB_EMAIL + '" class="nav-cinematic-cta">Collaborate</a>\n' +
    '        <button class="nav-burger nav-cinematic-burger" type="button" aria-label="Toggle menu" aria-expanded="false" aria-controls="nav-links" onclick="toggleMenu()">\n' +
    '          <span></span><span></span><span></span>\n' +
    '        </button>\n' +
    '      </div>\n' +
    '    </div>\n' +
    '  </nav>'
  );
}

function buildOgTags(filename, content) {
  const meta = PAGE_META[filename];
  if (!meta || !meta.ogTitle) return content;

  const descMatch = content.match(/<meta name="description" content="([^"]*)"/);
  const desc = descMatch ? descMatch[1] : '';
  const url = filename === 'index.html' ? SITE_BASE + '/' : SITE_BASE + '/' + filename;

  if (content.includes('property="og:title"')) return content;

  const og = [
    '  <meta property="og:type" content="website" />',
    '  <meta property="og:url" content="' + url + '" />',
    '  <meta property="og:title" content="' + meta.ogTitle + '" />',
    '  <meta property="og:description" content="' + desc + '" />',
    '  <meta property="og:image" content="' + OG_IMAGE + '" />',
    '  <meta name="twitter:card" content="summary" />',
    '  <meta name="twitter:title" content="' + meta.ogTitle + '" />',
    '  <meta name="twitter:description" content="' + desc + '" />',
    '  <meta name="twitter:image" content="' + OG_IMAGE + '" />',
  ].join('\n');

  return content.replace(/<link rel="canonical"[^>]*>/, (m) => m + '\n' + og);
}

function processHtml(content, filename) {
  const year = new Date().getFullYear();
  let out = content.replace(/{{\s*year\s*}}/g, String(year));

  if (out.includes('<!-- SITE_HEAD_ICONS -->')) {
    out = out.replace('<!-- SITE_HEAD_ICONS -->', readSnippet('head-icons.html'));
  } else if (!out.includes('rel="icon"')) {
    out = out.replace('</head>', readSnippet('head-icons.html') + '\n</head>');
  }

  out = buildOgTags(filename, out);

  if (out.includes('<!-- SITE_NAV -->')) {
    out = out.replace('<!-- SITE_NAV -->', buildNav(filename));
  }

  if (out.includes('<!-- SITE_FOOTER -->')) {
    out = out.replace('<!-- SITE_FOOTER -->', readSnippet('footer.html').replace(/{{\s*year\s*}}/g, String(year)));
  }

  if (out.includes('<!-- SITE_MOL_LAYER -->')) {
    out = out.replace('<!-- SITE_MOL_LAYER -->', readSnippet('page-mol-layer.html'));
  }

  // Wrap inner page body content in <main> if marker present
  if (out.includes('<!-- SITE_MAIN_START -->')) {
    const afterStart = out.split('<!-- SITE_MAIN_START -->')[1] || '';
    const needsMain = !/^\s*<main[\s>]/i.test(afterStart);
    out = out.replace('<!-- SITE_MAIN_START -->', needsMain ? '<main id="main-content">' : '');
    out = out.replace('<!-- SITE_MAIN_END -->', needsMain ? '</main>' : '');
  }

  // Normalize collaboration emails in built output
  out = out.replace(/mailto:suppaporn\.2544@gmail\.com/g, 'mailto:' + COLLAB_EMAIL);

  return out;
}

async function rmrf(dir) {
  if (!fs.existsSync(dir)) return;
  await fs.promises.rm(dir, { recursive: true, force: true });
}

async function copyRecursive(src, dest, rel = '') {
  const stat = await fs.promises.stat(src);
  if (stat.isDirectory()) {
    if (path.basename(src) === 'snippets') return;
    await fs.promises.mkdir(dest, { recursive: true });
    const entries = await fs.promises.readdir(src);
    for (const e of entries) {
      await copyRecursive(path.join(src, e), path.join(dest, e), path.join(rel, e));
    }
  } else {
    let content = await fs.promises.readFile(src);
    const ext = path.extname(src).toLowerCase();
    const basename = path.basename(src);
    if (['.html', '.htm'].includes(ext)) {
      content = processHtml(content.toString(), basename);
    } else if (['.css', '.js', '.txt'].includes(ext)) {
      content = content.toString().replace(/{{\s*year\s*}}/g, String(year));
    }
    await fs.promises.mkdir(path.dirname(dest), { recursive: true });
    await fs.promises.writeFile(dest, content);
  }
}

const year = new Date().getFullYear();

(async () => {
  try {
    await rmrf(OUT);
    await copyRecursive(SRC, OUT);
    console.log('Build complete. Output in docs/');
  } catch (err) {
    console.error('Build failed:', err);
    process.exit(1);
  }
})();
