(function () {
  "use strict";

  var uploadConfig = window.CDP_UPLOAD || {
    MAX_BYTES: 5 * 1024 * 1024 * 1024,
    MAX_LABEL: "5 GB",
    MULTIPART_BYTES: 100 * 1024 * 1024,
    COMPRESS_SKIP_BYTES: 50 * 1024 * 1024,
  };

  var DB_NAME = "cdp-gallery";
  var DB_VERSION = 1;
  var STORE = "photos";
  var apiAvailable = null;

  var form = document.getElementById("gallery-form");
  var status = document.getElementById("gallery-status");
  var fileInput = document.getElementById("gallery-file");
  var dropZone = document.getElementById("gallery-drop");
  var dropContent = document.getElementById("gallery-drop-content");
  var previewWrap = document.getElementById("gallery-preview");
  var previewImg = document.getElementById("gallery-preview-img");
  var previewVideo = document.getElementById("gallery-preview-video");
  var clearBtn = document.getElementById("gallery-clear");
  var submitBtn = document.getElementById("gallery-submit");
  var grid = document.getElementById("gallery-grid");
  var emptyEl = document.getElementById("gallery-empty");
  var countEl = document.getElementById("gallery-count");
  var lightbox = document.getElementById("gallery-lightbox");
  var lightboxMedia = document.getElementById("lightbox-media");
  var lightboxCaption = document.getElementById("lightbox-caption");
  var lightboxClose = document.getElementById("lightbox-close");

  var selectedFile = null;
  var previewUrl = null;
  var blobClientPromise = null;
  var preparedFilePromise = null;
  var SERVER_MAX_BYTES = 4 * 1024 * 1024;
  var COMPRESS_SKIP_BYTES = uploadConfig.COMPRESS_SKIP_BYTES || 400 * 1024;
  var MULTIPART_BYTES = uploadConfig.MULTIPART_BYTES || 100 * 1024 * 1024;
  var COMPRESS_MAX_DIM = 2048;
  var BLOB_CLIENT_URL =
    "https://esm.sh/@vercel/blob@0.27.3/client?target=es2020";

  var EXT_TO_TYPE = {
    jpg: "image/jpeg",
    jpeg: "image/jpeg",
    png: "image/png",
    webp: "image/webp",
    gif: "image/gif",
    heic: "image/heic",
    heif: "image/heif",
    mp4: "video/mp4",
    mov: "video/quicktime",
    webm: "video/webm",
    avi: "video/x-msvideo",
  };

  function setStatus(message, type) {
    if (!status) {
      return;
    }
    status.textContent = message;
    status.className = "form-note" + (type ? " form-note--" + type : "");
  }

  function fileContentType(file) {
    if (!file) {
      return "";
    }
    var fromType = String(file.type || "").toLowerCase();
    if (fromType) {
      return fromType;
    }
    var ext = String(file.name || "")
      .split(".")
      .pop()
      .toLowerCase();
    return EXT_TO_TYPE[ext] || "";
  }

  function isVideoFile(file) {
    return fileContentType(file).indexOf("video/") === 0;
  }

  function isAllowedFile(file) {
    var type = fileContentType(file);
    return type.indexOf("image/") === 0 || type.indexOf("video/") === 0;
  }

  function mediaTypeFor(photo) {
    if (photo.mediaType === "video") {
      return "video";
    }
    if (photo.contentType && photo.contentType.indexOf("video/") === 0) {
      return "video";
    }
    return "image";
  }

  function loadBlobClient() {
    if (!blobClientPromise) {
      blobClientPromise = import(BLOB_CLIENT_URL);
    }
    return blobClientPromise;
  }

  function compressImage(file) {
    return new Promise(function (resolve) {
      if (!file || isVideoFile(file)) {
        resolve(file);
        return;
      }

      var type = fileContentType(file);
      if (type === "image/gif" || file.size <= COMPRESS_SKIP_BYTES) {
        resolve(file);
        return;
      }

      var blobUrl = URL.createObjectURL(file);
      var finished = false;

      function done(result) {
        if (finished) {
          return;
        }
        finished = true;
        URL.revokeObjectURL(blobUrl);
        resolve(result || file);
      }

      function encodeCanvas(source, width, height) {
        var scale = Math.min(1, COMPRESS_MAX_DIM / Math.max(width, height));
        var cw = Math.max(1, Math.round(width * scale));
        var ch = Math.max(1, Math.round(height * scale));

        if (
          scale === 1 &&
          file.size <= 1024 * 1024 &&
          type === "image/jpeg"
        ) {
          done(file);
          return;
        }

        var canvas = document.createElement("canvas");
        canvas.width = cw;
        canvas.height = ch;
        canvas.getContext("2d").drawImage(source, 0, 0, cw, ch);

        if (source.close) {
          source.close();
        }

        canvas.toBlob(
          function (blob) {
            if (!blob || blob.size >= file.size * 0.95) {
              done(file);
              return;
            }
            var base = String(file.name || "photo").replace(/\.[^.]+$/, "");
            done(
              new File([blob], base + ".jpg", {
                type: "image/jpeg",
                lastModified: Date.now(),
              })
            );
          },
          "image/jpeg",
          0.82
        );
      }

      if (window.createImageBitmap) {
        createImageBitmap(file)
          .then(function (bitmap) {
            encodeCanvas(bitmap, bitmap.width, bitmap.height);
          })
          .catch(function () {
            var img = new Image();
            img.onload = function () {
              encodeCanvas(img, img.naturalWidth, img.naturalHeight);
            };
            img.onerror = function () {
              done(file);
            };
            img.src = blobUrl;
          });
        return;
      }

      var img = new Image();
      img.onload = function () {
        encodeCanvas(img, img.naturalWidth, img.naturalHeight);
      };
      img.onerror = function () {
        done(file);
      };
      img.src = blobUrl;
    });
  }

  function prepareUploadFile(file) {
    return compressImage(file);
  }

  function safeUploadPath(file) {
    var stem = String(file.name || "upload")
      .replace(/\.[^.]+$/, "")
      .replace(/[^\w.-]+/g, "-")
      .slice(0, 48);
    return "gallery/" + Date.now() + "-" + (stem || "upload");
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

  function idbGetAll() {
    return openDb().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(STORE, "readonly");
        var store = tx.objectStore(STORE);
        var request = store.getAll();
        request.onsuccess = function () {
          resolve(request.result || []);
        };
        request.onerror = function () {
          reject(request.error);
        };
      });
    });
  }

  function idbPut(photo) {
    return openDb().then(function (db) {
      return new Promise(function (resolve, reject) {
        var tx = db.transaction(STORE, "readwrite");
        tx.objectStore(STORE).put(photo);
        tx.oncomplete = function () {
          resolve();
        };
        tx.onerror = function () {
          reject(tx.error);
        };
      });
    });
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

  function loadPhotos() {
    return checkApi().then(function (hasApi) {
      if (hasApi) {
        return fetch("/api/photos")
          .then(function (response) {
            return response.json();
          })
          .then(function (data) {
            return data.photos || [];
          });
      }
      return idbGetAll().then(function (photos) {
        return photos.sort(function (a, b) {
          return new Date(b.uploadedAt).getTime() - new Date(a.uploadedAt).getTime();
        });
      });
    });
  }

  function createMediaElement(photo, forGrid) {
    var isVideo = mediaTypeFor(photo) === "video";

    if (isVideo) {
      var video = document.createElement("video");
      video.src = photo.url;
      video.muted = true;
      video.playsInline = true;
      video.preload = "metadata";
      if (forGrid) {
        video.autoplay = true;
        video.loop = true;
      } else {
        video.controls = true;
        video.className = "gallery-lightbox__video";
      }
      video.alt = photo.caption || ("Video by " + photo.name);
      return video;
    }

    var img = document.createElement("img");
    img.src = photo.url;
    img.alt = photo.caption || ("Photo by " + photo.name);
    img.loading = forGrid ? "lazy" : "eager";
    if (!forGrid) {
      img.className = "gallery-lightbox__img";
    }
    return img;
  }

  function renderGallery(photos) {
    if (!grid || !emptyEl || !countEl) {
      return;
    }

    grid.innerHTML = "";

    if (photos.length === 0) {
      emptyEl.classList.remove("is-hidden");
      countEl.textContent = "No uploads yet";
      return;
    }

    emptyEl.classList.add("is-hidden");
    countEl.textContent =
      photos.length === 1 ? "1 upload shared" : photos.length + " uploads shared";

    photos.forEach(function (photo) {
      var item = document.createElement("button");
      item.type = "button";
      item.className = "gallery-item";
      item.setAttribute(
        "aria-label",
        "View " + (mediaTypeFor(photo) === "video" ? "video" : "photo") + " by " + photo.name
      );

      var meta = document.createElement("span");
      meta.className = "gallery-item__meta";
      meta.textContent =
        (mediaTypeFor(photo) === "video" ? "Video · " : "") + photo.name;

      item.appendChild(createMediaElement(photo, true));
      item.appendChild(meta);

      item.addEventListener("click", function () {
        openLightbox(photo);
      });

      grid.appendChild(item);
    });
  }

  function refreshGallery() {
    return loadPhotos().then(renderGallery);
  }

  var lightboxTrigger = null;

  function openLightbox(photo) {
    if (!lightbox || !lightboxMedia || !lightboxCaption) {
      return;
    }

    lightboxTrigger = document.activeElement;
    lightboxMedia.innerHTML = "";
    lightboxMedia.appendChild(createMediaElement(photo, false));
    lightboxCaption.textContent = photo.caption
      ? photo.name + " — " + photo.caption
      : photo.name;
    lightbox.showModal();
    if (lightboxClose) {
      lightboxClose.focus();
    }
  }

  function closeLightbox() {
    if (!lightbox) {
      return;
    }
    lightbox.close();
    if (lightboxTrigger && typeof lightboxTrigger.focus === "function") {
      lightboxTrigger.focus();
    }
    lightboxTrigger = null;
  }

  if (lightboxClose && lightbox) {
    lightboxClose.addEventListener("click", closeLightbox);
    lightbox.addEventListener("click", function (event) {
      if (event.target === lightbox) {
        closeLightbox();
      }
    });
    lightbox.addEventListener("cancel", function () {
      if (lightboxMedia) {
        lightboxMedia.innerHTML = "";
      }
    });
  }

  function clearPreview() {
    selectedFile = null;
    preparedFilePromise = null;
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      previewUrl = null;
    }
    if (previewImg) {
      previewImg.removeAttribute("src");
      previewImg.classList.add("is-hidden");
    }
    if (previewVideo) {
      previewVideo.pause();
      previewVideo.removeAttribute("src");
      previewVideo.load();
      previewVideo.classList.add("is-hidden");
    }
    if (fileInput) {
      fileInput.value = "";
      fileInput.style.pointerEvents = "";
    }
    if (previewWrap) {
      previewWrap.classList.add("is-hidden");
    }
    if (dropContent) {
      dropContent.classList.remove("is-hidden");
    }
  }

  function setPreview(file) {
    if (!isAllowedFile(file)) {
      setStatus("Please choose a photo or video file.", "error");
      return;
    }
    if (file.size > uploadConfig.MAX_BYTES) {
      setStatus("File must be " + uploadConfig.MAX_LABEL + " or smaller.", "error");
      return;
    }

    selectedFile = file;
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    previewUrl = URL.createObjectURL(file);

    if (isVideoFile(file) && previewVideo) {
      previewVideo.src = previewUrl;
      previewVideo.classList.remove("is-hidden");
      if (previewImg) {
        previewImg.classList.add("is-hidden");
      }
    } else if (previewImg) {
      previewImg.src = previewUrl;
      previewImg.alt = "Preview of selected photo";
      previewImg.classList.remove("is-hidden");
      if (previewVideo) {
        previewVideo.classList.add("is-hidden");
      }
    }

    dropContent.classList.add("is-hidden");
    previewWrap.classList.remove("is-hidden");
    fileInput.style.pointerEvents = "none";
    setStatus("");
    preparedFilePromise = prepareUploadFile(file);
  }

  if (fileInput) {
    fileInput.addEventListener("change", function () {
      if (fileInput.files && fileInput.files[0]) {
        setPreview(fileInput.files[0]);
      }
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", clearPreview);
  }

  if (dropZone) {
    ["dragenter", "dragover"].forEach(function (eventName) {
      dropZone.addEventListener(eventName, function (event) {
        event.preventDefault();
        dropZone.classList.add("is-dragover");
      });
    });

    ["dragleave", "drop"].forEach(function (eventName) {
      dropZone.addEventListener(eventName, function (event) {
        event.preventDefault();
        dropZone.classList.remove("is-dragover");
      });
    });

    dropZone.addEventListener("drop", function (event) {
      var file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
      if (file) {
        setPreview(file);
      }
    });
  }

  function readFileAsDataUrl(file) {
    return new Promise(function (resolve, reject) {
      var reader = new FileReader();
      reader.onload = function () {
        resolve(reader.result);
      };
      reader.onerror = function () {
        reject(reader.error);
      };
      reader.readAsDataURL(file);
    });
  }

  function uploadLocal(file, name, caption) {
    if (isVideoFile(file) && file.size > 15 * 1024 * 1024) {
      return Promise.reject(
        new Error("Videos are too large to save locally. Use the live site to upload.")
      );
    }

    return readFileAsDataUrl(file).then(function (dataUrl) {
      var photo = {
        id: "local-" + Date.now() + "-" + Math.random().toString(36).slice(2, 9),
        url: dataUrl,
        name: name,
        caption: caption,
        contentType: fileContentType(file),
        mediaType: isVideoFile(file) ? "video" : "image",
        uploadedAt: new Date().toISOString(),
      };
      return idbPut(photo).then(function () {
        return {
          pending: false,
          message:
            "Saved locally. Deploy to Vercel with Blob storage to share with everyone.",
        };
      });
    });
  }

  function parseUploadResponse(response) {
    return response.json().then(function (data) {
      if (!response.ok) {
        var error = new Error(data.error || "Upload failed.");
        error.code = data.code;
        throw error;
      }
      return data;
    });
  }

  function uploadViaServer(file, name, caption) {
    var formData = new FormData();
    formData.append("file", file, file.name || "upload");
    formData.append("name", name);
    formData.append("caption", caption);

    return fetch("/api/upload", {
      method: "POST",
      body: formData,
    }).then(parseUploadResponse);
  }

  function registerGalleryUpload(blob, file, name, caption) {
    return fetch("/api/gallery-register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: blob.url,
        contentType: fileContentType(file),
        name: name,
        caption: caption,
      }),
    }).then(parseUploadResponse);
  }

  function uploadViaClient(file, name, caption) {
    return loadBlobClient()
      .then(function (mod) {
        return mod.upload(safeUploadPath(file), file, {
          access: "public",
          handleUploadUrl: "/api/upload",
          contentType: fileContentType(file) || undefined,
          multipart: file.size > MULTIPART_BYTES,
        });
      })
      .then(function (blob) {
        return registerGalleryUpload(blob, file, name, caption);
      });
  }

  function uploadRemote(file, name, caption) {
    if (isVideoFile(file) || file.size > SERVER_MAX_BYTES) {
      return uploadViaClient(file, name, caption);
    }
    return uploadViaServer(file, name, caption).catch(function (error) {
      if (error.code === "USE_CLIENT_UPLOAD") {
        return uploadViaClient(file, name, caption);
      }
      throw error;
    });
  }

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      if (!selectedFile) {
        setStatus("Please choose a photo or video to upload.", "error");
        return;
      }

      var name = form.name.value.trim() || "Anonymous";
      var caption = form.caption.value.trim();
      var uploadLabel = isVideoFile(selectedFile) ? "video" : "photo";

      submitBtn.disabled = true;
      setStatus("Preparing your " + uploadLabel + "…");

      checkApi()
        .then(function (hasApi) {
          if (!hasApi) {
            return uploadLocal(selectedFile, name, caption);
          }

          return (preparedFilePromise || prepareUploadFile(selectedFile))
            .then(function (prepared) {
              if (prepared !== selectedFile && !isVideoFile(prepared)) {
                setStatus("Uploading optimized " + uploadLabel + "…");
              } else if (prepared.size > MULTIPART_BYTES) {
                setStatus("Uploading large " + uploadLabel + " — this may take a while…");
              } else {
                setStatus("Uploading your " + uploadLabel + "…");
              }
              return uploadRemote(prepared, name, caption);
            });
        })
        .then(function (data) {
          clearPreview();
          form.caption.value = "";
          setStatus(data.message || "Upload complete!", "success");
          if (!data.pending) {
            return refreshGallery();
          }
        })
        .catch(function (error) {
          setStatus(error.message || "Something went wrong. Please try again.", "error");
        })
        .finally(function () {
          submitBtn.disabled = false;
        });
    });
  }

  refreshGallery();
  setInterval(refreshGallery, 30000);

  checkApi().then(function (hasApi) {
    if (hasApi) {
      loadBlobClient();
    }
  });
})();
