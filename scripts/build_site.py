"""GitHub Pages தளம்: build/site/ — முகப்பு, தேடல் (thedal/), நூல்வழிச் சோதனை (sothanai/), செந்தமிழ் ஆக்கம் (aakkam/, தனிச் செயலி).
முன் தேவை: make check (build/bundle_v2.json), python3 karuvi/build.py. python3 scripts/build_site.py"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build/site"
shutil.rmtree(OUT, ignore_errors=True)
OUT.mkdir(parents=True)
DOC = ('<!doctype html>\n<html lang="ta">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}[hidden]{display:none!important}</style>\n'
       '</head>\n<body>\n{body}\n</body>\n</html>\n')

# தேடல் — செயலி
(OUT / "thedal/app").mkdir(parents=True)
idx = (ROOT / "index.html").read_text("utf-8").replace("./build/bundle_v2.json", "./bundle_v2.json")
(OUT / "thedal/index.html").write_text(idx, "utf-8")
shutil.copy(ROOT / "app/app.js", OUT / "thedal/app/app.js")
shutil.copy(ROOT / "build/bundle_v2.json", OUT / "thedal/bundle_v2.json")

# நூல்வழிச் சோதனை
(OUT / "sothanai").mkdir()
(OUT / "sothanai/index.html").write_text(DOC.replace("{body}", (ROOT / "karuvi/noolvazhi.html").read_text("utf-8")), "utf-8")

# செந்தமிழ் ஆக்கம் — தனிச் செயலி
shutil.copytree(ROOT / "app/aakkam", OUT / "aakkam")

# செந்தமிழ் — ஒருங்கிணைந்த AI / ஆக்கம் PWA
shutil.copytree(ROOT / "app/senthamil", OUT / "senthamil")
(OUT / "senthamil/app").mkdir()
shutil.copy(ROOT / "app/app.js", OUT / "senthamil/app/app.js")
shutil.copy(ROOT / "build/bundle_v2.json", OUT / "senthamil/bundle_v2.json")

# முகப்பு
home = """<title>செந்தமிழ் மரபு</title>
<style>
:root { --bg:#eef2ee; --surface:#fff; --ink:#16201b; --muted:#56655d; --line:#d3dbd5; --accent:#145c50 }
@media (prefers-color-scheme: dark) { :root { --bg:#0e1411; --surface:#16201b; --ink:#e1eae4; --muted:#95a59c; --line:#29352f; --accent:#5cc3ad; color-scheme: dark } }
body { background:var(--bg); color:var(--ink); font-family:"Noto Sans Tamil","Latha","Tamil Sangam MN",system-ui,sans-serif; line-height:1.6;
  padding-left:max(16px,env(safe-area-inset-left,0px)); padding-right:max(16px,env(safe-area-inset-right,0px)); padding-block:32px }
main { max-width:760px; margin:0 auto; display:grid; gap:18px }
h1 { font-family:"Noto Serif Tamil",serif; font-size:clamp(30px,6vw,44px); margin:0 }
p { margin:0; color:var(--muted) }
.cards { display:grid; gap:12px; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)) }
a.card { display:grid; gap:4px; background:var(--surface); border:1px solid var(--line); border-radius:10px; padding:16px; color:var(--ink); text-decoration:none }
a.card b { color:var(--accent); font-size:18px }
a.card:focus-visible { outline:2px solid var(--accent) }
small { color:var(--muted) }
</style>
<main>
  <h1>செந்தமிழ் மரபு</h1>
  <p>தொல்காப்பிய நூற்பாக்கள் 1602 — காண்டிகை, உரை, துணிவு; நூலின் சொந்த அளவுகோலால்.</p>
  <div class="cards">
    <a class="card" href="senthamil/"><b>செந்தமிழ் — AI மற்றும் ஆக்கம்</b><span>நூலில் ஆதாரம் தேடவும், ஆக்கம் உருவாக்கவும் ஒரே செயலியைத் திறக்க.</span></a>
    <a class="card" href="thedal/"><b>தேடல்</b><span>சூத்திரங்களை எண், சொல், நிலை, உத்தி வாரியாகத் தேடிப் படிக்க.</span></a>
    <a class="card" href="sothanai/"><b>நூல்வழிச் சோதனை</b><span>உரையின் இலக்கணத்தையும் பாடலின் யாப்பையும் நூற்பாக்களால் சோதிக்க.</span></a>
    <a class="card" href="aakkam/"><b>செந்தமிழ் ஆக்கம்</b><span>புதிய பாடலோ கட்டுரையோ உருவாக்க. தொலைபேசியில் «முகப்புத் திரையில் சேர்» வழி தனிச் செயலியாக நிறுவலாம்.</span></a>
    <a class="card" href="https://github.com/thanu2008v-prog/senthamil-marabu/releases/latest"><b>நூல் — PDF, மின்னூல்</b><span>அச்சு நூலும் மின்னூலும் கணினி வடிவத் தரவும்.</span></a>
  </div>
  <small>கருத்தாக்க DOI 10.5281/zenodo.24011590 · © 2026 தனுசாந்தன் வர்ணகுலசிங்கம் — உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; தொழில்நுட்ப உதவி: Claude (Anthropic).</small>
</main>"""
(OUT / "index.html").write_text(DOC.replace("{body}", home), "utf-8")
(OUT / ".nojekyll").write_text("")
print("build/site:", sorted(p.name for p in OUT.iterdir()))
