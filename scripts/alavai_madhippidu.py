"""நூல்வழி அளவை — மதிப்பிடல்.
1) கேள்வித் தூண்டல்: python3 scripts/alavai_madhippidu.py thoondal [--paguppu தேர்வு] > prompts.jsonl
   ஒவ்வொரு வரியும் {id, prompt}. எந்த AI மாதிரியிலும் இயக்கி {id, vidai} என விடைக் கோப்பு ஆக்குக.
2) மதிப்பெண்: python3 scripts/alavai_madhippidu.py madhippu vidaigal.jsonl [--paguppu தேர்வு]
   பணிவகை வாரியாகச் சரி விழுக்காடு, தற்செயல் அடிப்படை, மொத்தம் (பணிவகைச் சராசரி)."""
import json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROWS = [json.loads(l) for l in (ROOT / "alavai/alavai.jsonl").open(encoding="utf-8")][1:]
NERI = ("கீழ்வரும் கேள்விக்கு «செந்தமிழ் மரபு» (தொல்காப்பிய நூற்பாக்கள்) மட்டுமே அளவுகோல். "
        "தரப்பட்ட தேர்வுகளுள் ஒன்றை மட்டும், அதே எழுத்தில், விடையாக எழுதுக; விளக்கம் வேண்டாம்.")


def prompt(r):
    th = "\n".join(f"- {t}" for t in r["thervugal"])
    return f"{NERI}\n\n{r['kelvi']}\n\nதேர்வுகள்:\n{th}\n\nவிடை:"


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


pg = arg("--paguppu")
rows = [r for r in ROWS if not pg or r["paguppu"] == pg]
if len(sys.argv) > 1 and sys.argv[1] == "thoondal":
    for r in rows:
        print(json.dumps({"id": r["id"], "prompt": prompt(r)}, ensure_ascii=False))
elif len(sys.argv) > 2 and sys.argv[1] == "madhippu":
    pred = {}
    for l in open(sys.argv[2], encoding="utf-8"):
        if l.strip():
            p = json.loads(l); pred[p["id"]] = str(p.get("vidai", "")).strip().strip("«»\"'.")
    S = defaultdict(lambda: [0, 0, 0.0])
    for r in rows:
        s = S[r["vagai"]]
        s[0] += pred.get(r["id"]) == r["vidai"]; s[1] += 1; s[2] += 1 / len(r["thervugal"])
    print(f"{'பணிவகை':<14} {'சரி':>6} {'மொத்தம்':>7} {'விழுக்காடு':>10} {'தற்செயல்':>9}")
    for v, (c, n, b) in sorted(S.items()):
        print(f"{v:<14} {c:>6} {n:>7} {100 * c / n:>9.1f}% {100 * b / n:>8.1f}%")
    print(f"பணிவகைச் சராசரி: {sum(100 * c / n for c, n, _ in S.values()) / len(S):.1f}%   "
          f"(விடை இல்லாதவை: {sum(1 for r in rows if r['id'] not in pred)})")
else:
    print(__doc__)
