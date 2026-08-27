/* BoatOS study soundtrack — "Ocean Graph Theme" */
(function () {
  "use strict";

  const TRACK = {
    src: "audio/ocean_graph_theme.mp3",
    title: "Ocean Graph Theme",
    subtitle: "BoatOS · research story score",
  };

  let audio = null;
  let playing = false;

  function resolveSrc() {
    const depth = (location.pathname.match(/\/(th|ja)(\/|$)/) || [])[1] ? "../" : "";
    return depth + TRACK.src;
  }

  function ensureAudio() {
    if (audio) return audio;
    audio = new Audio(resolveSrc());
    audio.loop = true;
    audio.preload = "metadata";
    audio.volume = 0.55;
    audio.addEventListener("timeupdate", syncBars);
    audio.addEventListener("ended", () => setPlaying(false));
    return audio;
  }

  function setPlaying(on) {
    playing = on;
    document.querySelectorAll("[data-song-play]").forEach((btn) => {
      btn.textContent = on ? "⏸ Pause Theme" : "▶ Play Theme";
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    const label = document.getElementById("media-track");
    if (label) label.textContent = on ? TRACK.title + " ▸ playing" : TRACK.title;
    const dock = document.getElementById("song-dock-status");
    if (dock) dock.textContent = on ? "Now playing · Ocean Graph Theme" : "Theme ready";
  }

  function syncBars() {
    if (!audio || !audio.duration) return;
    const pct = Math.min(100, (audio.currentTime / audio.duration) * 100);
    const bar = document.getElementById("media-bar");
    if (bar) bar.style.width = pct + "%";
    const dockBar = document.getElementById("song-dock-bar");
    if (dockBar) dockBar.style.width = pct + "%";
  }

  async function play() {
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
    syncBars();
  }

  window.BoatOSSong = { play, pause, toggle, stop, TRACK };

  document.addEventListener("DOMContentLoaded", () => {
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

    /* Hook classic media dialog buttons if present */
    const mediaPlay = document.getElementById("media-play");
    const mediaStop = document.getElementById("media-stop");
    const mediaNext = document.getElementById("media-next");
    const mediaLabel = document.getElementById("media-track");
    if (mediaLabel) mediaLabel.textContent = TRACK.title;
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
        syncBars();
      }, true);
    }
  });
})();
