// 登録免許税クイック計算機 Service Worker（sync_toumen.py が生成。手で直さない）
// scope はこのディレクトリだけ。サイト本体には関与しない。
const VERSION = 'f74910ebec5b';
const CACHE = 'toumen-' + VERSION;
const ROOT = self.registration.scope; // https://host/tools/<隠しパス>/
const ASSETS = [ROOT, ROOT + 'manifest.webmanifest', ROOT + 'icon-192.png', ROOT + 'icon-512.png', ROOT + 'icon-180.png'];

self.addEventListener('install', function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(ASSETS); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k.indexOf('toumen-') === 0 && k !== CACHE; }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function (e) {
  if (e.request.method !== 'GET') return;
  var url = new URL(e.request.url);
  if (url.origin !== self.location.origin || url.pathname.indexOf(new URL(ROOT).pathname) !== 0) return;
  // index.html への直打ちもディレクトリURLに寄せる（Cloudflare Pages は index.html をリダイレクトするため）
  var key = e.request.mode === 'navigate' ? ROOT : e.request;
  e.respondWith(
    caches.match(key, { ignoreSearch: true }).then(function (cached) {
      var refresh = fetch(key, { cache: 'no-cache' }).then(function (res) {
        if (res && res.ok && !res.redirected) { var copy = res.clone(); caches.open(CACHE).then(function (c) { c.put(key, copy); }); }
        return res;
      }).catch(function () { return cached; });
      return cached || refresh;
    })
  );
});
