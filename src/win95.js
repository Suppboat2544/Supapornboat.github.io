(() => {
  "use strict";

  const BOOT_LINES = [
    "BoatOS BIOS Version 1.0",
    "Copyright (C) 2026 Supaporn Klabklaydee",
    "",
    "Detecting hardware...",
    "  CPU: Neural Graph Processor OK",
    "  RAM: 64MB Cheminformatics OK",
    "  HDD: Portfolio.drv OK",
    "",
    "Loading BoatOS 95...",
  ];

  const BOOT_STATUS = [
    "Starting BoatOS…",
    "Loading system fonts…",
    "Mounting desktop…",
    "Starting Explorer…",
    "Welcome.",
  ];

  const WINDOW_DEFAULTS = {
    about: { top: 48, left: 110, width: 440, height: 360, title: "About Me.txt", icon: "📄" },
    projects: { top: 64, left: 150, width: 460, height: 380, title: "Projects", icon: "📁" },
    skills: { top: 80, left: 190, width: 420, height: 340, title: "Skills.exe", icon: "💾" },
    contact: { top: 96, left: 230, width: 400, height: 360, title: "Contact", icon: "✉️" },
  };

  let zTop = 100;
  let bootDone = false;

  const bootScreen = document.getElementById("boot-screen");
  const bootBios = document.getElementById("boot-bios");
  const bootBar = document.getElementById("boot-bar");
  const bootStatus = document.getElementById("boot-status");
  const desktop = document.getElementById("desktop");
  const startBtn = document.getElementById("start-btn");
  const startMenu = document.getElementById("start-menu");
  const taskbarApps = document.getElementById("taskbar-apps");
  const clockEl = document.getElementById("clock");
  const shutdownScreen = document.getElementById("shutdown-screen");

  /* ——— Boot ——— */
  async function runBoot() {
    const preferReduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (preferReduce || new URLSearchParams(location.search).has("skipboot")) {
      finishBoot();
      return;
    }

    let text = "";
    for (let i = 0; i < BOOT_LINES.length; i++) {
      text += BOOT_LINES[i] + "\n";
      bootBios.textContent = text;
      await wait(preferReduce ? 0 : 90 + Math.random() * 60);
    }

    for (let p = 0; p <= 100; p += 2) {
      bootBar.style.width = p + "%";
      bootStatus.textContent = BOOT_STATUS[Math.min(BOOT_STATUS.length - 1, Math.floor(p / 25))];
      await wait(28);
    }
    await wait(220);
    finishBoot();
  }

  function finishBoot() {
    bootDone = true;
    bootScreen.classList.add("boot-done");
    desktop.hidden = false;
    setTimeout(() => {
      bootScreen.hidden = true;
      openWindow("about");
    }, 500);
  }

  function wait(ms) {
    return new Promise((r) => setTimeout(r, ms));
  }

  /* ——— Clock ——— */
  function updateClock() {
    const now = new Date();
    const h = now.getHours();
    const m = String(now.getMinutes()).padStart(2, "0");
    const h12 = ((h + 11) % 12) + 1;
    const ampm = h >= 12 ? "PM" : "AM";
    clockEl.textContent = `${h12}:${m} ${ampm}`;
    clockEl.dateTime = now.toISOString();
  }

  /* ——— Windows ——— */
  function getWin(id) {
    return document.getElementById("win-" + id);
  }

  function bringToFront(win) {
    zTop += 1;
    win.style.zIndex = String(zTop);
    document.querySelectorAll(".win95-window").forEach((w) => w.classList.remove("is-active"));
    win.classList.add("is-active");
    syncTaskbar();
  }

  function placeWindow(win, id) {
    const d = WINDOW_DEFAULTS[id];
    const mobile = window.matchMedia("(max-width: 700px)").matches;
    if (!win.dataset.placed) {
      if (mobile) {
        win.style.top = "40px";
        win.style.left = "8px";
        win.style.width = "calc(100% - 16px)";
        win.style.height = "min(70vh, 420px)";
      } else {
        win.style.top = d.top + "px";
        win.style.left = d.left + "px";
        win.style.width = d.width + "px";
        win.style.height = d.height + "px";
      }
      win.dataset.placed = "1";
    }
  }

  function openWindow(id) {
    const win = getWin(id);
    if (!win) return;
    closeStartMenu();

    const wasHidden = win.style.display === "none" || win.classList.contains("is-minimized");
    win.style.display = "flex";
    win.classList.remove("is-minimized", "is-closing");
    placeWindow(win, id);
    bringToFront(win);

    if (wasHidden) {
      win.classList.remove("is-opening");
      void win.offsetWidth;
      win.classList.add("is-opening");
      win.addEventListener(
        "animationend",
        () => win.classList.remove("is-opening"),
        { once: true }
      );
    }
    syncTaskbar();
  }

  function closeWindow(id) {
    const win = getWin(id);
    if (!win || win.style.display === "none") return;
    win.classList.add("is-closing");
    win.classList.remove("is-maximized", "is-minimized");
    win.addEventListener(
      "animationend",
      () => {
        win.style.display = "none";
        win.classList.remove("is-closing", "is-active");
        syncTaskbar();
      },
      { once: true }
    );
  }

  function minimizeWindow(id) {
    const win = getWin(id);
    if (!win) return;
    win.classList.add("is-minimized");
    win.classList.remove("is-active");
    syncTaskbar();
  }

  function maximizeWindow(id) {
    const win = getWin(id);
    if (!win) return;
    if (win.classList.contains("is-maximized")) {
      win.classList.remove("is-maximized");
      if (win.dataset.prevRect) {
        const [t, l, w, h] = win.dataset.prevRect.split(",");
        win.style.top = t;
        win.style.left = l;
        win.style.width = w;
        win.style.height = h;
      }
    } else {
      win.dataset.prevRect = [win.style.top, win.style.left, win.style.width, win.style.height].join(",");
      win.classList.add("is-maximized");
    }
    bringToFront(win);
  }

  function syncTaskbar() {
    taskbarApps.innerHTML = "";
    Object.keys(WINDOW_DEFAULTS).forEach((id) => {
      const win = getWin(id);
      if (!win || win.style.display === "none") return;
      const d = WINDOW_DEFAULTS[id];
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "task-btn";
      if (win.classList.contains("is-active") && !win.classList.contains("is-minimized")) {
        btn.classList.add("is-active");
      }
      btn.innerHTML = `<span aria-hidden="true">${d.icon}</span> ${d.title}`;
      btn.addEventListener("click", () => {
        if (win.classList.contains("is-minimized")) {
          win.classList.remove("is-minimized");
          bringToFront(win);
        } else if (win.classList.contains("is-active")) {
          minimizeWindow(id);
        } else {
          bringToFront(win);
        }
      });
      taskbarApps.appendChild(btn);
    });
  }

  /* ——— Drag ——— */
  function bindDrag(win) {
    const bar = win.querySelector("[data-drag]");
    if (!bar) return;
    let dragging = false;
    let ox = 0;
    let oy = 0;

    const onDown = (e) => {
      if (e.target.closest(".win95-btn") || win.classList.contains("is-maximized")) return;
      dragging = true;
      bringToFront(win);
      const rect = win.getBoundingClientRect();
      const pt = point(e);
      ox = pt.x - rect.left;
      oy = pt.y - rect.top;
      win.style.transition = "none";
      e.preventDefault();
    };

    const onMove = (e) => {
      if (!dragging) return;
      const pt = point(e);
      const desk = desktop.getBoundingClientRect();
      let left = pt.x - ox - desk.left;
      let top = pt.y - oy - desk.top;
      const maxL = desk.width - 80;
      const maxT = desk.height - 56;
      left = Math.max(-win.offsetWidth + 80, Math.min(left, maxL));
      top = Math.max(0, Math.min(top, maxT));
      win.style.left = left + "px";
      win.style.top = top + "px";
    };

    const onUp = () => {
      if (!dragging) return;
      dragging = false;
      win.style.transition = "";
    };

    bar.addEventListener("pointerdown", onDown);
    window.addEventListener("pointermove", onMove);
    window.addEventListener("pointerup", onUp);
  }

  /* ——— Resize ——— */
  function bindResize(win) {
    const handle = win.querySelector("[data-resize]");
    if (!handle) return;
    let resizing = false;
    let startX = 0;
    let startY = 0;
    let startW = 0;
    let startH = 0;

    handle.addEventListener("pointerdown", (e) => {
      if (win.classList.contains("is-maximized")) return;
      resizing = true;
      bringToFront(win);
      const pt = point(e);
      startX = pt.x;
      startY = pt.y;
      startW = win.offsetWidth;
      startH = win.offsetHeight;
      win.style.transition = "none";
      e.preventDefault();
      e.stopPropagation();
    });

    window.addEventListener("pointermove", (e) => {
      if (!resizing) return;
      const pt = point(e);
      const w = Math.max(260, startW + (pt.x - startX));
      const h = Math.max(180, startH + (pt.y - startY));
      win.style.width = w + "px";
      win.style.height = h + "px";
    });

    window.addEventListener("pointerup", () => {
      if (!resizing) return;
      resizing = false;
      win.style.transition = "";
    });
  }

  function point(e) {
    if (e.touches && e.touches[0]) {
      return { x: e.touches[0].clientX, y: e.touches[0].clientY };
    }
    return { x: e.clientX, y: e.clientY };
  }

  /* ——— Wire windows ——— */
  document.querySelectorAll(".win95-window").forEach((win) => {
    const id = win.dataset.window;
    bindDrag(win);
    bindResize(win);
    win.addEventListener("pointerdown", () => bringToFront(win));

    win.querySelectorAll("[data-action]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const action = btn.dataset.action;
        if (action === "close") closeWindow(id);
        if (action === "minimize") minimizeWindow(id);
        if (action === "maximize") maximizeWindow(id);
      });
    });

    const titlebar = win.querySelector("[data-drag]");
    if (titlebar) {
      titlebar.addEventListener("dblclick", () => maximizeWindow(id));
    }
  });

  document.querySelectorAll("[data-open]").forEach((el) => {
    el.addEventListener("click", () => openWindow(el.dataset.open));
  });

  /* Skills tabs */
  document.querySelectorAll(".skills-tab").forEach((tab) => {
    tab.addEventListener("click", () => {
      const panel = tab.dataset.tab;
      document.querySelectorAll(".skills-tab").forEach((t) => {
        t.classList.toggle("active", t === tab);
        t.setAttribute("aria-selected", t === tab ? "true" : "false");
      });
      document.querySelectorAll(".skills-panel").forEach((p) => {
        p.hidden = p.dataset.panel !== panel;
      });
    });
  });

  /* Start menu */
  function closeStartMenu() {
    startMenu.hidden = true;
    startBtn.classList.remove("is-pressed");
    startBtn.setAttribute("aria-expanded", "false");
  }

  function toggleStartMenu() {
    const open = startMenu.hidden;
    startMenu.hidden = !open;
    startBtn.classList.toggle("is-pressed", open);
    startBtn.setAttribute("aria-expanded", open ? "true" : "false");
  }

  startBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    toggleStartMenu();
  });

  document.addEventListener("click", (e) => {
    if (!startMenu.hidden && !startMenu.contains(e.target) && e.target !== startBtn) {
      closeStartMenu();
    }
  });

  document.getElementById("shutdown-btn").addEventListener("click", () => {
    closeStartMenu();
    desktop.hidden = true;
    shutdownScreen.hidden = false;
  });

  document.getElementById("reboot-btn").addEventListener("click", () => {
    shutdownScreen.hidden = true;
    bootScreen.hidden = false;
    bootScreen.classList.remove("boot-done");
    bootBios.textContent = "";
    bootBar.style.width = "0%";
    bootStatus.textContent = "Starting BoatOS…";
    Object.keys(WINDOW_DEFAULTS).forEach((id) => {
      const win = getWin(id);
      win.style.display = "none";
      win.classList.remove("is-minimized", "is-maximized", "is-active");
      delete win.dataset.placed;
    });
    syncTaskbar();
    runBoot();
  });

  /* Keyboard */
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeStartMenu();
  });

  updateClock();
  setInterval(updateClock, 1000);
  runBoot();
})();
