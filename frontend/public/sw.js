// ScamShield India Service Worker (PWA Offline Shell)
const CACHE_NAME = "scamshield-v1";
const ASSETS_TO_CACHE = [
  "/",
  "/manifest.json",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  // Only cache GET requests and do NOT cache /api/ dynamic calls
  if (event.request.method === "GET" && !event.request.url.includes("/api/")) {
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        return (
          cachedResponse ||
          fetch(event.request).catch(() => {
            // Offline fallback
            if (event.request.mode === "navigate") {
              return caches.match("/");
            }
          })
        );
      })
    );
  }
});
