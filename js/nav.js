(function () {
  "use strict";

  var toggle = document.querySelector(".nav__toggle");
  var menu = document.getElementById("nav-menu");

  function closeMenu() {
    if (!toggle || !menu) {
      return;
    }

    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open menu");
    menu.classList.remove("is-open");
    document.body.classList.remove("is-nav-open");
    menu.querySelectorAll(".nav__drop[open]").forEach(function (detail) {
      detail.removeAttribute("open");
    });
  }

  function openMenu() {
    if (!toggle || !menu) {
      return;
    }

    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Close menu");
    menu.classList.add("is-open");
    document.body.classList.add("is-nav-open");
  }

  if (toggle && menu) {
    toggle.addEventListener("click", function () {
      var open = toggle.getAttribute("aria-expanded") === "true";
      if (open) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    menu.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", closeMenu);
    });

    menu.querySelectorAll(".nav__drop").forEach(function (detail) {
      detail.addEventListener("toggle", function () {
        if (!detail.open) {
          return;
        }

        menu.querySelectorAll(".nav__drop").forEach(function (other) {
          if (other !== detail) {
            other.removeAttribute("open");
          }
        });
      });
    });

    document.addEventListener("click", function (event) {
      if (menu.contains(event.target) || toggle.contains(event.target)) {
        return;
      }

      closeMenu();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeMenu();
      }
    });
  }

  function currentPage() {
    var path = window.location.pathname.replace(/\/+$/, "");
    var file = path.split("/").pop() || "index.html";
    if (file === "" || file === "index.html" || file === "index") {
      return "index.html";
    }
    return file;
  }

  function injectGuestChrome() {
    if (!document.querySelector(".nav") || document.querySelector(".guest-dock")) {
      return;
    }

    var page = currentPage();
    var homeHref = page === "index.html" ? "#top" : "index.html";
    var mapHref = page === "index.html" ? "#location" : "index.html#location";

    var dock = document.createElement("nav");
    dock.className = "guest-dock";
    dock.setAttribute("aria-label", "Party shortcuts");
    dock.innerHTML =
      '<a class="guest-dock__item" data-dock="index.html" href="' + homeHref + '">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 11.2 12 4l8 7.2V20a1 1 0 0 1-1 1h-5.2v-6.2H10.2V21H5a1 1 0 0 1-1-1z"/></svg>' +
        "<span>Home</span>" +
      "</a>" +
      '<a class="guest-dock__item" data-dock="gallery.html" href="gallery.html">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7.5 5.5 8.7 3.7a1.5 1.5 0 0 1 1.25-.7h4.1a1.5 1.5 0 0 1 1.25.7l1.2 1.8H20a1.5 1.5 0 0 1 1.5 1.5v12A1.5 1.5 0 0 1 20 20.5H4A1.5 1.5 0 0 1 2.5 19V7A1.5 1.5 0 0 1 4 5.5h3.5z"/><circle cx="12" cy="12.5" r="3.75"/></svg>' +
        "<span>Gallery</span>" +
      "</a>" +
      '<a class="guest-dock__item" data-dock="vote.html" href="vote.html">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 7.5 7.75 11 12 5l4.25 6 4.25-3.5-1.5 10.5a1.5 1.5 0 0 1-1.49 1.3H6.49A1.5 1.5 0 0 1 5 18z"/></svg>' +
        "<span>Vote</span>" +
      "</a>" +
      '<a class="guest-dock__item" data-dock="ice-breaker.html" href="ice-breaker.html">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 11.5a8.5 8.5 0 0 1-12.4 7.55L3 20.5l1.45-5.6A8.5 8.5 0 1 1 21 11.5z"/><path d="M8.5 10.25h7M8.5 13.25h4.5"/></svg>' +
        "<span>Ice</span>" +
      "</a>" +
      '<a class="guest-dock__item" data-dock="location" href="' + mapHref + '">' +
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6.2 7-11.2A7 7 0 0 0 5 9.8C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.8" r="2.4"/></svg>' +
        "<span>Map</span>" +
      "</a>";

    dock.querySelectorAll("[data-dock]").forEach(function (item) {
      if (item.getAttribute("data-dock") === page) {
        item.setAttribute("aria-current", "page");
      }
    });

    document.body.appendChild(dock);
    document.body.classList.add("has-guest-dock");

    if (!document.getElementById("top")) {
      document.body.id = "top";
    }

    var topLink = document.createElement("a");
    topLink.className = "back-to-top";
    topLink.href = "#top";
    topLink.textContent = "Back to top";
    document.body.appendChild(topLink);

    function updateTopLink() {
      var show = window.scrollY > 480;
      topLink.classList.toggle("is-visible", show);
    }

    window.addEventListener("scroll", updateTopLink, { passive: true });
    updateTopLink();
  }

  injectGuestChrome();
})();
