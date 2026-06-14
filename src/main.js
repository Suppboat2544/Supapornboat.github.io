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
        animateCount(el, parseInt(el.dataset.count), 1200);
      });
      statsObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.5 });

const statsEl = document.querySelector('.stats-strip');
if (statsEl) statsObserver.observe(statsEl);
