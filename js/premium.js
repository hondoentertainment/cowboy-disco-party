(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  function revealAll() {
    document.querySelectorAll(".reveal, .reveal-stagger").forEach(function (el) {
      el.classList.add("is-visible");
    });
  }

  if (reduceMotion.matches) {
    revealAll();
    return;
  }

  /* --- Scroll reveals ---------------------------------------------------- */

  var revealEls = document.querySelectorAll(".reveal, .reveal-stagger");

  if (revealEls.length && "IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) {
            return;
          }
          // Sections entering together rise in sequence rather than as a slab.
          var order = Number(entry.target.dataset.revealOrder || 0);
          entry.target.style.setProperty("--reveal-delay", order * 0.07 + "s");
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        });
      },
      { threshold: 0.1, rootMargin: "0px 0px -60px 0px" }
    );

    var seen = 0;
    revealEls.forEach(function (el) {
      // Anything already on screen at load should not animate in late.
      var box = el.getBoundingClientRect();
      if (box.top < window.innerHeight && box.bottom > 0) {
        el.dataset.revealOrder = String(seen++);
      }
      observer.observe(el);
    });
  } else {
    revealAll();
  }

  /* --- Hero rhinestones -------------------------------------------------- */

  var field = document.querySelector("[data-rhinestones]");
  if (field) {
    // Deterministic placement — a fixed sequence keeps the look consistent
    // between loads and avoids clustering.
    var stones = [
      [8, 22, 3, 6.5, 0.9], [17, 68, 2, 4.5, 0.7], [24, 14, 4, 8, 0.85],
      [31, 47, 2, 5, 0.6], [39, 78, 3, 6, 0.8], [46, 9, 2, 4.5, 0.7],
      [53, 62, 4, 8, 0.9], [61, 31, 2, 5, 0.65], [68, 74, 3, 6.5, 0.8],
      [74, 18, 2, 4.5, 0.7], [81, 55, 4, 7.5, 0.85], [88, 27, 2, 5, 0.6],
      [93, 70, 3, 6, 0.75], [12, 88, 2, 4.5, 0.6], [57, 88, 3, 6, 0.7],
      [35, 92, 2, 4.5, 0.55], [78, 92, 3, 5.5, 0.65], [4, 52, 2, 4.5, 0.6]
    ];

    var frag = document.createDocumentFragment();
    stones.forEach(function (s, i) {
      var el = document.createElement("span");
      el.className = "rhinestone";
      el.style.left = s[0] + "%";
      el.style.top = s[1] + "%";
      el.style.setProperty("--r-size", s[2] + "px");
      el.style.setProperty("--r-glow", s[3] + "px");
      el.style.setProperty("--r-peak", String(s[4]));
      el.style.setProperty("--r-dur", (4.5 + (i % 5) * 0.9).toFixed(1) + "s");
      el.style.setProperty("--r-delay", ((i * 0.53) % 6).toFixed(2) + "s");
      frag.appendChild(el);
    });
    field.appendChild(frag);
  }

  /* --- Hero parallax ------------------------------------------------------
     Applied to the wrapper, not the image: the image carries the ken-burns
     animation, and an inline transform on it would override that entirely. */

  var heroVisual = document.querySelector(".hero__visual");
  var hero = document.querySelector(".hero--premium");
  if (heroVisual && hero) {
    var ticking = false;

    var onScroll = function () {
      if (ticking) {
        return;
      }
      ticking = true;
      window.requestAnimationFrame(function () {
        var y = window.scrollY;
        if (y < hero.offsetHeight) {
          heroVisual.style.transform = "translate3d(0," + y * 0.22 + "px,0)";
          heroVisual.style.opacity = String(Math.max(0, 1 - y / (hero.offsetHeight * 1.15)));
        }
        ticking = false;
      });
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* --- Failsafe ----------------------------------------------------------
     If an error above ever prevents the observer from running, content must
     not be left sitting at opacity 0. Reveal anything still hidden. */

  window.setTimeout(function () {
    document.querySelectorAll(".reveal, .reveal-stagger").forEach(function (el) {
      if (!el.classList.contains("is-visible")) {
        var box = el.getBoundingClientRect();
        if (box.top < window.innerHeight * 1.5) {
          el.classList.add("is-visible");
        }
      }
    });
  }, 2500);

  /* --- Turn everything off if the user flips reduced-motion on ----------- */

  var onPreferenceChange = function (event) {
    if (event.matches) {
      revealAll();
      if (heroVisual) {
        heroVisual.style.transform = "";
        heroVisual.style.opacity = "";
      }
      if (field) {
        field.innerHTML = "";
      }
    }
  };

  if (typeof reduceMotion.addEventListener === "function") {
    reduceMotion.addEventListener("change", onPreferenceChange);
  } else if (typeof reduceMotion.addListener === "function") {
    reduceMotion.addListener(onPreferenceChange);
  }
})();
