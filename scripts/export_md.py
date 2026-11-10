"""எல்லாப் பகுதிகளும் தனித்தனி md கோப்பாக → build/thani_md/ (+ build/senthamil-marabu-md.zip).

மூலம் docs/THOGUPPU.md ஒன்றே (திருத்தம் அங்கே); இந்நிரல் ஒவ்வொரு பகுதியையும் தனிக் கோப்பாக எடுக்கிறது.
கூடவே: நூல் மூலம் 1602 (md), பிற மொழி மாதிரி நெறி (md), உள்ளடக்க அட்டவணை (00_PATTIYAL.md)."""
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
import senthamil_marabu as sm                                        # noqa: E402
from thoguppu import KOPPU, edu                                      # noqa: E402

OUT = ROOT / "build" / "thani_md"
ZIP = ROOT / "build" / "senthamil-marabu-md.zip"
FOOT = "© 2026 தனுசாந்தன் வர்ணகுலசிங்கம் — உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; தொழில்நுட்ப உதவி: Claude (Anthropic)."
PAD = {"ezhuthu": "எழு.", "sol": "சொல்.", "porul": "பொருள்."}

if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

text = KOPPU.read_text("utf-8")
keys = re.findall(r"<!-- பகுதி:([a-z_]+) -->", text)
rows = []
for i, k in enumerate(keys, 1):
    body = edu(k).strip("\n")
    m = re.search(r"^# (?:\d+\. )?(.+)$", body, re.M)
    title = m.group(1).strip() if m else k
    body = re.sub(r"^# \d+\. ", "# ", body, count=1, flags=re.M)
    name = f"{i:02d}_{k}.md"
    (OUT / name).write_text(body.rstrip() + f"\n\n---\n\n{FOOT}\n", "utf-8")
    rows.append((name, title))

# நூல் மூலம் — md வடிவில்
NAMES = __import__("json").loads((ROOT / "sources/othu_names.json").read_text("utf-8"))
nl = ["# செந்தமிழ் மரபு — 1602 நூற்பா (மூலம்)", "",
      "எழுத்ததிகாரம் 483 · சொல்லதிகாரம் 463 · பொருளதிகாரம் 656. மூலம் மாற்றக் கூடாது.", "",
      f"மேற்கோள்: Varnakulasingam, T. (2026). செந்தமிழ் மரபு. DOI {sm.DOI}. சூத்திரங்கள் பொதுவுடைமை. "
      "சொல், பொருள் அதிகாரங்களின் மின்பாடம் © Project Madurai — \"You are welcome to freely distribute this file, provided this header page is kept intact.\"", ""]
cur, n_s = None, 0
for r in sm.sutras():
    k = (r["padalam"], r["othu"])
    if k != cur:
        cur = k
        nl += [f"## {NAMES[r['padalam']]['_']} · ஓத்து {r['othu']} — {NAMES[r['padalam']][str(r['othu'])]}", ""]
    nl += [f"### {PAD[r['padalam']]} {r['sutra']}", "", "  \n".join(r["moolam"].split("\n")), ""]
    n_s += 1
assert n_s == 1602
nool = f"{len(keys) + 1:02d}_nool_1602.md"
(OUT / nool).write_text("\n".join(nl) + f"\n---\n\n{FOOT}\n", "utf-8")
rows.append((nool, "நூல் மூலம் — 1602 நூற்பா"))

# தருக்க வாய்பாடு — 1602 முழுவதும்
thk = ROOT / "pothu/tharukkam.jsonl"
if thk.exists():
    import json as _j
    T = [_j.loads(l) for l in open(thk, encoding="utf-8")]
    K2 = {"ezhu": "ezhuthu", "sol": "sol", "porul": "porul"}
    MO = {(r["padalam"], r["sutra"]): r["moolam"] for r in sm.sutras()}
    tl = ["# ஒவ்வொரு நூற்பாவும் ஒரு தருக்கம் — முழுப் பட்டியல் (1602)", "",
          "வாய்பாடு பொது வடிவத்திலிருந்து நிரலால் உருவானது (`pothu/tharukkam.jsonl`); குறியீட்டு விளக்கம் 24_tharukkam.md. "
          "∀ எல்லா · → எனின் · ∧ உம் · ¬ அன்று · □ கட்டாயம் · ◇ இசைவு · ≝ வரையறை · |…| எண்ணிக்கை · ⊔ பகுப்பு · ≔ மாட்டேறு · ⊢ புலவர் கூற்று.", "",
          "| நூற்பா | மூலம் | வகை | வாய்பாடு | நிலை |", "|---|---|---|---|---|"]
    for o in T:
        a, n = o["id"].split(".")
        m_ = MO[(K2[a], int(n))].replace("\n", " / ").replace("|", "\\|")
        tl.append(f"| {PAD[K2[a]]} {n} | {m_} | {o['vagai']} | {o['vaaipaadu'].replace('|', '\\|')} | {o['nilai']} |")
    assert len(T) == 1602
    thn = f"{len(rows) + 1:02d}_tharukkam_muzhu.md"
    (OUT / thn).write_text("\n".join(tl) + f"\n\n---\n\n{FOOT}\n", "utf-8")
    rows.append((thn, "தருக்க வாய்பாடு — 1602 முழுவதும்"))

# பிற மொழி மாதிரி நெறி
neri_src = ROOT / "build/llm_kit/SENTHAMIL_MARABU_NERI.md"
if neri_src.exists():
    neri = f"{len(rows) + 1:02d}_llm_neri.md"
    shutil.copy(neri_src, OUT / neri)
    rows.append((neri, "பிற மொழி மாதிரிகளுக்கான நெறி (முழு)"))

# பட்டியல்
pl = ["# செந்தமிழ் மரபு — கோப்புப் பட்டியல்", "",
      "ஒவ்வொரு பகுதியும் தனி md கோப்பு. மூலம்: `docs/THOGUPPU.md` (திருத்தம் அங்கே மட்டும்); இக்கோப்புகளை `python3 scripts/export_md.py` மீண்டும் உருவாக்கும்.", "",
      "| கோப்பு | தலைப்பு |", "|---|---|"]
pl += [f"| [{n}]({n}) | {t} |" for n, t in rows]
(OUT / "00_PATTIYAL.md").write_text("\n".join(pl) + f"\n\n---\n\n{FOOT}\n", "utf-8")

# சரிபார்ப்பு: ஒவ்வொரு பகுதியின் உரையும் THOGUPPU-வில் உள்ளதோடு ஒக்க வேண்டும் (தலைப்பு எண் தவிர)
for i, k in enumerate(keys, 1):
    got = (OUT / f"{i:02d}_{k}.md").read_text("utf-8")
    want = re.sub(r"^# \d+\. ", "# ", edu(k).strip("\n"), count=1, flags=re.M)
    assert got.startswith(want.rstrip()), k
    assert FOOT in got

if ZIP.exists():
    ZIP.unlink()
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
    for p in sorted(OUT.iterdir()):
        z.write(p, f"senthamil-marabu-md/{p.name}")
print(f"தனி md: {len(list(OUT.iterdir()))} கோப்பு → {OUT.relative_to(ROOT)}; zip {ZIP.stat().st_size // 1024} KB")
