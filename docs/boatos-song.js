/* BoatOS R&B single — "Graph of My Heart" */
(function () {
  "use strict";

  const TRACK = {
    src: "audio/graph_of_my_heart.mp3",
    lyricsSrc: "audio/graph_of_my_heart_lyrics.json",
    title: "Soft Tide",
    subtitle: "HYBS-inspired · soft R&B",
    artist: "Boat · BoatOS",
  };

  let audio = null;
  let playing = false;
  let lyrics = null;
  let lyricIdx = -1;

  function prefix() {
    return /\/(th|ja)(\/|$)/.test(location.pathname) ? "../" : "";
  }

  function ensureAudio() {
    if (audio) return audio;
    audio = new Audio(prefix() + TRACK.src);
    audio.loop = false;
    audio.preload = "metadata";
    audio.volume = 0.7;
    audio.addEventListener("timeupdate", onTime);
    audio.addEventListener("ended", () => {
      setPlaying(false);
      lyricIdx = -1;
      renderLyric("— end —");
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
      btn.textContent = on ? "⏸ Pause" : "▶ Play Song";
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    const label = document.getElementById("media-track");
    if (label) label.textContent = on ? TRACK.title + " ▸ playing" : TRACK.title + " — " + TRACK.artist;
    const dock = document.getElementById("song-dock-status");
    if (dock) dock.textContent = on ? "Now playing · Soft Tide" : "Soft Tide · soft R&B";
  }

  async function play() {
    await loadLyrics();
    const a = ensureAudio();
    try {
      await a.play();
      setPlaying(true);
    } catch (err) {
      setPlaying(false);
      console.warn("Audio play blocked until user gesture", err);
    }
  }

  function pause() {
    if (!audio) return;
    audio.pause();
    setPlaying(false);
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
  }

  window.BoatOSSong = { play, pause, toggle, stop, TRACK };

  document.addEventListener("DOMContentLoaded", () => {
    loadLyrics().then((data) => {
      const meta = document.getElementById("song-lyrics-meta");
      if (meta && data) {
        meta.textContent = (data.title || TRACK.title) + " · " + (data.genre || "R&B") + " · " + (data.bpm || 74) + " BPM";
      }
      renderLyric("Press play for lyrics", "");
    });

    document.querySelectorAll("[data-song-play]").forEach((btn) => {
      btn.addEventListener("click", (e) => {
        e.preventDefault();
        toggle();
      });
    });
    document.querySelectorAll("[data-song-stop]").forEach((btn) => {
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
    if (mediaPlay) {
      mediaPlay.addEventListener("click", (e) => {
        e.stopImmediatePropagation();
        toggle();
      }, true);
    }
    if (mediaStop) {
      mediaStop.addEventListener("click", (e) => {
        e.stopImmediatePropagation();
        stop();
      }, true);
    }
    if (mediaNext) {
      mediaNext.addEventListener("click", (e) => {
        e.stopImmediatePropagation();
        if (audio) audio.currentTime = Math.min(audio.duration || 0, audio.currentTime + 12);
        onTime();
      }, true);
    }
  });
})();
