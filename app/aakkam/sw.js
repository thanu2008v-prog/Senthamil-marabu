// செந்தமிழ் ஆக்கம் — service worker. செயலிக் கூட்டைச் சேமித்து இணையமின்றியும் திறக்கும்; ஆக்கத்துக்கு இணையம் வேண்டும்.
const CACHE = "aakkam-5b3a4ddb643f";
const FILES = ["./", "index.html", "thaniyurimai.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "icons/apple-touch-icon.png", "fonts/noto-serif-tamil-tamil-400-normal.woff2", "fonts/noto-serif-tamil-tamil-700-normal.woff2", "fonts/noto-sans-tamil-tamil-400-normal.woff2", "fonts/noto-sans-tamil-tamil-700-normal.woff2"];
self.addEventListener("install", e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;      // Claude அழைப்பு நேரடியாக
  e.respondWith(caches.match(e.request, { ignoreSearch: true }).then(hit => hit || fetch(e.request).then(res => {
    const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return res; }).catch(() => caches.match("index.html"))));
});
