const CACHE_NAME = 'babelflow-v1'
const SHELL_URLS = ['/', '/index.html']

// Install — cache shell
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_URLS))
  )
  self.skipWaiting()
})

// Activate — clean old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  )
  self.clients.claim()
})

// Fetch — cache-first for assets, network-first for API
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url)

  // Skip non-GET and WebSocket
  if (event.request.method !== 'GET' || url.protocol === 'ws:' || url.protocol === 'wss:') return

  // API calls — network first
  if (url.pathname.startsWith('/api/') || url.pathname === '/health') {
    event.respondWith(
      fetch(event.request).catch(() =>
        new Response(JSON.stringify({ error: 'offline' }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' },
        })
      )
    )
    return
  }

  // Assets — cache first
  if (url.pathname.startsWith('/assets/')) {
    event.respondWith(
      caches.match(event.request).then((cached) =>
        cached || fetch(event.request).then((res) => {
          const clone = res.clone()
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone))
          return res
        })
      )
    )
    return
  }

  // Shell — network first, fallback to cache
  event.respondWith(
    fetch(event.request)
      .then((res) => {
        const clone = res.clone()
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone))
        return res
      })
      .catch(() =>
        caches.match(event.request).then((cached) =>
          cached || new Response(
            '<!DOCTYPE html><html><body style="font-family:system-ui;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;background:#f9fafb"><h1 style="color:#6b7280">BabelFlow is offline</h1></body></html>',
            { headers: { 'Content-Type': 'text/html' } }
          )
        )
      )
  )
})
