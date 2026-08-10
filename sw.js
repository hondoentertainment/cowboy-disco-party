const CACHE = "cdp-v38";
const ASSETS = [
  "/",
  "/index.html",
  "/css/styles.css",
  "/css/brand.css",
  "/css/premium.css",
  "/css/fonts.css",
  "/assets/fonts/cormorant-garamond-400.woff2",
  "/assets/fonts/cormorant-garamond-400-italic.woff2",
  "/assets/fonts/cormorant-garamond-500.woff2",
  "/assets/fonts/cormorant-garamond-600.woff2",
  "/assets/fonts/dm-sans-400.woff2",
  "/assets/fonts/dm-sans-500.woff2",
  "/assets/fonts/dm-sans-600.woff2",
  "/assets/og-card.jpg",
  "/assets/editorial-cocktails.jpg",
  "/assets/editorial-dance.jpg",
  "/assets/editorial-dance.webp",
  "/assets/editorial-photobooth.jpg",
  "/assets/editorial-highlights.jpg",
  "/404.html",
  "/assets/cowboy-disco-party.ics",
  "/js/premium.js",
  "/js/pwa.js",
  "/js/nav.js",
  "/js/poll.js",
  "/assets/brand-mark.svg",
  "/assets/editorial-atmosphere.jpg",
  "/assets/editorial-atmosphere.webp",
  "/assets/editorial-wardrobe.jpg",
  "/assets/editorial-wardrobe.webp",
  "/assets/editorial-cocktails.webp",
  "/js/config.js",
  "/js/main.js",
  "/js/qr.js",
  "/js/vote.js",
  "/js/ice-breaker.js",
  "/assets/poster.webp",
  "/assets/poster-hero.jpg",
  "/assets/drink-list.webp",
  "/assets/drink-list.jpg",
  "/assets/sign-entrance.webp",
  "/assets/sign-entrance.jpg",
  "/assets/sign-kyles-apartment.webp",
  "/assets/sign-kyles-apartment.jpg",
  "/assets/food-labels-sheet.webp",
  "/assets/food-labels-sheet.jpg",
  "/assets/menu.pdf",
  "/assets/qr-code.png",
  "/assets/app-icon.png",
  "/assets/app-icon-192.png",
  "/gallery.html",
  "/js/gallery.js",
  "/js/slideshow.js",
  "/vote.html",
  "/host.html",
  "/plan.html",
  "/js/plan.js",
  "/js/plan-data.js",
  "/poll-results.html",
  "/qr.html",
  "/qr-pack.html",
  "/assets/poster-official.jpg",
  "/assets/look-01.jpg",
  "/assets/look-01.webp",
  "/assets/look-02.jpg",
  "/assets/look-02.webp",
  "/assets/look-03.jpg",
  "/assets/look-03.webp",
  "/assets/look-04.jpg",
  "/assets/look-04.webp",
  "/assets/look-05.jpg",
  "/assets/look-05.webp",
  "/assets/look-06.jpg",
  "/assets/look-06.webp",
  "/assets/qr-gallery.png",
  "/assets/qr-vote.png",
  "/assets/qr-icebreakers.png",
  "/signs.html",
  "/print-pack.html",
  "/party-kit.html",
  "/lookbook.html",
  "/invite-card.html",
  "/schedule-card.html",
  "/css/print-physical.css",
  "/assets/party-kit.pdf",
  "/assets/invite-card.png",
  "/assets/schedule-card.png",
  "/party-night.html",
  "/invite.html",
  "/mobile-test.html",
  "/numbers.html",
  "/slideshow.html",
  "/admin.html",
  "/poll.html",
  "/ice-breaker.html",
  "/manifest.json",
];

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE).then(function (cache) {
      return cache.addAll(ASSETS);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys
          .filter(function (key) {
            return key !== CACHE;
          })
          .map(function (key) {
            return caches.delete(key);
          })
      );
    }).then(function () {
      return self.clients.claim();
    })
  );
});

self.addEventListener("fetch", function (event) {
  if (event.request.method !== "GET") {
    return;
  }

  const url = new URL(event.request.url);
  if (url.pathname.startsWith("/api/")) {
    return;
  }

  event.respondWith(
    caches.match(event.request).then(function (cached) {
      return (
        cached ||
        fetch(event.request).then(function (response) {
          if (!response || response.status !== 200 || response.type !== "basic") {
            return response;
          }
          const copy = response.clone();
          caches.open(CACHE).then(function (cache) {
            cache.put(event.request, copy);
          });
          return response;
        })
      );
    })
  );
});
