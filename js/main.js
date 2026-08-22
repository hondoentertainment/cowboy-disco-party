(function () {
  "use strict";

  const config = window.CDP || {};
  const dateTbd = Boolean(config.PARTY_DATE_TBD || !config.PARTY_DATE);
  const PARTY_DATE = config.PARTY_DATE ? new Date(config.PARTY_DATE) : null;
  const PARTY_END = config.PARTY_END ? new Date(config.PARTY_END) : null;

  const daysEl = document.getElementById("days");
  const hoursEl = document.getElementById("hours");
  const minutesEl = document.getElementById("minutes");
  const secondsEl = document.getElementById("seconds");
  const countdownEl = document.querySelector(".countdown");
  const dateTbdEl = document.getElementById("date-tbd");
  const postPartyEl = document.getElementById("post-party");
  const heroStatus = document.getElementById("hero-status");
  const heroEyebrow = document.getElementById("hero-eyebrow");
  const heroTagline = document.getElementById("hero-tagline");
  const partyNightEl = document.getElementById("party-night");

  function pad(n) {
    return String(n).padStart(2, "0");
  }

  function applyDateTbdMode() {
    if (!dateTbd) {
      return;
    }

    document.body.classList.add("is-date-tbd");

    if (countdownEl) {
      countdownEl.classList.add("is-hidden");
    }

    if (dateTbdEl) {
      dateTbdEl.classList.remove("is-hidden");
    }
  }

  function isPostParty() {
    if (dateTbd || !PARTY_END) {
      return false;
    }
    return Date.now() >= PARTY_END.getTime();
  }

  function isPartyLive() {
    if (dateTbd || !PARTY_DATE || !PARTY_END) {
      return false;
    }
    const now = Date.now();
    return now >= PARTY_DATE.getTime() && now < PARTY_END.getTime();
  }

  function applyPostPartyMode() {
    if (!isPostParty()) {
      return;
    }

    document.body.classList.add("is-post-party");

    if (heroStatus) {
      heroStatus.textContent = "Thanks for dancing — relive the night in the gallery.";
      heroStatus.classList.remove("is-hidden");
    }

    if (countdownEl) {
      countdownEl.classList.add("is-hidden");
    }

    if (dateTbdEl) {
      dateTbdEl.classList.add("is-hidden");
    }

    if (postPartyEl) {
      postPartyEl.classList.remove("is-hidden");
    }

    if (partyNightEl) {
      partyNightEl.querySelector(".party-night__heading").textContent = "Keep the Party Going";
      partyNightEl.querySelector(".party-night__lead").textContent =
        "Upload photos, vote for best outfit, and tell us when to do it all again.";
    }
  }

  function applyLivePartyMode() {
    if (!isPartyLive()) {
      return;
    }

    document.body.classList.add("is-party-live");

    if (heroStatus) {
      heroStatus.textContent = "Party night is live — open Gallery, Vote, or Ice Breakers from the menu.";
      heroStatus.classList.remove("is-hidden");
    }

    if (countdownEl) {
      countdownEl.classList.add("is-hidden");
    }

    if (dateTbdEl) {
      dateTbdEl.classList.add("is-hidden");
    }

    if (postPartyEl) {
      postPartyEl.classList.add("is-hidden");
    }
  }

  function updateCountdown() {
    applyDateTbdMode();

    if (dateTbd) {
      return;
    }

    if (!daysEl || !hoursEl || !minutesEl || !secondsEl || !PARTY_DATE) {
      applyPostPartyMode();
      applyLivePartyMode();
      return;
    }

    if (isPostParty()) {
      applyPostPartyMode();
      return;
    }

    if (isPartyLive()) {
      applyLivePartyMode();
      return;
    }

    const diff = PARTY_DATE.getTime() - Date.now();
    if (diff <= 0) {
      daysEl.textContent = "00";
      hoursEl.textContent = "00";
      minutesEl.textContent = "00";
      secondsEl.textContent = "00";
      applyLivePartyMode();
      return;
    }

    const totalSeconds = Math.floor(diff / 1000);
    const days = Math.floor(totalSeconds / 86400);
    const hours = Math.floor((totalSeconds % 86400) / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;

    daysEl.textContent = pad(days);
    hoursEl.textContent = pad(hours);
    minutesEl.textContent = pad(minutes);
    secondsEl.textContent = pad(seconds);
  }

  const spotifyUrl = String(config.SPOTIFY_PLAYLIST_URL || "").trim();
  if (spotifyUrl) {
    document.querySelectorAll("[data-spotify]").forEach(function (link) {
      link.href = spotifyUrl;
    });
    document.querySelectorAll("[data-spotify-wrap]").forEach(function (wrap) {
      wrap.classList.remove("is-hidden");
    });
  }

  function renderLiveMoments() {
    const container = document.getElementById("live-moments");
    const grid = document.getElementById("live-moments-grid");
    if (!container || !grid || (!isPostParty() && !isPartyLive())) {
      return;
    }

    fetch("/api/photos")
      .then(function (response) {
        if (!response.ok) {
          throw new Error("gallery unavailable");
        }
        return response.json();
      })
      .then(function (data) {
        const photos = (data.photos || [])
          .filter(function (photo) {
            return photo && photo.url && !(photo.type || "").startsWith("video");
          })
          .slice(0, 6);

        if (photos.length === 0) {
          return;
        }

        photos.forEach(function (photo) {
          const link = document.createElement("a");
          link.href = "gallery.html";
          link.className = "live-moments__item";
          const img = document.createElement("img");
          img.src = photo.url;
          img.alt = photo.caption || "Party photo";
          img.loading = "lazy";
          img.decoding = "async";
          link.appendChild(img);
          grid.appendChild(link);
        });
        container.classList.remove("is-hidden");
      })
      .catch(function () {
        /* gallery strip is a progressive enhancement */
      });
  }

  renderLiveMoments();

  const partifulUrl = String(config.PARTIFUL_URL || "").trim();
  if (partifulUrl) {
    document.querySelectorAll("[data-partiful]").forEach(function (link) {
      link.href = partifulUrl;
      link.classList.remove("is-hidden");
    });

    document.querySelectorAll("[data-partiful-nav]").forEach(function (link) {
      link.href = partifulUrl;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
    });
  }

  /* --- One-tap share ------------------------------------------------------
     Uses the native share sheet where available (that is the "one tap" on
     phones) and falls back to clipboard on desktop. */

  var shareButtons = document.querySelectorAll("[data-share]");
  if (shareButtons.length) {
    var shareText = String(config.SHARE_MESSAGE || "You're invited to Cowboy Disco.");
    var shareUrl = String(config.SITE_URL || window.location.origin);
    var partifulShare = String(config.PARTIFUL_URL || "").trim();
    if (partifulShare) {
      shareText += " RSVP: " + partifulShare;
    }

    shareButtons.forEach(function (btn) {
      var original = btn.textContent;
      var resetTimer;

      btn.addEventListener("click", function () {
        function flash(msg) {
          btn.textContent = msg;
          window.clearTimeout(resetTimer);
          resetTimer = window.setTimeout(function () {
            btn.textContent = original;
          }, 2200);
        }

        if (navigator.share) {
          navigator
            .share({ title: "Cowboy Disco Party", text: shareText, url: shareUrl })
            .catch(function () {
              /* user dismissed the sheet */
            });
          return;
        }

        if (navigator.clipboard && navigator.clipboard.writeText) {
          navigator.clipboard.writeText(shareText + " " + shareUrl).then(
            function () {
              flash("Invite copied");
            },
            function () {
              flash("Copy failed");
            }
          );
          return;
        }

        flash("Copy the link from your browser bar");
      });
    });
  }

  /* --- Ambient audio ------------------------------------------------------
     Opt-in only: nothing plays until the guest asks for it, and the choice
     persists. Hidden entirely unless AMBIENT_AUDIO_URL is configured. */

  var audioUrl = String(config.AMBIENT_AUDIO_URL || "").trim();
  var audioToggle = document.getElementById("ambient-toggle");
  if (audioUrl && audioToggle) {
    var STORE_KEY = "cdp-ambient";
    var audio = new Audio(audioUrl);
    audio.loop = true;
    audio.preload = "none";
    audio.volume = 0.35;

    function setPlaying(on) {
      audioToggle.setAttribute("aria-pressed", String(on));
      audioToggle.dataset.playing = on ? "true" : "false";
      audioToggle.setAttribute("aria-label", on ? "Mute party music" : "Play party music");
      audioToggle.title = on ? "Mute party music" : "Play party music";
    }

    audioToggle.classList.remove("is-hidden");
    setPlaying(false);

    audioToggle.addEventListener("click", function () {
      if (audio.paused) {
        audio.play().then(
          function () {
            setPlaying(true);
            try { localStorage.setItem(STORE_KEY, "on"); } catch (e) {}
          },
          function () {
            setPlaying(false);
          }
        );
      } else {
        audio.pause();
        setPlaying(false);
        try { localStorage.setItem(STORE_KEY, "off"); } catch (e) {}
      }
    });

    // Browsers block autoplay without a gesture, so a remembered "on" only
    // resumes after the guest next interacts with the page.
    var wanted = null;
    try { wanted = localStorage.getItem(STORE_KEY); } catch (e) {}
    if (wanted === "on") {
      var resume = function () {
        audio.play().then(function () { setPlaying(true); }, function () {});
        document.removeEventListener("pointerdown", resume);
        document.removeEventListener("keydown", resume);
      };
      document.addEventListener("pointerdown", resume, { once: true });
      document.addEventListener("keydown", resume, { once: true });
    }
  }

  updateCountdown();
  setInterval(updateCountdown, 1000);
  applyPostPartyMode();
  applyLivePartyMode();

  var lookbookGrid = document.querySelector(".lookbook__grid");
  var lookbookStatus = document.getElementById("lookbook-status");
  if (lookbookGrid && lookbookStatus) {
    var lookCards = lookbookGrid.querySelectorAll(".look-card");

    function updateLookbookStatus() {
      if (!lookCards.length) {
        return;
      }

      var nearest = 0;
      var best = Infinity;
      var left = lookbookGrid.scrollLeft;
      lookCards.forEach(function (card, index) {
        var distance = Math.abs(card.offsetLeft - left);
        if (distance < best) {
          best = distance;
          nearest = index;
        }
      });

      var n = nearest + 1;
      lookbookStatus.textContent = "Look " + n + " of " + lookCards.length + " — swipe for more";
    }

    lookbookGrid.addEventListener("scroll", updateLookbookStatus, { passive: true });
    lookbookGrid.addEventListener("keydown", function (event) {
      if (event.key !== "ArrowRight" && event.key !== "ArrowLeft") {
        return;
      }

      var card = lookCards[0];
      if (!card) {
        return;
      }

      var step = card.getBoundingClientRect().width + 12;
      lookbookGrid.scrollBy({
        left: event.key === "ArrowRight" ? step : -step,
        behavior: "smooth",
      });
      event.preventDefault();
    });
    updateLookbookStatus();
  }

})();
