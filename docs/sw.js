const CACHE = 'radar-v1';
const OFFLINE_URL = '/rd-thoughts/';

const PRECACHE = [
  '/rd-thoughts/',
  '/rd-thoughts/index.html',
  '/rd-thoughts/archive.html',
  '/rd-thoughts/icon-192.png',
  '/rd-thoughts/icon-512.png',
  '/rd-thoughts/manifest.json',
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // Only handle same-origin requests
  if (!url.pathname.startsWith('/rd-thoughts')) return;

  e.respondWith(
    fetch(e.request)
      .then(resp => {
        // Cache successful HTML/image responses
        if (resp.ok && (url.pathname.endsWith('.html') || url.pathname.endsWith('.png')
            || url.pathname === '/rd-thoughts/' || url.pathname === '/rd-thoughts')) {
          const clone = resp.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return resp;
      })
      .catch(() => caches.match(e.request).then(cached => cached || caches.match(OFFLINE_URL)))
  );
});
