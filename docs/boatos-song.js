/* BoatOS R&B single — Soft Tide (persists across pages via sessionStorage) */
(function () {
  "use strict";

  const TRACK = {
    src: "audio/soft_tide.mp3",
    lyricsSrc: "audio/soft_tide_lyrics.json",
    title: "Soft Tide",
    subtitle: "soft R&B",
    artist: "Boat · BoatOS",
  };
  const STORE_KEY = "boatos-song-v1";
  const UNLOCK_KEY = "boatos-audio-unlocked";

  let audio = null;
  let playing = false;
  let lyrics = null;
  let lyricIdx = -1;
  let saveTimer = null;

  function prefix() {
    return /\/(th|ja)(\/|$)/.test(location.pathname) ? "../" : "";
  }

  function loadState() {
    try {
      return JSON.parse(sessionStorage.getItem(STORE_KEY) || "null") || {};
    } catch (_) {
      return {};
    }
  }

  function saveState() {
    if (!audio) return;
    try {
      sessionStorage.setItem(
        STORE_KEY,
        JSON.stringify({
          t: audio.currentTime || 0,
          playing: !audio.paused,
          vol: audio.volume,
        })
      );
    } catch (_) {}
  }

  function ensureAudio() {
    if (audio) return audio;
    audio = new Audio(prefix() + TRACK.src);
    audio.loop = true;
    audio.preload = "auto";
    audio.volume = 0.65;
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("play", () => {
      setPlaying(true);
      saveState();
    });
    audio.addEventListener("pause", () => {
      setPlaying(false);
      saveState();
    });
    return audio;
  }

  async function loadLyrics() {
    if (lyrics) return lyrics;
    try {
      const res = await fetch(prefix() + TRACK.lyricsSrc);
      lyrics = await res.json();
    } catch (e) {
      lyrics = { lines: [] };
    }
    return lyrics;
  }

  function renderLyric(text, section) {
    const el = document.getElementById("song-lyrics-line");
    const sec = document.getElementById("song-lyrics-section");
    if (el) el.textContent = text || "…";
    if (sec) sec.textContent = section ? "[" + section + "]" : "";
    const dock = document.getElementById("song-dock-lyric");
    if (dock) dock.textContent = text || TRACK.subtitle;
  }

  function onTime() {
    syncBars();
    if (!lyrics || !lyrics.lines || !audio) return;
    const t = audio.currentTime;
    let i = 0;
    for (let n = 0; n < lyrics.lines.length; n++) {
      if (lyrics.lines[n].t <= t) i = n;
      else break;
    }
    if (i !== lyricIdx) {
      lyricIdx = i;
      const line = lyrics.lines[i];
      renderLyric(line.text, line.section);
    }
  }

  function syncBars() {
    if (!audio || !audio.duration) return;
    const pct = Math.min(100, (audio.currentTime / audio.duration) * 100);
    const bar = document.getElementById("media-bar");
    if (bar) bar.style.width = pct + "%";
    const dockBar = document.getElementById("song-dock-bar");
    if (dockBar) dockBar.style.width = pct + "%";
  }

  function setPlaying(on) {
    playing = on;
    document.querySelectorAll("[data-song-play]").forEach((btn) => {
      btn.textContent = on ? "⏸ Pause" : "▶ Play";
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    const label = document.getElementById("media-track");
    if (label) label.textContent = on ? TRACK.title + " ▸ looping" : TRACK.title + " — " + TRACK.artist;
    const dock = document.getElementById("song-dock-status");
    if (dock) dock.textContent = on ? "Playing · loop on" : "Ready · Soft Tide";
  }

  async function play() {
    await loadLyrics();
    const a = ensureAudio();
    a.loop = true;
    try {
      await a.play();
      sessionStorage.setItem(UNLOCK_KEY, "1");
      setPlaying(true);
      saveState();
      return true;
    } catch (err) {
      setPlaying(false);
      return false;
    }
  }

  function pause() {
    if (!audio) return;
    audio.pause();
    setPlaying(false);
    saveState();
  }

  function toggle() {
    if (playing) pause();
    else play();
  }

  function stop() {
    if (!audio) return;
    audio.pause();
    audio.currentTime = 0;
    setPlaying(false);
    lyricIdx = -1;
    renderLyric("Press play for lyrics", "");
    syncBars();
    saveState();
  }

  function bindUnlock() {
    const unlock = () => {
      sessionStorage.setItem(UNLOCK_KEY, "1");
      play();
      document.removeEventListener("pointerdown", unlock, true);
      document.removeEventListener("keydown", unlock, true);
    };
    document.addEventListener("pointerdown", unlock, true);
    document.addEventListener("keydown", unlock, true);
  }

  /** Resume from session or start fresh; keep playing across page loads. */
  async function resumeOrStart() {
    await loadLyrics();
    const a = ensureAudio();
    const state = loadState();
    if (typeof state.t === "number" && state.t > 0) {
      try {
        a.currentTime = state.t;
      } catch (_) {}
    }
    if (typeof state.vol === "number") a.volume = state.vol;

    const wantPlay = state.playing !== false; // default: play
    if (!wantPlay) {
      setPlaying(false);
      renderLyric("Paused — press play", "");
      return;
    }

    const ok = await play();
    if (!ok) {
      const dock = document.getElementById("song-dock-status");
      if (dock) dock.textContent = "Tap anywhere to start music";
      renderLyric("Tap anywhere to start Soft Tide", "");
      bindUnlock();
    }
  }

  window.BoatOSSong = {
    play,
    pause,
    toggle,
    stop,
    resumeOrStart,
    autoplayLoop: resumeOrStart,
    saveState,
    TRACK,
  };

  function wireUi() {
    document.querySelectorAll("[data-song-play]").forEach((btn) => {
      if (btn.dataset.songWired) return;
      btn.dataset.songWired = "1";
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        toggle();
      });
    });
    document.querySelectorAll("[data-song-stop]").forEach((btn) => {
      if (btn.dataset.songWired) return;
      btn.dataset.songWired = "1";
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        stop();
      });
    });

    const mediaPlay = document.getElementById("media-play");
    const mediaStop = document.getElementById("media-stop");
    const mediaNext = document.getElementById("media-next");
    const mediaLabel = document.getElementById("media-track");
    if (mediaLabel) mediaLabel.textContent = TRACK.title + " — " + TRACK.artist;
    if (mediaPlay && !mediaPlay.dataset.songWired) {
      mediaPlay.dataset.songWired = "1";
      mediaPlay.addEventListener(
        "click",
        (e) => {
          e.stopImmediatePropagation();
          toggle();
        },
        true
      );
    }
    if (mediaStop && !mediaStop.dataset.songWired) {
      mediaStop.dataset.songWired = "1";
      mediaStop.addEventListener(
        "click",
        (e) => {
          e.stopImmediatePropagation();
          stop();
        },
        true
      );
    }
    if (mediaNext && !mediaNext.dataset.songWired) {
      mediaNext.dataset.songWired = "1";
      mediaNext.addEventListener(
        "click",
        (e) => {
          e.stopImmediatePropagation();
          if (audio) audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 12);
          onTime();
        },
        true
      );
    }
  }

  function boot() {
    wireUi();
    loadLyrics().then((data) => {
      const meta = document.getElementById("song-lyrics-meta");
      if (meta && data) meta.textContent = (data.title || TRACK.title) + " — " + TRACK.artist;
    });
    // Start / resume ASAP (before boot overlay finishes when possible)
    resumeOrStart();
    if (!saveTimer) saveTimer = setInterval(saveState, 500);
    window.addEventListener("pagehide", saveState);
    window.addEventListener("beforeunload", saveState);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
