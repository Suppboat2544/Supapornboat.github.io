/* ── NAV ── */
function toggleMenu() {
  const links = document.querySelector('.nav-links');
  const burger = document.querySelector('.nav-burger');
  if (!links) return;

  const isOpen = links.classList.toggle('open');
  burger?.classList.toggle('open', isOpen);
  burger?.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  document.body.classList.toggle('menu-open', isOpen);
}

function closeMenu() {
  const links = document.querySelector('.nav-links');
  const burger = document.querySelector('.nav-burger');
  links?.classList.remove('open');
  burger?.classList.remove('open');
  burger?.setAttribute('aria-expanded', 'false');
  document.body.classList.remove('menu-open');
}

document.querySelectorAll('.nav-links a').forEach(a => {
  a.addEventListener('click', closeMenu);
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeMenu();
});

const nav = document.getElementById('nav');
if (nav) {
  window.addEventListener('scroll', () => {
    const scrolled = window.scrollY > 10;
    if (nav.classList.contains('nav-cinematic-bar')) {
      nav.classList.toggle('scrolled', scrolled);
    } else if (!nav.classList.contains('nav-cinematic')) {
      nav.style.boxShadow = scrolled ? '0 4px 28px rgba(0,0,0,.45)' : '';
    }
  }, { passive: true });
}

/* ── REDUCED MOTION ── */
if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  document.querySelectorAll('[class*="animate-fade"]').forEach(el => {
    el.style.animation = 'none';
    el.style.opacity = '1';
    el.style.transform = 'none';
  });
  const heroVideo = document.querySelector('.hero-video');
  if (heroVideo) {
    heroVideo.pause();
    heroVideo.removeAttribute('autoplay');
  }
}

/* ── SCROLL REVEAL ── */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('revealed');
      revealObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

document.querySelectorAll('[data-reveal]').forEach(el => revealObserver.observe(el));

/* ── STAT COUNT-UP ── */
function animateCount(el, target, duration) {
  const start = performance.now();
  const update = (now) => {
    const progress = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(ease * target);
    if (progress < 1) requestAnimationFrame(update);
  };
  requestAnimationFrame(update);
}

const statsObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.querySelectorAll('.stat-num[data-count]').forEach(el => {
        animateCount(el, parseInt(el.dataset.count, 10), 1200);
      });
      statsObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

const statsEl = document.querySelector('.stats-strip');
if (statsEl) statsObserver.observe(statsEl);

/* ── ABOUT: RESEARCH EXPANDABLES ── */
function initAboutExpandables() {
  const items = document.querySelectorAll('.research-item.expandable');
  if (!items.length) return;

  items.forEach((item) => {
    const toggle = item.querySelector('.research-toggle') || item;
    if (!toggle) return;

    const setExpanded = (open) => {
      items.forEach(i => {
        i.classList.remove('open');
        const btn = i.querySelector('.research-toggle') || i;
        btn.setAttribute('aria-expanded', 'false');
      });
      if (open) {
        item.classList.add('open');
        toggle.setAttribute('aria-expanded', 'true');
      }
    };

    const onActivate = () => {
      const willOpen = !item.classList.contains('open');
      setExpanded(willOpen);
    };

    if (toggle.classList.contains('research-toggle')) {
      toggle.addEventListener('click', onActivate);
    } else {
      toggle.setAttribute('role', 'button');
      toggle.setAttribute('tabindex', '0');
      toggle.setAttribute('aria-expanded', 'false');
      toggle.addEventListener('click', onActivate);
      toggle.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onActivate();
        }
      });
    }
  });
}

/* ── RESEARCH: FILTERS + MODALS ── */
let lastModalFocus = null;

function closeResearchModal(overlay) {
  if (!overlay) return;
  overlay.classList.remove('open');
  overlay.removeAttribute('aria-modal');
  const dialog = overlay.querySelector('.ri-modal');
  if (dialog) {
    dialog.removeAttribute('role');
    dialog.removeAttribute('aria-labelledby');
  }
  document.body.style.overflow = '';
  if (lastModalFocus) {
    lastModalFocus.focus();
    lastModalFocus = null;
  }
}

function openResearchModal(id) {
  const overlay = document.getElementById(id);
  if (!overlay) return;

  lastModalFocus = document.activeElement;
  overlay.classList.add('open');
  overlay.setAttribute('aria-modal', 'true');

  const dialog = overlay.querySelector('.ri-modal');
  const title = overlay.querySelector('.ri-modal h2, .ri-modal h3');
  if (dialog) {
    dialog.setAttribute('role', 'dialog');
    if (title) dialog.setAttribute('aria-labelledby', title.id || (title.id = 'modal-title-' + id));
  }

  document.body.style.overflow = 'hidden';
  const closeBtn = overlay.querySelector('.ri-modal-close');
  closeBtn?.focus();
}

