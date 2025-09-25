self.addEventListener('install', e => {
    e.waitUntil(
        caches.open('v1').then(cache => {
            return cache.addAll([
                '/home',
                '/static/home.html',
                '/static/manifest.json',
                '/static/icon-192.png',
                '/static/icon-512.png'
            ]);
        })
    );
});

self.addEventListener('fetch', e => {
    e.respondWith(
        caches.match(e.request).then(r => r || fetch(e.request))
    );
});
