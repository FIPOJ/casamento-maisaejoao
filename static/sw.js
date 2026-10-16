const CACHE_NAME = "casamento-bovi-v35";
const ASSETS = ["/", "/static/app.css", "/static/app.js", "/static/manifest.webmanifest", "/static/icon.svg"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request).then((cached) => cached || caches.match("/")))
  );
});
