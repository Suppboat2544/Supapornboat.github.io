/* BoatOS interactive layer for the multipage site */
(function () {
  "use strict";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const skipBoot = new URLSearchParams(location.search).has("skipboot")
    || sessionStorage.getItem("boatos-booted") === "1";

  /* ——— Boot / load bar ——— */
  function runBoot() {
    const screen = document.getElementById("site-boot");
    if (!screen) return Promise.resolve();
    if (reduce || skipBoot) {
      screen.classList.add("boot-done");
      screen.hidden = true;
      sessionStorage.setItem("boatos-booted", "1");
      return Promise.resolve();
    }

    const bar = document.getElementById("site-boot-bar");
    const status = document.getElementById("site-boot-status");
    const bios = document.getElementById("site-boot-bios");
    const lines = [
      "BoatOS BIOS 95",
      "Detecting portfolio modules...",
      "  GNN core .............. OK",
      "  Cheminformatics ....... OK",
      "  HPC pipelines ......... OK",
      "",
      "Loading desktop...",
    ];
    const statuses = ["Starting BoatOS…", "Loading figures…", "Mounting research…", "Welcome."];

    return (async () => {
      let text = "";
      for (const line of lines) {
        text += line + "\n";
        if (bios) bios.textContent = text;
        await wait(70);
      }
      for (let p = 0; p <= 100; p += 2) {
        if (bar) bar.style.width = p + "%";
        if (status) status.textContent = statuses[Math.min(statuses.length - 1, Math.floor(p / 28))];
        await wait(22);
      }
      await wait(180);
      screen.classList.add("boot-done");
      sessionStorage.setItem("boatos-booted", "1");
      setTimeout(() => { screen.hidden = true; }, 450);
    })();
  }

  function wait(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  /* ——— Clock ——— */
  function tickClock() {
    document.querySelectorAll("[data-win-clock]").forEach((el) => {
      const now = new Date();
      const h = now.getHours();
      const m = String(now.getMinutes()).padStart(2, "0");
      const h12 = ((h + 11) % 12) + 1;
      el.textContent = `${h12}:${m} ${h >= 12 ? "PM" : "AM"}`;
    });
  }

  /* ——— Dialogs ——— */
  function openDialog(id) {
    const dlg = document.getElementById(id);
    if (!dlg) return;
    dlg.hidden = false;
    dlg.classList.add("is-open");
    const focus = dlg.querySelector("button, [href], input");
    focus?.focus();
  }

  function closeDialog(id) {
    const dlg = document.getElementById(id);
    if (!dlg) return;
    dlg.classList.remove("is-open");
    dlg.hidden = true;
  }

  document.querySelectorAll("[data-open-dialog]").forEach((el) => {
    el.addEventListener("click", () => openDialog(el.getAttribute("data-open-dialog")));
  });

  document.querySelectorAll("[data-close-dialog]").forEach((el) => {
    el.addEventListener("click", () => closeDialog(el.getAttribute("data-close-dialog")));
  });

  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    document.querySelectorAll(".win-dialog.is-open").forEach((dlg) => {
      dlg.classList.remove("is-open");
      dlg.hidden = true;
    });
  });

  /* ——— Window chrome on homepage panels ——— */
  document.querySelectorAll("[data-win-panel]").forEach((panel) => {
    const minBtn = panel.querySelector("[data-win-min]");
    const maxBtn = panel.querySelector("[data-win-max]");
    const closeBtn = panel.querySelector("[data-win-close]");
    const body = panel.querySelector("[data-win-body]");

    minBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      panel.classList.toggle("is-min");
      if (body) body.hidden = panel.classList.contains("is-min");
    });
    maxBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      panel.classList.toggle("is-max");
    });
    closeBtn?.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      panel.classList.add("is-closed");
      setTimeout(() => { panel.style.display = "none"; }, 200);
    });
  });

  /* ——— Progress meters ——— */
  const meterObs = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (!entry.isIntersecting) return;
      const fill = entry.target.querySelector("[data-meter-fill]");
      const target = Number(entry.target.getAttribute("data-meter") || "80");
      if (fill) {
        fill.style.width = "0%";
        requestAnimationFrame(() => { fill.style.width = target + "%"; });
      }
      meterObs.unobserve(entry.target);
    });
  }, { threshold: 0.35 });

  document.querySelectorAll("[data-meter]").forEach((el) => meterObs.observe(el));

  /* ——— Gallery lightbox ——— */
  document.querySelectorAll("[data-lightbox]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      const src = el.getAttribute("data-lightbox") || el.querySelector("img")?.src;
      const title = el.getAttribute("data-lightbox-title") || "Image Preview";
      const img = document.getElementById("lightbox-img");
      const titleEl = document.getElementById("lightbox-title");
      if (img && src) img.src = src;
      if (titleEl) titleEl.textContent = title;
      openDialog("dlg-lightbox");
    });
  });

  /* ——— Start menu ——— */
  const startBtn = document.getElementById("site-start-btn");
  const startMenu = document.getElementById("site-start-menu");
  startBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = startMenu?.hidden;
    if (startMenu) startMenu.hidden = !open;
    startBtn.classList.toggle("is-pressed", !!open);
  });
  document.addEventListener("click", () => {
    if (startMenu && !startMenu.hidden) {
      startMenu.hidden = true;
      startBtn?.classList.remove("is-pressed");
    }
  });

  /* ——— Skills tabs on homepage ——— */
  document.querySelectorAll("[data-skill-tab]").forEach((tab) => {
    tab.addEventListener("click", () => {
      const id = tab.getAttribute("data-skill-tab");
      document.querySelectorAll("[data-skill-tab]").forEach((t) => {
        const on = t === tab;
        t.classList.toggle("is-active", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
      });
      document.querySelectorAll("[data-skill-panel]").forEach((p) => {
        const on = p.getAttribute("data-skill-panel") === id;
        p.hidden = !on;
        p.classList.toggle("is-active", on);
      });
    });
  });

  tickClock();
  setInterval(tickClock, 1000);
  runBoot().then(() => {
    if (window.BoatOSSong && typeof window.BoatOSSong.autoplayLoop === "function") {
      window.BoatOSSong.autoplayLoop();
    }
  });
})();
