"""இணையக் கருவிகள் உருவாக்கம்.
  karuvi/noolvazhi.html, karuvi/aakkam.html — Claude-இல் வெளியிடும் பக்கங்கள் (Artifact)
  app/aakkam/ — «செந்தமிழ் ஆக்கம்» தொலைபேசியில் தனியாக இயங்கும் செயலி (PWA): index.html, manifest, sw.js, சின்னங்கள், எழுத்துருக்கள்
python3 karuvi/build.py
"""
import json, shutil, hashlib
from pathlib import Path

H = Path(__file__).resolve().parent
ROOT = H.parent
GFONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
          '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+Tamil:wght@500;700&family=Hind+Madurai:wght@400;500;600&display=swap">')
logic = (H / "logic.js").read_text("utf-8").replace("if (typeof module", "if (false && typeof module")

# ── Claude-இல் வெளியிடும் பக்கங்கள்
page = (H / "page.html").read_text("utf-8").replace("/*LOGIC*/", logic).replace("/*BOOKWORDS*/", (H / "bookwords.json").read_text("utf-8"))
(H / "noolvazhi.html").write_text(page, "utf-8")
aakkam_src = (H / "aakkam_page.html").read_text("utf-8")
(H / "aakkam.html").write_text(aakkam_src.replace("<!--FONTS-->", GFONTS).replace("/*LOGIC*/", logic), "utf-8")

# ── தனிச் செயலி (PWA)
APP = ROOT / "app/aakkam"
(APP / "fonts").mkdir(parents=True, exist_ok=True)
(APP / "icons").mkdir(exist_ok=True)
FONTS = {"noto-serif-tamil-tamil-400-normal.woff2": ("Noto Serif Tamil", 400), "noto-serif-tamil-tamil-700-normal.woff2": ("Noto Serif Tamil", 700),
         "noto-sans-tamil-tamil-400-normal.woff2": ("Noto Sans Tamil", 400), "noto-sans-tamil-tamil-700-normal.woff2": ("Noto Sans Tamil", 700)}
for f in FONTS:
    shutil.copy(ROOT / "book/fonts" / f, APP / "fonts" / f)
shutil.copy(ROOT / "book/fonts/OFL.txt", APP / "fonts/OFL.txt")
face = "\n".join(f'@font-face {{ font-family: "{fam}"; font-weight: {w}; font-display: swap; src: url("fonts/{f}") format("woff2"); }}'
                 for f, (fam, w) in FONTS.items())
head = f"""<!doctype html>
<html lang="ta">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#145c50">
<meta name="description" content="திணை, உணர்வு, கூற்று தேர்ந்து புதிய செந்தமிழ்ப் பாடலோ கட்டுரையோ உருவாக்கும் செயலி.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<style>{face}
:root {{ padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px) }}
body {{ margin: 0 }}
</style>
</head>
<body>
"""
sw_reg = """
<script>
if ("serviceWorker" in navigator) addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
</script>
</body>
</html>
"""
body = aakkam_src.replace("<!--FONTS-->", "").replace("/*LOGIC*/", logic)
body = body.replace("தொழில்நுட்ப உதவி: Claude (Anthropic).</footer>",
                    'தொழில்நுட்ப உதவி: Claude (Anthropic). · <a href="thaniyurimai.html">தனியுரிமை</a></footer>', 1)
(APP / "thaniyurimai.html").write_text((H / "thaniyurimai.html").read_text("utf-8").replace("/*FACE*/", face), "utf-8")
(APP / "index.html").write_text(head + body + sw_reg, "utf-8")

manifest = {
    "name": "செந்தமிழ் ஆக்கம்", "short_name": "ஆக்கம்", "lang": "ta", "dir": "ltr",
    "description": "திணை, உணர்வு, கூற்று தேர்ந்து புதிய செந்தமிழ்ப் பாடலோ கட்டுரையோ உருவாக்கும் செயலி.",
    "id": "./", "start_url": "./", "scope": "./", "display": "standalone", "orientation": "portrait",
    "background_color": "#eef2ee", "theme_color": "#145c50", "categories": ["education", "books"],
    "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}],
}
(APP / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), "utf-8")

# சின்னங்கள் — «செ» இலைப் பச்சையில்
from PIL import Image, ImageDraw, ImageFont
def icon(size, pad, path, radius):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=(20, 92, 80, 255))
    ft = ImageFont.truetype(str(ROOT / "book/fonts/noto-serif-tamil-tamil-700-normal.woff2"), int(size * (1 - 2 * pad) * 0.62))
    l, t, r, b = d.textbbox((0, 0), "செ", font=ft)
    d.text(((size - (r - l)) / 2 - l, (size - (b - t)) / 2 - t), "செ", font=ft, fill=(246, 244, 234, 255))
    im.save(path)
icon(192, 0.08, APP / "icons/icon-192.png", 40)
icon(512, 0.08, APP / "icons/icon-512.png", 108)
icon(512, 0.2, APP / "icons/maskable-512.png", 0)
icon(180, 0.08, APP / "icons/apple-touch-icon.png", 0)

# service worker — செயலிக் கூடு இணையமின்றியும் திறக்க; பதிப்பு உள்ளடக்கத்தின் கைரேகையால்
files = ["./", "index.html", "thaniyurimai.html", "manifest.webmanifest", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png",
         "icons/apple-touch-icon.png"] + [f"fonts/{f}" for f in FONTS]
digest = hashlib.sha256(b"".join((APP / f).read_bytes() for f in files if f != "./")).hexdigest()[:12]
sw = f"""// செந்தமிழ் ஆக்கம் — service worker. செயலிக் கூட்டைச் சேமித்து இணையமின்றியும் திறக்கும்; ஆக்கத்துக்கு இணையம் வேண்டும்.
const CACHE = "aakkam-{digest}";
const FILES = {json.dumps(files)};
self.addEventListener("install", e => e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {{
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;      // Claude அழைப்பு நேரடியாக
  e.respondWith(caches.match(e.request, {{ ignoreSearch: true }}).then(hit => hit || fetch(e.request).then(res => {{
    const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return res; }}).catch(() => caches.match("index.html"))));
}});
"""
(APP / "sw.js").write_text(sw, "utf-8")
print("karuvi: noolvazhi.html, aakkam.html · app/aakkam: PWA", digest)
