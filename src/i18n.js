/* BoatOS i18n — EN / TH / JA */
(function () {
  "use strict";

  const SITE_ROOT = "/Supapornboat.github.io";

  function detectLang() {
    const q = new URLSearchParams(location.search).get("lang");
    if (q === "th" || q === "ja" || q === "en") return q;
    if (/\/th(\/|$)/.test(location.pathname)) return "th";
    if (/\/ja(\/|$)/.test(location.pathname)) return "ja";
    return "en";
  }

  function assetPrefix() {
    return /\/(th|ja)(\/|$)/.test(location.pathname) ? "../" : "";
  }

  function getByPath(obj, path) {
    return path.split(".").reduce((o, k) => (o && o[k] != null ? o[k] : null), obj);
  }

  async function loadLocale(lang) {
    const url = assetPrefix() + "locales/" + lang + ".json";
    const res = await fetch(url);
    if (!res.ok) throw new Error("locale " + lang);
    return res.json();
  }

  function apply(dict) {
    document.documentElement.lang = dict.lang || "en";
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.getAttribute("data-i18n");
      const val = getByPath(dict, key);
      if (val != null) el.textContent = val;
    });
    document.querySelectorAll("[data-i18n-html]").forEach((el) => {
      const key = el.getAttribute("data-i18n-html");
      const val = getByPath(dict, key);
      if (val != null) el.innerHTML = val;
    });
    document.querySelectorAll("[data-i18n-nav]").forEach((el) => {
      const key = el.getAttribute("data-i18n-nav");
      const val = getByPath(dict, "nav." + key);
      if (val != null) el.textContent = val;
    });
    document.querySelectorAll(".lang-switch a").forEach((a) => {
      const lang = a.getAttribute("data-lang");
      a.classList.toggle("is-active", lang === dict.lang);
      // Keep absolute project-root links healthy on GitHub Pages
      const file = (location.pathname.split("/").pop() || "index.html");
      const page = file.includes(".html") ? file : "index.html";
      if (lang === "en") {
        a.href = page === "index.html" ? SITE_ROOT + "/" : SITE_ROOT + "/" + page;
      } else {
        a.href = SITE_ROOT + "/" + lang + "/" + page;
      }
    });
  }

  async function init() {
    const lang = detectLang();
    try {
      const dict = await loadLocale(lang);
      apply(dict);
      window.BoatOSI18n = { lang, dict, apply };
    } catch (e) {
      console.warn("i18n load failed", e);
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
