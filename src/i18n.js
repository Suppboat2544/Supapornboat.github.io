/* BoatOS i18n — EN / TH / JA */
(function () {
  "use strict";

  function detectLang() {
    const q = new URLSearchParams(location.search).get("lang");
    if (q === "th" || q === "ja" || q === "en") return q;
    if (/\/th(\/|$)/.test(location.pathname)) return "th";
    if (/\/ja(\/|$)/.test(location.pathname)) return "ja";
    const stored = localStorage.getItem("boatos-lang");
    if (stored === "th" || stored === "ja" || stored === "en") return stored;
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
      a.classList.toggle("is-active", a.getAttribute("data-lang") === dict.lang);
    });
  }

  function langHref(lang) {
    const file = (location.pathname.split("/").pop() || "index.html");
    const page = file.includes(".html") ? file : "index.html";
    if (lang === "en") return assetPrefix() ? "../" + page : page;
    if (assetPrefix()) {
      return lang === detectLang() ? page : "../" + lang + "/" + page;
    }
    return lang + "/" + (page === "index.html" ? "index.html" : page);
  }

  window function init() {
    const lang = detectLang();
    localStorage.setItem("boatos-lang", lang);
    try {
      const dict = await loadLocale(lang);
      apply(dict);
      window.BoatOSI18n = { lang, dict, apply };
    } catch (e) {
      console.warn("i18n load failed", e);
    }

    document.querySelectorAll(".lang-switch a[data-lang]").forEach((a) => {
      a.addEventListener("click", () => {
        localStorage.setItem("boatos-lang", a.getAttribute("data-lang"));
      });
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
