"""ஆய்வுக்கான எடுத்துக்காட்டுகள் — senthamil_marabu தொகுப்பைக் கொண்டு. python3 examples/aayvu_eduthukkaattu.py"""
import collections, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # நிறுவாமல் களஞ்சியத்திலிருந்தே இயக்க
import senthamil_marabu as sm
from senthamil_marabu import ilakkanam, yappu, kuri

R = sm.sutras()

# 1. அதிகார வாரியாகத் துணிவு நிலை — நூல் தீர்க்காதவை எங்கே அதிகம்?
print("1. அதிகார வாரியாக நிலை")
t = collections.Counter((r["padalam"], r["nilai"]) for r in R)
for p in sm.PADALAM:
    n = sum(v for (a, _), v in t.items() if a == p)
    print(f"   {sm.PADALAM[p]:6} " + "  ".join(f"{k}: {t[(p, k)]} ({100 * t[(p, k)] / n:.1f}%)" for k in sm.NILAI))

# 2. ஒவ்வோர் அதிகாரத்தின் மாத்திரைக் கூட்டு — குறியாக்கத்திலிருந்தே (எழு. 3, 4, 11, 12)
print("2. மாத்திரை")
for p in sm.PADALAM:
    total = sum(kuri.maathirai(c) for r in sm.by_padalam(p) for c in kuri.encode(r["moolam"]) if kuri.is_ezhuthu(c))
    print(f"   {sm.PADALAM[p]:6} {total}")

# 3. பிறரால் அதிகம் சுட்டப்படும் சூத்திரங்கள் — நூலுள் மைய விதிகள்
print("3. அதிகம் சுட்டப்படுவன")
cites = collections.Counter(x for r in R for x in (r.get("urai") or {}).get("iyaipu", []))
for sid, n in cites.most_common(5):
    print(f"   {sid:10} {n:3}  {sm.get(sid)['moolam'].splitlines()[0]}")

# 4. உத்திகள் அதிகாரம் வாரியாக
print("4. உத்தி (சொல் அடையாளம்)")
u = collections.Counter((r["padalam"], x["peyar"]) for r in R for x in r.get("utthi", []))
for name in ["தொகுத்துக் கூறல்", "ஒருதலை அன்மை", "ஆணை கூறல்", "பிறன் உடன்பட்டது தான் உடம்படுதல்"]:
    print(f"   {name:34} " + "  ".join(f"{sm.PADALAM[p]} {u[(p, name)]}" for p in sm.PADALAM))

# 5. ஓர் உரையை இலக்கணச் சரிபார்ப்பால், ஒரு பாடலை யாப்பால்
print("5. சரிபார்ப்பு")
for f in ilakkanam.check("ரவி நேற்று பஸ்ஸில் ஊருக்குச் சென்றான்")["findings"]:
    print(f"   {f['word']:10} {f['rule']:10} {f['nilai']:8} {f['msg']}")
for l in yappu.check("யாயும் ஞாயும் யாரா கியரோ\nஎந்தையும் நுந்தையும் எம்முறைக் கேளிர்")["lines"]:
    print(f"   {l['line']}  →  {l['ezhuthu']} எழுத்து, {l['vagai']} ({l['vref']}); " + " ".join("-".join(a["peyar"] for a in s["asai"]) for s in l["seer"]))

# 6. pandas இருந்தால்: அட்டவணையாக
try:
    df = sm.to_dataframe()
    print("6. DataFrame", df.shape)
    print(df.groupby("padalam")["kaandigai_porul"].apply(lambda s: s.str.len().mean()).round(0).to_string())
except ImportError:
    print("6. pandas நிறுவப்படவில்லை")
