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
      heroStatus.textContent = "Party night is live — scan the QR for photos, ice breakers, and votes.";
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

    const rsvpDirections = document.getElementById("rsvp-directions");
    if (rsvpDirections) {
      rsvpDirections.textContent = "Directions";
      rsvpDirections.classList.remove("btn--rsvp");
      rsvpDirections.classList.add("btn--ghost");
    }
  }

  updateCountdown();
  setInterval(updateCountdown, 1000);
  applyPostPartyMode();
  applyLivePartyMode();

})();
