function toggleMenu() {
  document.querySelector('.nav-links').classList.toggle('open');
}
// Close menu on link click
document.querySelectorAll('.nav-links a').forEach(a => {
  a.addEventListener('click', () => document.querySelector('.nav-links').classList.remove('open'));
});
// Scroll-based nav shadow
window.addEventListener('scroll', () => {
  document.getElementById('nav').style.boxShadow = window.scrollY > 10 ? '0 4px 24px rgba(0,0,0,.4)' : '';
});
