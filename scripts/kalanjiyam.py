"""களஞ்சியச் சரிபார்ப்பு — docs/THOGUPPU.md §2.6. python3 scripts/kalanjiyam.py (தோல்வியெனில் வெளியேறும் குறி 1)"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "github.com/thanu2008v-prog/senthamil-marabu"
DOI = "10.5281/zenodo.24011590"
ORCID = "0009-0005-4309-7476"
FOOT = "தமிழுக்கும்"  # பழைய வரி — இருக்கக் கூடாது
FOOTER = "உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; தொழில்நுட்ப உதவி: Claude (Anthropic)"
R = []


def ok(name, cond, detail=""):
    R.append((name, bool(cond), detail))


T = lambda p: (ROOT / p).read_text("utf-8")

# 1. தேவையான கோப்புகள்
REQ = ["README.md", "LICENSE.md", "CITATION.cff", ".zenodo.json", "CHANGES.md", "CONTRIBUTING.md", "pyproject.toml",
       "requirements.txt", "Makefile", ".gitignore", ".gitattributes", "datapackage.json", "docs/TARAVU.md", "docs/DATA_CARD.md",
       "docs/THOGUPPU.md", "schema/sutra.v2.schema.json", ".github/workflows/validate.yml", ".github/workflows/pages.yml",
       ".github/workflows/release.yml", "senthamil_marabu/data/sutras.jsonl", "karuvi/noolvazhi.html", "karuvi/aakkam.html",
       "app/aakkam/index.html", "app/aakkam/manifest.webmanifest", "app/aakkam/sw.js", "scripts/build_site.py"]
missing = [p for p in REQ if not (ROOT / p).exists()]
ok("1. தேவையான கோப்புகள்", not missing, ", ".join(missing))

# 2. பதிப்பு, DOI, ORCID, முகவரி, உரிமம்
sys.path.insert(0, str(ROOT))
import senthamil_marabu as sm  # noqa: E402
zen = json.loads(T(".zenodo.json"))
vers = {"pyproject": re.search(r'^version = "([^"]+)"', T("pyproject.toml"), re.M).group(1),
        "தொகுப்பு": sm.__version__,
        "CITATION": re.search(r'^version: "([^"]+)"', T("CITATION.cff"), re.M).group(1),
        ".zenodo": zen.get("version"),
        "CHANGES": re.search(r"^## v([\d.]+)", T("CHANGES.md"), re.M).group(1)}
ok("2அ. பதிப்பு எண் ஒன்றே", len(set(vers.values())) == 1, str(vers))
ok("2ஆ. DOI", all(DOI in T(p) for p in ["README.md", "CITATION.cff", "senthamil_marabu/__init__.py", "docs/TARAVU.md", "LICENSE.md"]))
ok("2இ. ORCID", ORCID in T("CITATION.cff") and ORCID in zen["creators"][0]["orcid"] and ORCID in T("README.md"))
ok("2ஈ. களஞ்சிய முகவரி", all(REPO in T(p) for p in ["CITATION.cff", "pyproject.toml", "README.md"]) and REPO in json.dumps(zen))
lic = {"pyproject": "CC-BY-NC-4.0" in T("pyproject.toml"), "CITATION": "CC-BY-NC-4.0" in T("CITATION.cff"),
       ".zenodo": zen.get("license") == "cc-by-nc-4.0", "LICENSE": "CC BY-NC 4.0" in T("LICENSE.md"),
       "README": "CC BY-NC 4.0" in T("README.md"), "datapackage": "CC-BY-NC-4.0" in T("datapackage.json")}
ok("2உ. உரிமம் ஒன்றே", all(lic.values()), str({k: v for k, v in lic.items() if not v}))

# 3. களஞ்சியத்தில் இருக்கக் கூடாதவை
tracked = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout.split("\n")
junk = [f for f in tracked if re.search(r"(__pycache__|\.pyc$|\.egg-info|\.pytest_cache|node_modules|^build/|^export/|\.DS_Store)", f)]
ok("3. தேவையற்ற கோப்பு இல்லை", not junk, ", ".join(junk[:5]))

# 4. கருவிகள் ஒரே விதி நிரலிலிருந்து
logic_core = T("karuvi/logic.js").split("if (typeof module")[0]
ok("4. கருவிகளில் ஒரே விதி நிரல்", all(logic_core in T(p) for p in ["karuvi/noolvazhi.html", "karuvi/aakkam.html", "app/aakkam/index.html"]),
   "python3 karuvi/build.py இயக்குக")

# 5. தனிச் செயலி
man = json.loads(T("app/aakkam/manifest.webmanifest"))
icons_ok = True
try:
    from PIL import Image
    for ic in man["icons"]:
        w, h = map(int, ic["sizes"].split("x"))
        icons_ok &= Image.open(ROOT / "app/aakkam" / ic["src"]).size == (w, h)
except ImportError:
    icons_ok = all((ROOT / "app/aakkam" / ic["src"]).exists() for ic in man["icons"])
sw_files = json.loads(re.search(r"const FILES = (\[.*?\]);", T("app/aakkam/sw.js")).group(1))
ok("5அ. manifest", man.get("display") == "standalone" and man.get("start_url") and any(i.get("purpose") == "maskable" for i in man["icons"]) and icons_ok)
ok("5ஆ. service worker கோப்புகள்", all(f == "./" or (ROOT / "app/aakkam" / f).exists() for f in sw_files))
ok("5இ. இணையமின்றி எழுத்துரு", 'src: url("fonts/' in T("app/aakkam/index.html") and "fonts.googleapis" not in T("app/aakkam/index.html"))

# 6. நூலில் ஆங்கிலம் இல்லை
ALLOW = {"Project", "Madurai", "projectmadurai", "org", "Creative", "Commons", "Attribution", "NonCommercial", "International", "CC", "BY", "NC",
         "DOI", "Zenodo", "ORCID", "Claude", "Anthropic", "https", "creativecommons", "licenses", "by-nc", "BY-NC", "zenodo", "SIL", "Open", "Font", "License", "Noto"}
book = ""
if (ROOT / "build/senthamil_marabu.md").exists():
    book = T("build/senthamil_marabu.md")
book += T("sources/munnurai.md").split("## படலம் 1")[0]
eng = sorted({w for w in re.findall(r"[A-Za-z][A-Za-z\-]+", book) if w not in ALLOW})
ok("6. நூலில் ஆங்கிலம் இல்லை", not eng, ", ".join(eng[:10]))

# 7. உரிமை வரி
places = ["README.md", "karuvi/noolvazhi.html", "karuvi/aakkam.html", "app/aakkam/index.html", "scripts/build_book.py", "LICENSE.md"]
ok("7. உரிமை வரி", all(FOOTER in T(p) for p in places) and not any(FOOT in T(p) for p in places), str([p for p in places if FOOTER not in T(p)]))

w = max(len(n) for n, _, _ in R)
for n, c, d in R:
    print(f"{'✓' if c else '✘'} {n:<{w}}  {'' if c else d}")
bad = [n for n, c, _ in R if not c]
print(f"களஞ்சியச் சரிபார்ப்பு: {len(R) - len(bad)}/{len(R)}")
sys.exit(1 if bad else 0)
