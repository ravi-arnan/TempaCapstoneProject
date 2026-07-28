/**
 * Asahlagi service worker (ROADMAP §6.5 — "PWA dulu" path).
 *
 * Goal is modest and honest: make the app installable and keep the shell
 * usable when the network drops. Quiz generation still needs the backend, so
 * nothing about the API is cached — a stale quiz would be worse than an error.
 *
 * ponytail: hand-rolled instead of vite-plugin-pwa. Vite asset names are
 * content-hashed and immutable, so runtime cache-first over /assets/ gets the
 * same result as a generated precache manifest without a build plugin. If we
 * ever need true first-visit offline or update prompts, swap in Workbox.
 */
const CACHE = "asahlagi-v1";

// Enough to boot the SPA offline; everything else warms up as the user browses.
const SHELL = ["/", "/manifest.webmanifest", "/favicon.svg", "/icon-192.png"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      // Best-effort: a single 404 must not abort the whole install.
      .then((cache) => Promise.allSettled(SHELL.map((url) => cache.add(url))))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))),
      )
      .then(() => self.clients.claim()),
  );
});

function isCacheableAsset(url) {
  return (
    url.pathname.startsWith("/assets/") ||
    url.pathname.startsWith("/mascot/") ||
    /\.(?:png|svg|webp|woff2?|css|js)$/.test(url.pathname)
  );
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  // Backend lives on another origin (HF Space). Never touch it, never cache it.
  if (url.origin !== self.location.origin) return;

  // SPA navigation: fresh HTML when online, cached shell when not.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const copy = response.clone();
          // waitUntil, not a bare promise: the browser may kill the worker as
          // soon as respondWith settles, and a half-written cache entry is how
          // the offline shell quietly stops existing.
          event.waitUntil(caches.open(CACHE).then((cache) => cache.put("/", copy)));
          return response;
        })
        .catch(() => caches.match("/").then((hit) => hit ?? Response.error())),
    );
    return;
  }

  if (!isCacheableAsset(url)) return;

  // Hashed build output: cache-first is safe, a new build means a new name.
  event.respondWith(
    caches.match(request).then(
      (hit) =>
        hit ??
        fetch(request).then((response) => {
          if (response.ok) {
            const copy = response.clone();
            event.waitUntil(
              caches.open(CACHE).then((cache) => cache.put(request, copy)),
            );
          }
          return response;
        }),
    ),
  );
});