function initResearchPage() {
  const grid = document.getElementById('riGrid');
  if (!grid) return;

  let emptyMsg = document.getElementById('riEmpty');
  if (!emptyMsg) {
    emptyMsg = document.createElement('p');
    emptyMsg.id = 'riEmpty';
    emptyMsg.className = 'ri-empty-msg';
    emptyMsg.hidden = true;
    emptyMsg.textContent = 'No topics match this filter.';
    grid.parentNode.insertBefore(emptyMsg, grid.nextSibling);
  }

  document.querySelectorAll('.ri-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.ri-filter').forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');

      const filter = btn.dataset.filter;
      let visible = 0;
      document.querySelectorAll('.ri-card').forEach(card => {
        const show = filter === 'all' || card.dataset.tags.includes(filter);
        card.style.display = show ? '' : 'none';
        if (show) visible++;
      });
      emptyMsg.hidden = visible > 0;
    });
    btn.setAttribute('aria-pressed', btn.classList.contains('active') ? 'true' : 'false');
  });

  document.querySelectorAll('.ri-card[data-modal]').forEach(card => {
    const open = () => openResearchModal(card.dataset.modal);
    card.addEventListener('click', open);
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        open();
      }
    });
  });

  document.querySelectorAll('.ri-modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeResearchModal(overlay);
    });
    overlay.querySelector('.ri-modal-close')?.addEventListener('click', () => closeResearchModal(overlay));
  });

  document.addEventListener('keydown', (e) => {
    if (e.key !== 'Escape') return;
    document.querySelectorAll('.ri-modal-overlay.open').forEach(closeResearchModal);
  });
}

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', () => {
  initAboutExpandables();
  initResearchPage();
  initSectionLoadPhase();
});

/* ── SECTION LOAD PHASE (Win95-style) ── */
function initSectionLoadPhase() {
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  let overlay = document.getElementById('section-load');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'section-load';
    overlay.className = 'section-load';
    overlay.hidden = true;
    overlay.setAttribute('aria-live', 'polite');
    overlay.innerHTML =
      '<div class="section-load-panel">' +
      '  <div class="section-load-titlebar"><span>⏳</span><span id="section-load-title">Loading…</span></div>' +
      '  <div class="section-load-body">' +
      '    <p id="section-load-msg">Opening section…</p>' +
      '    <div class="section-load-track"><i id="section-load-bar"></i></div>' +
      '  </div>' +
      '</div>';
    document.body.appendChild(overlay);
  }

  const titleEl = () => document.getElementById('section-load-title');
  const msgEl = () => document.getElementById('section-load-msg');
  const barEl = () => document.getElementById('section-load-bar');

  function labelFromHref(href) {
    try {
      const u = new URL(href, location.href);
      const file = (u.pathname.split('/').pop() || 'index.html').replace(/\.html$/, '') || 'home';
      const map = {
        index: 'Home',
        about: 'About Me',
        research: 'Research',
        publications: 'Publications',
        talks: 'Talks',
        projects: 'Projects',
        cv: 'Curriculum Vitae',
        cram: 'CRAM-GTransformer',
        gsat: 'GSAT Model',
        win95: 'BoatOS Desktop',
      };
      return map[file] || file;
    } catch (_) {
      return 'section';
    }
  }

  function showLoad(label) {
    overlay.hidden = false;
    overlay.classList.add('is-open');
    if (titleEl()) titleEl().textContent = label + '.exe';
    if (msgEl()) msgEl().textContent = 'Loading ' + label + '…';
    if (barEl()) barEl().style.width = '0%';
    requestAnimationFrame(() => {
      if (barEl()) barEl().style.width = '100%';
    });
  }

  function go(href) {
    showLoad(labelFromHref(href));
    const delay = 720;
    setTimeout(() => { location.href = href; }, delay);
  }

  function shouldIntercept(a) {
    if (!a || a.target === '_blank' || a.hasAttribute('download')) return false;
    const href = a.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('mailto:') || href.startsWith('tel:')) return false;
    if (href.startsWith('http') && !href.includes('Supapornboat.github.io') && !href.startsWith(location.origin)) {
      return false;
    }
    // Same-page hash only
    try {
      const u = new URL(href, location.href);
      if (u.pathname === location.pathname && u.hash) return false;
      if (u.origin !== location.origin && !href.includes('/Supapornboat.github.io/')) return false;
      // Only HTML pages / site sections
      const path = u.pathname;
      if (!/\.html?$/.test(path) && !/\/(th|ja)?\/?$/.test(path) && !path.endsWith('/')) return false;
      return true;
    } catch (_) {
      return /\.html/.test(href);
    }
  }

  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href]');
    if (!a || !shouldIntercept(a)) return;
    // Skip language switcher (already fast absolute nav)
    if (a.closest('.lang-switch')) return;
    e.preventDefault();
    closeMenu();
    go(a.href);
  }, true);
}
