"""登録免許税クイック計算機（正本：Dropbox _共通\\ツール）を事務所HPの隠しパスへ写す。

    python scripts/sync_toumen.py              # 写す＋ビルド（dist/ を更新）
    python scripts/sync_toumen.py --deploy     # 写す＋ビルド＋デプロイ
    python scripts/sync_toumen.py --no-build   # 写すだけ（ローカル確認用）

やること
  1. 正本HTMLを public/tools/<隠しパス>/index.html にコピー。head に noindex・manifest・アイコン、
     body 末尾に Service Worker の登録を差し込む（正本は触らない）。
  2. sw.js を書き出す。CACHE のバージョンは index.html の内容ハッシュなので、
     正本を直して流し直すたびに SW が更新され、スマホ側のキャッシュも入れ替わる。
  3. npm run build。sitemap に隠しパスが載っていないことを確認する。
  4. --deploy のとき scripts/deploy.config.json の method に従ってデプロイ。
       {"method": "git"}                                → git add/commit/push（Cloudflare Pages の Git 連携）
       {"method": "wrangler", "project": "<Pages名>"}  → npx wrangler pages deploy dist
     config が無ければ手順を表示して終わる（推測でデプロイしない）。
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # Windows コンソールの文字化け対策
HIDDEN = "vzpqflysskptq1"  # 推測されにくいパス。変えるときは manifest/_HPメモ/_HP設置メモ も直す
DEST_DIR = REPO / "public" / "tools" / HIDDEN
DEST_HTML = DEST_DIR / "index.html"
DEST_SW = DEST_DIR / "sw.js"
SRC = (
    Path.home() / "Dropbox" / "亀田ファイル" / "【CoworkProjects】" / "_共通" / "ツール"
    / "登録免許税クイック計算機.html"
)
DEPLOY_CONFIG = REPO / "scripts" / "deploy.config.json"

HEAD_TAGS = """<meta name="robots" content="noindex,nofollow">
<meta name="theme-color" content="#4A7FC5">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="登録免許税">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icon-180.png">
<link rel="icon" href="icon-192.png" type="image/png">
"""

SW_REGISTER = """<script>
// HP設置版のみ：オフライン用 Service Worker（scope はこのディレクトリだけ）
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost' || location.hostname === '127.0.0.1')) {
  window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });
}
</script>
"""

SW_TEMPLATE = """// 登録免許税クイック計算機 Service Worker（sync_toumen.py が生成。手で直さない）
// scope はこのディレクトリだけ。サイト本体には関与しない。
const VERSION = '__VERSION__';
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
"""


def inject(html: str) -> str:
    if "</title>" not in html or "</body>" not in html:
        raise SystemExit("正本HTMLに </title> か </body> が無い")
    if 'name="robots"' in html:
        raise SystemExit("正本HTMLに robots メタが既にある（二重差し込みになる）")
    html = html.replace("</title>", "</title>\n" + HEAD_TAGS, 1)
    html = html.replace("</body>", SW_REGISTER + "</body>", 1)
    return html


def check_offline(html: str) -> None:
    bad = re.findall(r'<(?:script|link)[^>]+(?:src|href)=["\']https?://', html)
    if bad:
        raise SystemExit(f"外部リソース参照がある（単一HTML・外部通信なしの前提が崩れる）: {bad[:3]}")


def run(cmd: list[str], **kw) -> None:
    print("$", " ".join(cmd))
    subprocess.run(cmd, cwd=REPO, check=True, shell=(sys.platform == "win32"), **kw)


def main() -> int:
    args = sys.argv[1:]
    if not SRC.exists():
        raise SystemExit(f"正本が無い: {SRC}")
    html = SRC.read_text(encoding="utf-8")
    check_offline(html)
    out = inject(html)
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    DEST_HTML.write_text(out, encoding="utf-8", newline="\n")
    version = hashlib.sha256(out.encode("utf-8")).hexdigest()[:12]
    DEST_SW.write_text(SW_TEMPLATE.replace("__VERSION__", version), encoding="utf-8", newline="\n")
    for f in ("manifest.webmanifest", "icon-192.png", "icon-512.png", "icon-180.png"):
        if not (DEST_DIR / f).exists():
            raise SystemExit(f"{f} が無い。python scripts/make_toumen_icons.py を先に流す")
    print(f"copied -> {DEST_HTML.relative_to(REPO)}  (sw version {version})")

    if "--no-build" in args:
        return 0

    run(["npm", "run", "build"])
    dist = REPO / "dist"
    if not (dist / "tools" / HIDDEN / "index.html").exists():
        raise SystemExit("dist に計算機が出ていない")
    for sm in dist.glob("sitemap*.xml"):
        if "/tools/" in sm.read_text(encoding="utf-8"):
            raise SystemExit(f"sitemap に /tools/ が載っている: {sm}")
    robots = (dist / "robots.txt").read_text(encoding="utf-8")
    if "tools" in robots:
        raise SystemExit("robots.txt に tools の記述がある（ブロックするとパスが露出する）")
    print("build OK（sitemap・robots.txt に隠しパスなし）")

    if "--deploy" not in args:
        print("デプロイは --deploy を付けて流す")
        return 0

    if not DEPLOY_CONFIG.exists():
        print(
            "scripts/deploy.config.json が無いのでデプロイしていない。\n"
            '  Git連携（GitHub→Cloudflare Pages）なら {"method": "git"}\n'
            '  直接アップロードなら {"method": "wrangler", "project": "<Cloudflare Pages のプロジェクト名>"}\n'
            "  を書いてから --deploy を流す。"
        )
        return 3
    cfg = json.loads(DEPLOY_CONFIG.read_text(encoding="utf-8"))
    method = cfg.get("method")
    if method == "git":
        run(["git", "add", "public/tools", "public/_headers"])
        status = subprocess.run(["git", "status", "--porcelain", "public/tools", "public/_headers"],
                                cwd=REPO, capture_output=True, text=True, shell=(sys.platform == "win32")).stdout
        if status.strip():
            run(["git", "commit", "-m", f"登録免許税クイック計算機を更新（{version}）"])
        else:
            print("変更なし（コミットしない）")
        run(["git", "push"])
        print("push 完了。Cloudflare Pages のビルドが終わるまで1〜2分待つ")
    elif method == "wrangler":
        project = cfg.get("project")
        if not project:
            raise SystemExit("deploy.config.json に project が無い")
        run(["npx", "wrangler", "pages", "deploy", "dist", "--project-name", project])
    else:
        raise SystemExit(f"method が不明: {method!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
