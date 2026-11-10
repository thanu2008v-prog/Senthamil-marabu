"""மாட்டேற்று வரைபடம் — கட்டம் 3 (docs/THOGUPPU.md §10.4). python3 scripts/build_maatteru.py → docs/THOGUPPU.md §14
«இன்ன இயற்றே», «அதனோ ரற்றே» — ஒரு நூற்பா இன்னொன்றின் இயல்பைப் பெறுவது. வட்டச் சுட்டு இருந்தால் தோல்வி."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import senthamil_marabu as sm                                       # noqa: E402

P = {json.loads(l)["id"]: json.loads(l) for l in (ROOT / "pothu/pothu.jsonl").open(encoding="utf-8")}
REF = {"ezhu": "எழு.", "sol": "சொல்.", "porul": "பொருள்."}
nm = lambda i: f"{REF[i.split('.')[0]]} {i.split('.')[1]}"
M = {i: r["maatteru"] for i, r in P.items() if r.get("maatteru")}
E = {i: m["suttu"][0] for i, m in M.items() if m["suttu"]}               # முதன்மைச் சுட்டு

# வட்டம்
cyc = []
for s in E:
    seen, c = set(), s
    while c in E:
        if c in seen:
            cyc.append(s); break
        seen.add(c); c = E[c]


def chain(s):
    out = [s]
    while out[-1] in E and E[out[-1]] not in out:
        out.append(E[out[-1]])
    return out


roots = Counter(chain(s)[-1] for s in E)
chains = sorted((chain(s) for s in E if s not in E.values()), key=len, reverse=True)
vz = Counter(m.get("vazhi", "—") for m in M.values())
VZ = {"காண்டிகை": "காண்டிகையில் நூற்பா எண் சுட்டப்பட்டது", "அண்மை": "«அற்றே», «அதனோ ரற்றே», «அன்ன இயல» — முந்தைய நூற்பா",
      "சொல் தேடல்": "«X இயற்றே» — X ஐ எழுவாயாகக் கொண்ட நூற்பா (எழுத்துப் பெயரெனில் அண்மை முந்தையது; சொல் வகையெனில் முதல் வருவது)",
      "பழைய புலம்": "பழைய கணினிப் புலத்தின் சுட்டு", "—": "தீர்க்கப்படவில்லை"}

L = ["# மாட்டேற்று வரைபடம்", "",
     "«ஆகார இறுதி அகர இயற்றே» (எழு. 221) — ஒரு நூற்பா தன் விதியைக் கூறாமல் இன்னொரு நூற்பாவின் இயல்பைப் பெறுகிறது. அவ்விணைப்புகள் இங்கே.", "",
     f"மாட்டேறு உள்ள நூற்பா: **{len(M)}** · சுட்டு கண்டவை: **{len(E)}** · வட்டச் சுட்டு: **{len(cyc)}**", "",
     "| எவ்வழிக் கண்டது | எண்ணிக்கை | பொருள் |", "|---|---|---|"] + [f"| {k} | {v} | {VZ[k]} |" for k, v in vz.most_common()] + [
     "", "«அண்மை», «சொல் தேடல்» இரண்டும் நூற்பாவின் சொல்லிலிருந்து நிரல் கண்டவை; ஒவ்வொன்றும் `pothu.jsonl` இல் `maatteru.vazhi` ஆகக் குறிக்கப்பட்டுள்ளது.", "",
     "## அடிப்படை நூற்பாக்கள் (மிகப் பல மாட்டேறு சென்றடைவது)", "", "| நூற்பா | முதலடி | சென்றடையும் மாட்டேறு |", "|---|---|---|"] + [
     f"| {nm(i)} | {sm.get(i)['moolam'].splitlines()[0]} | {n} |" for i, n in roots.most_common(12)] + [
     "", "## நீண்ட சங்கிலிகள்", ""] + [
     "- " + " → ".join(f"{nm(x)} «{' '.join(sm.get(x)['moolam'].split()[:3])}»" for x in c) for c in chains[:10] if len(c) > 2] + [
     "", "## உயிரீற்றுச் சங்கிலி (எழுத்ததிகாரம்)", "", "```mermaid", "graph RL"]
seen = set()
for s in ["ezhu.289", "ezhu.249", "ezhu.254", "ezhu.278"]:
    c = chain(s)
    for a, b in zip(c, c[1:]):
        if (a, b) not in seen:
            seen.add((a, b))
            L.append(f'  {a.replace(".", "_")}["{nm(a)} {" ".join(sm.get(a)["moolam"].split()[:2])}"] --> {b.replace(".", "_")}["{nm(b)} {" ".join(sm.get(b)["moolam"].split()[:2])}"]')
L += ["```", "", "## தீர்க்கப்படாதவை — நூற்பா அன்றிக் கருத்தைச் சுட்டுவன", "", "| நூற்பா | மூலம் | சுட்டும் கருத்து |", "|---|---|---|"] + [
     f"| {nm(i)} | {sm.get(i)['moolam'].replace(chr(10), ' / ')} | {m.get('karuthu', '')} |" for i, m in M.items() if not m["suttu"]] + [
     "", "இவற்றுள் «வேற்றுமை இயல» போன்றவை ஒரு நூற்பாவை அன்றிப் பொது முறையைச் சுட்டுகின்றன; «செந்தூக்கு», «நிரையசை» போன்றவை வரையறுக்கப்பட்ட இடம் "
     "எழுவாயாக வராததால் நிரல் காணவில்லை — ஆசிரியர் பார்வைக்கு.", "", "---", "",
     "© 2026 தனுசாந்தன் வர்ணகுலசிங்கம் — உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; தொழில்நுட்ப உதவி: Claude (Anthropic)."]
sys.path.insert(0, str(ROOT / "scripts"))
from thoguppu import ezhuthu as _ezhuthu  # noqa: E402
_ezhuthu("maatteru", "\n".join(L))
print(f"மாட்டேறு {len(M)}; சுட்டு {len(E)}; வட்டம் {len(cyc)}; அடிப்படை {len(roots)}")
sys.exit(1 if cyc else 0)
