const CACHE_NAME = "traknus-battery-pwa-v1";
const APP_BASE = self.registration.scope;
const APP_SHELL = [
  APP_BASE,
  new URL("index.html", APP_BASE).href,
  new URL("manifest.webmanifest", APP_BASE).href,
  new URL("icons/traknus-app-192.png", APP_BASE).href,
  new URL("icons/traknus-app-512.png", APP_BASE).href,
  new URL("icons/traknus-app-512-maskable.png", APP_BASE).href,
  new URL("icons/traknus-app-180.png", APP_BASE).href
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(APP_SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key.startsWith("traknus-battery-pwa-") && key !== CACHE_NAME)
        .map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request).then(response => {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
        return response;
      }).catch(async () => {
        return (await caches.match(request)) || caches.match(new URL("index.html", APP_BASE).href);
      })
    );
    return;
  }

  event.respondWith(caches.match(request).then(cached => {
    const fresh = fetch(request).then(response => {
      if (response.ok) caches.open(CACHE_NAME).then(cache => cache.put(request, response.clone()));
      return response;
    }).catch(() => cached);
    return cached || fresh;
  }));
});
