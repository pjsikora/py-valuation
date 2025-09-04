const CACHE_VERSION = 'v1';
const STATIC_CACHE = `static-${CACHE_VERSION}`;

const APP_SHELL = [
  '/',                     
  '/index.html',          
  '/manifest.webmanifest'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(APP_SHELL))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys.filter(k => k !== STATIC_CACHE).map(k => caches.delete(k))
      );
      await self.clients.claim();
    })()
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;

  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  const isSameOrigin = url.origin === self.location.origin;

  const isStatic =
    isSameOrigin &&
    (url.pathname.endsWith('.css') ||
     url.pathname.endsWith('.js')  ||
     url.pathname.endsWith('.png') ||
     url.pathname.endsWith('.jpg') ||
     url.pathname.endsWith('.jpeg')||
     url.pathname.endsWith('.webp')||
     url.pathname.endsWith('.svg') ||
     APP_SHELL.includes(url.pathname) ||
     url.pathname === '/');

  if (isStatic) {
    event.respondWith(cacheFirst(request));
    return;
  }

  event.respondWith(staleWhileRevalidate(request));
});

async function cacheFirst(request) {
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(request);
  if (cached) return cached;

  try {
    const fresh = await fetch(request);
    cache.put(request, fresh.clone());
    return fresh;
  } catch (err) {
    if (request.mode === 'navigate') {
      const cache = await caches.open(STATIC_CACHE);
      const shell = await cache.match('/index.html') || await cache.match('/');
      if (shell) return shell;
    }
    throw err;
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(STATIC_CACHE);
  const cached = await cache.match(request);

  const networkPromise = fetch(request)
    .then((response) => {
      if (response && (response.status === 200 || response.type === 'opaque')) {
        cache.put(request, response.clone());
      }
      return response;
    })
    .catch(() => null);

  if (cached) return cached;


  const network = await networkPromise;
  if (network) return network;

  if (request.mode === 'navigate') {
    const shell = await cache.match('/index.html') || await cache.match('/');
    if (shell) return shell;
  }

  return new Response('Offline', { status: 503, statusText: 'Offline' });
}
