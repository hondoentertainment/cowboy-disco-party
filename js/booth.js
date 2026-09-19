(function () {
  "use strict";

  var DB_NAME = "cdp-gallery";
  var DB_VERSION = 1;
  var STORE = "photos";

  var stage = document.getElementById("booth-stage");
  var video = document.getElementById("booth-video");
  var shot = document.getElementById("booth-shot");
  var countEl = document.getElementById("booth-count");
  var emptyEl = document.getElementById("booth-empty");
  var nameInput = document.getElementById("booth-name");
  var statusEl = document.getElementById("booth-status");
  var flipBtn = document.getElementById("booth-flip");
  var snapBtn = document.getElementById("booth-snap");
  var retakeBtn = document.getElementById("booth-retake");
  var postBtn = document.getElementById("booth-post");

  var stream = null;
  var facing = "user";
  var blob = null;
  var ticking = false;
  var apiAvailable = null;

  function setStatus(message, type) {
    if (!statusEl) {
      return;
    }
    statusEl.textContent = message || "";
    statusEl.className = "form-note" + (type ? " form-note--" + type : "");
  }

  function setMode(mode) {
    var live = mode === "live";
    var review = mode === "review";
    if (video) {
      video.classList.toggle("is-hidden", !live);
    }
    if (shot) {
      shot.classList.toggle("is-hidden", !review);
    }
    if (snapBtn) {
      snapBtn.classList.toggle("is-hidden", !live);
    }
    if (flipBtn) {
      flipBtn.classList.toggle("is-hidden", !live);
    }
    if (retakeBtn) {
      retakeBtn.classList.toggle("is-hidden", !review);
    }
    if (postBtn) {
      postBtn.classList.toggle("is-hidden", !review);
    }
  }

  function stopStream() {
    if (!stream) {
      return;
    }
    stream.getTracks().forEach(function (track) {
      track.stop();
    });
    stream = null;
  }

  function startCamera() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      if (emptyEl) {
        emptyEl.textContent = "This browser cannot open a camera. Use the gallery to upload a photo.";
      }
      setStatus("Camera is not available on this device.", "error");
      return Promise.resolve(false);
    }

    stopStream();
    if (emptyEl) {
      emptyEl.textContent = "Opening camera…";
      emptyEl.classList.remove("is-hidden");
    }

    return navigator.mediaDevices
      .getUserMedia({
        audio: false,
        video: {
          facingMode: { ideal: facing },
          width: { ideal: 1280 },
          height: { ideal: 1280 },
        },
      })
      .then(function (next) {
        stream = next;
        if (video) {
          video.srcObject = next;
          video.classList.toggle("is-mirrored", facing === "user");
        }
        if (emptyEl) {
          emptyEl.classList.add("is-hidden");
        }
        setMode("live");
        setStatus("Strike a pose — then tap Take photo.");
        return true;
      })
      .catch(function () {
        if (emptyEl) {
          emptyEl.textContent = "Allow the camera, or upload from the gallery instead.";
          emptyEl.classList.remove("is-hidden");
        }
        setStatus("Camera permission is needed for the booth.", "error");
        return false;
      });
  }

  function captureFrame() {
    if (!video || !video.videoWidth) {
      return null;
    }

    var canvas = document.createElement("canvas");
    var width = video.videoWidth;
    var height = video.videoHeight;
    canvas.width = width;
    canvas.height = height;
    var ctx = canvas.getContext("2d");
    if (!ctx) {
      return null;
    }

    if (facing === "user") {
      ctx.translate(width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(video, 0, 0, width, height);
    return canvas;
  }

  function canvasToBlob(canvas) {
    return new Promise(function (resolve) {
      canvas.toBlob(
        function (next) {
          resolve(next);
        },
        "image/jpeg",
        0.9
      );
    });
  }

  function countdown() {
    if (ticking || !stream) {
      return;
    }

    ticking = true;
    var n = 3;
    if (countEl) {
      countEl.classList.remove("is-hidden");
      countEl.textContent = String(n);
    }
    if (snapBtn) {
      snapBtn.disabled = true;
    }

    var timer = window.setInterval(function () {
      n -= 1;
      if (n > 0) {
        if (countEl) {
          countEl.textContent = String(n);
        }
        return;
      }

      window.clearInterval(timer);
      if (countEl) {
        countEl.classList.add("is-hidden");
      }
      if (stage) {
        stage.classList.add("is-flash");
        window.setTimeout(function () {
          stage.classList.remove("is-flash");
        }, 180);
      }

      var canvas = captureFrame();
      if (!canvas) {
        ticking = false;
        if (snapBtn) {
          snapBtn.disabled = false;
        }
        setStatus("Could not capture that frame. Try again.", "error");
        return;
      }

      canvasToBlob(canvas).then(function (next) {
        blob = next;
        if (shot && next) {
          shot.src = URL.createObjectURL(next);
        }
        setMode("review");
        setStatus("Keep it or retake.");
        ticking = false;
        if (snapBtn) {
          snapBtn.disabled = false;
        }
      });
    }, 800);
  }

  function checkApi() {
    if (apiAvailable !== null) {
      return Promise.resolve(apiAvailable);
    }
    return fetch("/api/photos")
      .then(function (response) {
        apiAvailable = response.ok;
        return apiAvailable;
      })
      .catch(function () {
        apiAvailable = false;
        return false;
      });
  }

  function openDb() {
    return new Promise(function (resolve, reject) {
      var request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = function () {
        var db = request.result;
        if (!db.objectStoreNames.contains(STORE)) {
          db.createObjectStore(STORE, { keyPath: "id" });
        }
      };
      request.onsuccess = function () {
        resolve(request.result);
      };
      request.onerror = function () {
        reject(request.error);
      };
    });
  }

  function saveLocal(file, name) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () {
        var photo = {
          id: "local-" + Date.now() + "-" + Math.random().toString(36).slice(2, 9),
          url: reader.result,
          name: name,
          caption: "Photo booth",
          contentType: "image/jpeg",
          mediaType: "image",
          uploadedAt: new Date().toISOString(),
        };
        openDb()
          .then(function (db) {
            return new Promise(function (done, fail) {
              var tx = db.transaction(STORE, "readwrite");
              tx.objectStore(STORE).put(photo);
              tx.oncomplete = function () {
                done({
                  pending: false,
                  message: "Saved on this phone. The live gallery needs the party site online.",
                });
              };
              tx.onerror = function () {
                fail(tx.error);
              };
            });
          })
          .then(resolve)
          .catch(reject);
      };
      reader.onerror = function () {
        reject(reader.error);
      };
      reader.readAsDataURL(file);
    });
  }

  function uploadRemote(file, name) {
    var formData = new FormData();
    formData.append("file", file, "booth.jpg");
    formData.append("name", name);
    formData.append("caption", "Photo booth");

    return fetch("/api/upload", {
      method: "POST",
      body: formData,
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          throw new Error(data.error || "Upload failed.");
        }
        return data;
      });
    });
  }

  function postShot() {
    if (!blob) {
      setStatus("Take a photo first.", "error");
      return;
    }

    var name = (nameInput && nameInput.value.trim()) || "Guest";
    var file = new File([blob], "booth.jpg", { type: "image/jpeg" });
    if (postBtn) {
      postBtn.disabled = true;
    }
    setStatus("Posting to the gallery…");

    checkApi()
      .then(function (hasApi) {
        if (!hasApi) {
          return saveLocal(file, name);
        }
        return uploadRemote(file, name);
      })
      .then(function (data) {
        setStatus(data.message || "You're in the gallery.", "success");
        blob = null;
        if (shot) {
          shot.removeAttribute("src");
        }
        startCamera();
      })
      .catch(function (error) {
        setStatus(error.message || "Could not post that shot. Try again.", "error");
      })
      .finally(function () {
        if (postBtn) {
          postBtn.disabled = false;
        }
      });
  }

  if (snapBtn) {
    snapBtn.addEventListener("click", countdown);
  }

  if (flipBtn) {
    flipBtn.addEventListener("click", function () {
      facing = facing === "user" ? "environment" : "user";
      startCamera();
    });
  }

  if (retakeBtn) {
    retakeBtn.addEventListener("click", function () {
      blob = null;
      if (shot) {
        shot.removeAttribute("src");
      }
      setMode("live");
      setStatus("Strike a pose — then tap Take photo.");
    });
  }

  if (postBtn) {
    postBtn.addEventListener("click", postShot);
  }

  window.addEventListener("pagehide", stopStream);
  startCamera();
})();
