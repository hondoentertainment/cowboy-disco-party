(function (global) {
  "use strict";

  var QR_OPTIONS = {
    width: 200,
    margin: 1,
    color: { dark: "#3d0a2e", light: "#f5e6f0" },
  };

  function getSiteUrl() {
    return global.CDP && global.CDP.SITE_URL
      ? global.CDP.SITE_URL
      : "https://cowboy-disco-party.vercel.app";
  }

  function displayUrl(url) {
    return url.replace(/^https?:\/\//, "");
  }

  function loadQrLibrary(callback) {
    if (global.QRCode) {
      callback();
      return;
    }

    var existing = document.querySelector('script[data-qr-lib="true"]');
    if (existing) {
      existing.addEventListener("load", callback);
      return;
    }

    var script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/npm/qrcode@1.5.4/build/qrcode.min.js";
    script.setAttribute("data-qr-lib", "true");
    script.onload = callback;
    script.onerror = callback;
    document.head.appendChild(script);
  }

  function renderCanvas(canvas, url, size) {
    loadQrLibrary(function () {
      if (!global.QRCode) {
        return;
      }

      global.QRCode.toCanvas(canvas, url, {
        width: size || QR_OPTIONS.width,
        margin: QR_OPTIONS.margin,
        color: QR_OPTIONS.color,
      });
    });
  }

  function showCanvas(img, canvas, url) {
    if (!canvas) {
      return;
    }

    var size = Number(canvas.dataset.size) || QR_OPTIONS.width;
    canvas.classList.remove("is-hidden");
    canvas.removeAttribute("aria-hidden");
    renderCanvas(canvas, url, size);

    if (img) {
      img.classList.add("is-hidden");
    }
  }

  function showImage(img, canvas) {
    if (!img) {
      return;
    }

    img.classList.remove("is-hidden");
    if (canvas) {
      canvas.classList.add("is-hidden");
      canvas.setAttribute("aria-hidden", "true");
    }
  }

  function initBlock(root) {
    if (!root) {
      return;
    }

    var path = root.getAttribute("data-qr-path") || "";
    var url = getSiteUrl() + (path ? "/" + path.replace(/^\//, "") : "");
    var img = root.querySelector(".qr-block__img");
    var canvas = root.querySelector(".qr-block__canvas");
    var urlEl = root.querySelector(".qr-block__url");
    var copyBtn = root.querySelector(".qr-block__copy");
    var staticSrc = root.getAttribute("data-qr-src") || "/assets/qr-code.png";
    var remoteSrc =
      "https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=" +
      encodeURIComponent(url);

    if (urlEl) {
      urlEl.textContent = displayUrl(url);
    }

    if (img) {
      if (!img.getAttribute("src") || img.getAttribute("src").indexOf("assets/qr-code") !== -1) {
        img.src = staticSrc;
      }

      img.loading = "eager";
      img.decoding = "async";

      img.addEventListener("load", function () {
        if (img.naturalWidth > 0) {
          showImage(img, canvas);
        }
      });

      img.addEventListener("error", function () {
        if (img.dataset.fallback !== "remote") {
          img.dataset.fallback = "remote";
          img.src = remoteSrc;
          return;
        }

        showCanvas(img, canvas, url);
      });

      if (img.complete) {
        if (img.naturalWidth > 0) {
          showImage(img, canvas);
        } else {
          img.dispatchEvent(new Event("error"));
        }
      }
    } else if (canvas) {
      showCanvas(null, canvas, url);
    }

    if (img && canvas && !img.complete) {
      setTimeout(function () {
        if (img.naturalWidth === 0 && canvas.classList.contains("is-hidden")) {
          showCanvas(img, canvas, url);
        }
      }, 1500);
    }

    if (copyBtn) {
      copyBtn.addEventListener("click", function () {
        copyLink(url, copyBtn);
      });
    }
  }

  function copyLink(url, button) {
    var original = button.textContent;

    function done() {
      button.textContent = "Link copied!";
      setTimeout(function () {
        button.textContent = original;
      }, 2000);
    }

    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(url).then(done).catch(function () {
        fallbackCopy(url, button, original);
      });
      return;
    }

    fallbackCopy(url, button, original);
  }

  function fallbackCopy(url, button, original) {
    var input = document.createElement("input");
    input.value = url;
    document.body.appendChild(input);
    input.select();
    try {
      document.execCommand("copy");
      button.textContent = "Link copied!";
    } catch (error) {
      button.textContent = displayUrl(url);
    }
    document.body.removeChild(input);
    setTimeout(function () {
      button.textContent = original;
    }, 2000);
  }

  function initAll() {
    document.querySelectorAll("[data-qr-block]").forEach(initBlock);
  }

  global.CDP_QR = {
    initAll: initAll,
    initBlock: initBlock,
    getSiteUrl: getSiteUrl,
    displayUrl: displayUrl,
    renderCanvas: renderCanvas,
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAll);
  } else {
    initAll();
  }
})(window);
