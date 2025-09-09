// Basic service worker for caching essential assets
const CACHE_NAME = 'flowchat-v1';
const urlsToCache = [
  '/',
  '/chat',
  '/frontend/static/css/style.css',
  '/frontend/static/js/chat.js',
  '/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        return response || fetch(event.request);
      })
  );
});
