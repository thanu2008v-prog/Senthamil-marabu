"""செந்தமிழ் ஆக்கம் — தனிக் களஞ்சியம் உருவாக்கலும் சரிபார்ப்பும் (docs/THOGUPPU.md §3).
python3 scripts/build_seyali.py  → build/senthamil-aakkam/ , build/senthamil-aakkam-<பதிப்பு>.zip
முன்னர்: python3 karuvi/build.py (app/aakkam உருவாக)."""
import json, re, shutil, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP, SRC = ROOT / "app/aakkam", ROOT / "seyali"
OUT = ROOT / "build/senthamil-aakkam"
FOOTER = "உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; தொழில்நுட்ப உதவி: Claude (Anthropic)"
VERSION = (SRC / "VERSION").read_text().strip()

# ── உருவாக்கல்
if OUT.exists():
    shutil.rmtree(OUT)
shutil.copytree(APP, OUT)
for f in ["README.md", "LICENSE.md", "CHANGES.md", "VERSION"]:
    shutil.copy(SRC / f, OUT / f)
sys.path.insert(0, str(ROOT / "scripts"))
from thoguppu import edu  # noqa: E402
(OUT / "THITTAM.md").write_text(edu("seyali") + "\n---\n\n© 2026 தனுசாந்தன் வர்ணகுலசிங்கம் — உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; தொழில்நுட்ப உதவி: Claude (Anthropic).\n", "utf-8")
shutil.copytree(SRC / "android", OUT / "android")
(OUT / ".github/workflows").mkdir(parents=True)
shutil.copy(SRC / "pages.yml", OUT / ".github/workflows/pages.yml")
shutil.copy(SRC / "gitignore", OUT / ".gitignore")
(OUT / ".nojekyll").write_text("")

# ── சரிபார்ப்பு (திட்டம் §7)
R = []
def ok(n, c, d=""): R.append((n, bool(c), d))
T = lambda p: (OUT / p).read_text("utf-8")

REQ = ["index.html", "manifest.webmanifest", "sw.js", "thaniyurimai.html", "icons/icon-192.png", "icons/icon-512.png",
       "icons/maskable-512.png", "icons/apple-touch-icon.png", "fonts/OFL.txt", "android/twa-manifest.json",
       "android/assetlinks.template.json", ".github/workflows/pages.yml", "README.md", "LICENSE.md", "CHANGES.md",
       "THITTAM.md", "VERSION", ".nojekyll", ".gitignore"]
miss = [p for p in REQ if not (OUT / p).exists()]
ok("1. கோப்புகள்", not miss, ", ".join(miss))

html = T("index.html")
logic = (ROOT / "karuvi/logic.js").read_text("utf-8").split("if (typeof module")[0]
ok("2. நூல் களஞ்சியத்தோடு ஒத்தது", html == (APP / "index.html").read_text("utf-8") and logic in html)

man = json.loads(T("manifest.webmanifest"))
from PIL import Image
sizes = all(Image.open(OUT / i["src"]).size == tuple(map(int, i["sizes"].split("x"))) for i in man["icons"])
ok("3. manifest", man["display"] == "standalone" and man.get("id") and man["start_url"] == man["scope"] == "./"
   and any(i.get("purpose") == "maskable" for i in man["icons"]) and sizes and 'rel="manifest"' in html)

sw = json.loads(re.search(r"const FILES = (\[.*?\]);", T("sw.js")).group(1))
ok("4. service worker", all(f == "./" or (OUT / f).exists() for f in sw) and "thaniyurimai.html" in sw and 'register("sw.js")' in html)

hosts = set()
for page in ["index.html", "thaniyurimai.html"]:
    hosts |= set(re.findall(r"""(?:src|href)\s*=\s*["']https?://([^/"']+)""", T(page)))
    hosts |= set(re.findall(r"""fetch\(\s*["']https?://([^/"']+)""", T(page)))
ok("5. வெளி முகவரி api.anthropic.com மட்டும்", hosts <= {"api.anthropic.com"} and "fonts.googleapis" not in html, str(hosts))

ok("6. தனியுரிமைப் பக்கம் இணைப்பு", 'href="thaniyurimai.html"' in html and "api.anthropic.com" in T("thaniyurimai.html"))

twa = json.loads(T("android/twa-manifest.json"))
chg = re.search(r"^## v([\d.]+)", T("CHANGES.md"), re.M).group(1)
ok("7. பதிப்பு எண் ஒன்றே", VERSION == chg == twa["appVersionName"], f"{VERSION} {chg} {twa['appVersionName']}")
ok("7ஆ. Android அமைப்பு", twa["startUrl"] == "/senthamil-aakkam/" and twa["host"] in twa["webManifestUrl"]
   and json.loads(T("android/assetlinks.template.json"))[0]["target"]["package_name"] == twa["packageId"])

ok("8. உரிமை வரி", all(FOOTER in T(p) for p in ["index.html", "thaniyurimai.html", "README.md", "LICENSE.md"]))

w = max(len(n) for n, _, _ in R)
for n, c, d in R:
    print(f"{'✓' if c else '✘'} {n:<{w}}  {'' if c else d}")
bad = [n for n, c, _ in R if not c]
print(f"தனிச் செயலிச் சரிபார்ப்பு: {len(R) - len(bad)}/{len(R)}")
if bad:
    sys.exit(1)

# ── zip (களஞ்சியமாகப் பதிவேற்றத் தயார்)
z = ROOT / f"build/senthamil-aakkam-{VERSION}.zip"
with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            zf.write(p, "senthamil-aakkam/" + str(p.relative_to(OUT)))
print(z.relative_to(ROOT), f"{z.stat().st_size // 1024} KB")
