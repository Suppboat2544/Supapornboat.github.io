/* BoatOS playable Win95 apps: Minesweeper, Paint, Calculator, Notepad, Media, Cards */
(function () {
  "use strict";

  document.addEventListener("click", (e) => {
    const el = e.target.closest("[data-open-dialog]");
    if (!el) return;
    const id = el.getAttribute("data-open-dialog");
    setTimeout(() => {
      if (id === "dlg-mines") initMines(true);
      if (id === "dlg-paint") initPaint();
      if (id === "dlg-cards") initCards(true);
    }, 10);
  });

  /* ——— Minesweeper 8x8 ——— */
  let mineReady = false;
  function initMines(reset) {
    const grid = document.getElementById("mine-grid");
    const face = document.getElementById("mine-face");
    const flagsEl = document.getElementById("mine-flags");
    if (!grid) return;
    if (!reset && mineReady && document.getElementById("mine-grid")?.children.length) return;

    const W = 8, H = 8, MINES = 10;
    const cells = [];
    let mines = new Set();
    while (mines.size < MINES) {
      mines.add(Math.floor(Math.random() * W * H));
    }
    let flags = MINES;
    let opened = 0;
    let dead = false;
    let won = false;

    grid.innerHTML = "";
    grid.style.gridTemplateColumns = `repeat(${W}, 22px)`;
    face.textContent = "🙂";
    flagsEl.textContent = String(flags).padStart(3, "0");

    for (let i = 0; i < W * H; i++) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "mine-cell";
      btn.dataset.i = String(i);
      grid.appendChild(btn);
      cells.push({ btn, open: false, flag: false, mine: mines.has(i) });
    }

    function neighbors(i) {
      const x = i % W, y = (i / W) | 0;
      const out = [];
      for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
        if (!dx && !dy) continue;
        const nx = x + dx, ny = y + dy;
        if (nx >= 0 && nx < W && ny >= 0 && ny < H) out.push(ny * W + nx);
      }
      return out;
    }

    function count(i) {
      return neighbors(i).filter((j) => cells[j].mine).length;
    }

    function reveal(i) {
      const c = cells[i];
      if (c.open || c.flag || dead || won) return;
      c.open = true;
      opened++;
      c.btn.classList.add("is-open");
      if (c.mine) {
        c.btn.textContent = "💣";
        c.btn.classList.add("is-mine");
        dead = true;
        face.textContent = "😵";
        cells.forEach((x, idx) => {
          if (x.mine) {
            x.btn.textContent = "💣";
            x.btn.classList.add("is-open", "is-mine");
          }
        });
        return;
      }
      const n = count(i);
      c.btn.textContent = n ? String(n) : "";
      if (n) c.btn.dataset.n = String(n);
      else neighbors(i).forEach(reveal);
      if (opened === W * H - MINES) {
        won = true;
        face.textContent = "😎";
      }
    }

    cells.forEach((c, i) => {
      c.btn.addEventListener("click", () => reveal(i));
      c.btn.addEventListener("contextmenu", (e) => {
        e.preventDefault();
        if (c.open || dead || won) return;
        c.flag = !c.flag;
        c.btn.textContent = c.flag ? "🚩" : "";
        c.btn.classList.toggle("is-flag", c.flag);
        flags += c.flag ? -1 : 1;
        flagsEl.textContent = String(Math.max(0, flags)).padStart(3, "0");
      });
    });

    face.onclick = () => initMines(true);
    mineReady = true;
  }

  document.getElementById("mine-new")?.addEventListener("click", () => initMines(true));

  /* ——— Paint ——— */
  let paintReady = false;
  function initPaint() {
    const canvas = document.getElementById("paint-canvas");
    if (!canvas || paintReady) return;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    let drawing = false;
    let color = "#000080";
    let size = 3;

    const pos = (e) => {
      const r = canvas.getBoundingClientRect();
      const x = (("touches" in e ? e.touches[0].clientX : e.clientX) - r.left) * (canvas.width / r.width);
      const y = (("touches" in e ? e.touches[0].clientY : e.clientY) - r.top) * (canvas.height / r.height);
      return { x, y };
    };

    const start = (e) => {
      drawing = true;
      const p = pos(e);
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      e.preventDefault();
    };
    const move = (e) => {
      if (!drawing) return;
      const p = pos(e);
      ctx.strokeStyle = color;
      ctx.lineWidth = size;
      ctx.lineCap = "round";
      ctx.lineTo(p.x, p.y);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      e.preventDefault();
    };
    const end = () => { drawing = false; ctx.beginPath(); };

    canvas.addEventListener("mousedown", start);
    canvas.addEventListener("mousemove", move);
    window.addEventListener("mouseup", end);
    canvas.addEventListener("touchstart", start, { passive: false });
    canvas.addEventListener("touchmove", move, { passive: false });
    canvas.addEventListener("touchend", end);

    document.querySelectorAll("[data-paint-color]").forEach((btn) => {
      btn.addEventListener("click", () => {
        color = btn.getAttribute("data-paint-color");
        document.querySelectorAll("[data-paint-color]").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
      });
    });
    document.getElementById("paint-clear")?.addEventListener("click", () => {
      ctx.fillStyle = "#fff";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    });
    document.getElementById("paint-size")?.addEventListener("input", (e) => {
      size = Number(e.target.value) || 3;
    });
    paintReady = true;
  }

  /* ——— Calculator ——— */
  (function () {
    const display = document.getElementById("calc-display");
    if (!display) return;
    let cur = "0";
    let prev = null;
    let op = null;
    let reset = false;

    const render = () => { display.textContent = cur; };
    const input = (d) => {
      if (reset) { cur = "0"; reset = false; }
      if (d === "." && cur.includes(".")) return;
      cur = cur === "0" && d !== "." ? d : cur + d;
      render();
    };
    const apply = () => {
      if (prev === null || op === null) return;
      const a = parseFloat(prev), b = parseFloat(cur);
      let r = b;
      if (op === "+") r = a + b;
      if (op === "-") r = a - b;
      if (op === "*") r = a * b;
      if (op === "/") r = b === 0 ? "Error" : a / b;
      cur = String(r).slice(0, 12);
      prev = null;
      op = null;
      reset = true;
      render();
    };

    document.querySelectorAll("[data-calc]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const v = btn.getAttribute("data-calc");
        if (v === "C") { cur = "0"; prev = null; op = null; render(); return; }
        if (v === "=") { apply(); return; }
        if ("+-*/".includes(v)) {
          if (prev !== null) apply();
          prev = cur;
          op = v;
          reset = true;
          return;
        }
        input(v);
      });
    });
  })();

  /* ——— Media player (delegated to boatos-song.js when present) ——— */
  (function () {
    if (window.BoatOSSong || document.querySelector("[data-song-play]")) return;
    const play = document.getElementById("media-play");
    const bar = document.getElementById("media-bar");
    const label = document.getElementById("media-track");
    if (!play || !bar) return;
    let playing = false;
    let t = 0;
    let timer = null;
    const tracks = [
      "research_theme.mid",
      "gnn_groove.wav",
      "ocean_dom.mp3",
      "hpc_fanfare.mid",
    ];
    let ti = 0;
    const tick = () => {
      t = (t + 1) % 100;
      bar.style.width = t + "%";
      if (t === 0) {
        ti = (ti + 1) % tracks.length;
        if (label) label.textContent = tracks[ti];
      }
    };
    play.addEventListener("click", () => {
      playing = !playing;
      play.textContent = playing ? "⏸ Pause" : "▶ Play";
      if (playing) timer = setInterval(tick, 120);
      else clearInterval(timer);
    });
    document.getElementById("media-stop")?.addEventListener("click", () => {
      playing = false;
      play.textContent = "▶ Play";
      clearInterval(timer);
      t = 0;
      bar.style.width = "0%";
    });
    document.getElementById("media-next")?.addEventListener("click", () => {
      ti = (ti + 1) % tracks.length;
      if (label) label.textContent = tracks[ti];
      t = 0;
      bar.style.width = "0%";
    });
  })();

  /* ——— Solitaire-lite: match pairs ——— */
  function initCards(reset) {
    const board = document.getElementById("cards-board");
    const status = document.getElementById("cards-status");
    if (!board) return;
    if (!reset && board.dataset.ready) return;

    const icons = ["⚗️", "🧬", "🌊", "💻", "📊", "🧪", "🔬", "🧠"];
    const deck = [...icons, ...icons].sort(() => Math.random() - 0.5);
    let first = null;
    let lock = false;
    let matches = 0;
    board.innerHTML = "";
    board.dataset.ready = "1";
    if (status) status.textContent = "Match the pairs";

    deck.forEach((icon, idx) => {
      const card = document.createElement("button");
      card.type = "button";
      card.className = "card-tile";
      card.innerHTML = `<span class="card-back">🂠</span><span class="card-front">${icon}</span>`;
      card.addEventListener("click", () => {
        if (lock || card.classList.contains("is-flipped") || card.classList.contains("is-matched")) return;
        card.classList.add("is-flipped");
        if (!first) { first = card; return; }
        lock = true;
        if (first.querySelector(".card-front").textContent === icon) {
          first.classList.add("is-matched");
          card.classList.add("is-matched");
          matches++;
          first = null;
          lock = false;
          if (status) status.textContent = matches === icons.length ? "You win! 🎉" : `Matches: ${matches}/${icons.length}`;
        } else {
          const a = first, b = card;
          setTimeout(() => {
            a.classList.remove("is-flipped");
            b.classList.remove("is-flipped");
            first = null;
            lock = false;
          }, 550);
        }
      });
      board.appendChild(card);
    });
  }

  document.getElementById("cards-new")?.addEventListener("click", () => {
    const board = document.getElementById("cards-board");
    if (board) delete board.dataset.ready;
    initCards(true);
  });
})();
