/*
 * Service worker for Church Security Album.
 * Caches the static app shell (CSS/JS/icons/manifest) so the album UI
 * loads instantly and works offline; page HTML and member photos are
 * always fetched fresh from the network since that data changes.
 * Served from "/" (see app.py's /sw.js route) so it can control the
 * whole app, not just /static/.
 */
const CACHE_NAME = "church-security-album-shell-v1";
const SHELL_ASSETS = [
  "/static/css/style.css",
  "/static/js/app.js",
  "/static/manifest.webmanifest",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "/static/icons/apple-touch-icon.png",
  "/static/icons/favicon.ico",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(
        names
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  const isShellAsset = SHELL_ASSETS.includes(url.pathname);

  if (!isShellAsset) {
    return; // let the browser handle pages, photos, and API calls normally
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const network = fetch(event.request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return response;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
