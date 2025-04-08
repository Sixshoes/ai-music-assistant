const CACHE_NAME = 'ai-music-assistant-cache-v1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/assets/js/main.js',
  '/assets/css/main.css',
  '/assets/fonts/',
  '/assets/images/'
];

// 安裝 Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(STATIC_ASSETS);
      })
  );
});

// 啟用 Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      );
    })
  );
});

// 攔截請求
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // 快取命中
        if (response) {
          return response;
        }

        // 網路請求
        return fetch(event.request)
          .then((response) => {
            // 檢查是否為有效的響應
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // 克隆響應
            const responseToCache = response.clone();

            // 將響應存入快取
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return response;
          });
      })
  );
}); 