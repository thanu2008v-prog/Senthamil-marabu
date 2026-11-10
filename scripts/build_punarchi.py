"""புணர்ச்சிப் பொறி — ஏற்றுமதியும் சரிபார்ப்பும்.
python3 scripts/build_punarchi.py →
  punarchi/pori/NN_<id>.att  — ஒவ்வொரு விதியும் AT&T உருமாற்றுப் பொறி (foma «read att», HFST «hfst-txt2fst», OpenFst «fstcompile» ஏற்பன)
  punarchi/PORI.json         — தொடுப்பு வரிசை, சூத்திரம், நிலை, எழுத்துத் தொகுதி
  docs/THOGUPPU.md §8         — எழு. 103–483 ஒவ்வொன்றும்: பொறியில் / தனிச்சொல் / இன்னும் இல்லை
சரிபார்ப்பு: ஏற்றுமதியான .att கோப்புகளை pyfoma இன்றித் தனியே இயக்கி, pyfoma விளைவோடு ஒப்பிடுகிறது."""
import json, re, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import senthamil_marabu as sm                                   # noqa: E402
from senthamil_marabu import punarchi as P                      # noqa: E402
from pyfoma import FST                                          # noqa: E402

OUT = ROOT / "punarchi"
(OUT / "pori").mkdir(parents=True, exist_ok=True)
for old in (OUT / "pori").glob("*.att"):
    old.unlink()

# மூடிய எழுத்துத் தொகுதி — «வேறு எழுத்து» (.) இல்லாமல், எக்கருவியிலும் ஒரே பொருள் தர
ALPHA = sorted(set("pmsSvt+=") | set(P.UYIR) | set(P.MEY) | {P.P, "ஃ", P.KU})
SIG = "(" + "|".join("\\" + a if a in "+=" else a for a in ALPHA) + ")"


def closed(f):
    g = FST.re(f"{SIG}* @ $f @ {SIG}*", {"f": f})
    return g.trim() if hasattr(g, "trim") else g


def att(f):
    """pyfoma FST → AT&T உரை (நிலை 0 தொடக்கம்; வெறுமை @0@). நிலை எண் — தொடக்கத்திலிருந்து அகல முதல் தேடல், குறி வரிசைப்படி:
    ஒரே பொறிக்கு எப்போதும் ஒரே கோப்பு (git-இல் வீண் மாற்றம் இல்லை)."""
    def sig(s):
        return (s in f.finalstates, tuple(sorted(str(l) for l in s.transitions)))
    ids, order, queue = {f.initialstate: 0}, [f.initialstate], [f.initialstate]
    while queue:
        s = queue.pop(0)
        for label in sorted(s.transitions, key=str):
            for tg in sorted((t.targetstate for t in s.transitions[label]), key=sig):
                if tg not in ids:
                    ids[tg] = len(ids); order.append(tg); queue.append(tg)
    for s in f.states:                                          # அடையா நிலைகள் (இருந்தால்)
        if s not in ids:
            ids[s] = len(ids); order.append(s)
    lines = []
    for s in order:
        for label, trs in s.transitions.items():
            i, o = (label[0], label[0]) if len(label) == 1 else label
            assert i != "." and o != ".", "மூடாத எழுத்துத் தொகுதி"
            for t in trs:
                lines.append(f"{ids[s]}\t{ids[t.targetstate]}\t{i or '@0@'}\t{o or '@0@'}")
    for s in order:
        if s in f.finalstates:
            lines.append(str(ids[s]))
    fin = [l for l in lines if "\t" not in l]
    return "\n".join(sorted((l for l in lines if "\t" in l), key=lambda l: (int(l.split("\t")[0]), l)) + sorted(fin, key=int)) + "\n"


# ── ஏற்றுமதி
import shutil  # noqa: E402
shutil.copy(OUT / "THANI.json", ROOT / "senthamil_marabu/data/punarchi_thani.json")
manifest = []
for n, r in enumerate(P.RULES):
    g = closed(P._fst(n))
    name = f"{n:02d}_{r['id']}.att"
    (OUT / "pori" / name).write_text(att(g), "utf-8")
    manifest.append(dict(varisai=n, id=r["id"], kopu="pori/" + name, sutra=r["sutra"], nilai=P.NILAI[r["nilai"]],
                         kattayam=r["kattayam"], vilakkam=r["vilakkam"]))
(OUT / "PORI.json").write_text(json.dumps({
    "vilakkam": "புணர்ச்சி விதிகள் — வரிசைப்படி தொடுக்க (composition). உள்ளீடு ஒலி வரிசை: <இனக்குறி><நிலைமொழி><சந்தி><வருமொழி>.",
    "inakkuri": {v: k for k, v in P.INAMKURI.items()}, "santhi": {v: k for k, v in P.VAGAI.items()},
    "ezhuthukal": ALPHA, "kutriyalukaram_kuri": P.KU, "vetrumai": "@0@", "kairegai": P._kairegai(),
    "vithigal": manifest}, ensure_ascii=False, indent=1), "utf-8")


# தொகுப்புக்குள் நகல் — இயக்க நேரத்தில் pyfoma தேவையில்லை (senthamil_marabu.punarchi._att)
DP = ROOT / "senthamil_marabu/data/pori"
if DP.exists():
    shutil.rmtree(DP)
DP.mkdir(parents=True)
for m_ in manifest:
    shutil.copy(OUT / m_["kopu"], DP / Path(m_["kopu"]).name)
shutil.copy(OUT / "PORI.json", DP / "PORI.json")
P._att.cache_clear()

# ── தனி இயக்கி: .att கோப்புகளை மட்டும் கொண்டு (pyfoma இன்றி)
def load_att(path):
    T, F = defaultdict(list), set()
    for ln in path.read_text("utf-8").splitlines():
        p = ln.split("\t")
        if len(p) == 1:
            F.add(int(p[0]))
        else:
            T[int(p[0])].append((int(p[1]), "" if p[2] == "@0@" else p[2], "" if p[3] == "@0@" else p[3]))
    return T, F


def run(fst, s):
    T, F = fst
    out, stack, seen = set(), [(0, 0, "")], set()
    while stack:
        q, i, o = stack.pop()
        if (q, i, o) in seen or len(o) > 3 * len(s) + 20:
            continue
        seen.add((q, i, o))
        if i == len(s) and q in F:
            out.add(o)
        for t, a, b in T[q]:
            if a == "":
                stack.append((t, i, o + b))
            elif i < len(s) and s[i] == a:
                stack.append((t, i + 1, o + b))
    return out


PORI = [load_att(OUT / m["kopu"]) for m in manifest]


def cascade(s):
    forms = {s}
    for f in PORI:
        forms = {y for x in forms for y in run(f, x)}
    return forms


sys.path.insert(0, str(ROOT / "tests")); from test_punarchi import NOOL  # noqa: E402
from senthamil_marabu.ezhuthu import words as words_  # noqa: E402
cases = [(a, b, v, i) for a, b, v, i, *_ in NOOL]
words = sorted({w["s"] for r in sm.sutras() if r["padalam"] == "ezhuthu" for w in words_(r["moolam"])})
import random                                                    # noqa: E402
rnd = random.Random(483)
for _ in range(300):
    cases.append((rnd.choice(words), rnd.choice(words), rnd.choice(list(P.VAGAI)), rnd.choice(list(P.INAMKURI))))
bad = 0
for a, b, v, i in cases:
    s = P.INAMKURI[i] + P.to_oli(a) + P.VAGAI[v] + P.to_oli(b)
    want = set()
    forms = {s}
    for n in range(len(P.RULES)):
        forms = {g for f in forms for g in P._fst(n).generate(f)}     # pyfoma நேரடியாக — .att இயக்கியோடு ஒப்பிட
    if forms != cascade(s):
        bad += 1
        print("✘", a, b, v, i, sorted(forms), sorted(cascade(s)))
print(f"ஏற்றுமதிச் சரிபார்ப்பு: {len(cases) - bad}/{len(cases)} ஒத்தன ({len(P.RULES)} பொறி)")

# ── விரிவு: எழு. 103–483
THANI = P.thani()
in_pori = defaultdict(list)
for r in P.RULES:
    for s in r["sutra"]:
        in_pori[s].append(r["id"])
in_thani = defaultdict(list)
for w, d in THANI.items():
    for s in d["sutra"]:
        in_thani[s].append(w)
import re as _re                                                    # noqa: E402
NIRAL = {}
for name, path in [("தனிச்சொல் விதி", "senthamil_marabu/thanisol.py"), ("உருபு", "senthamil_marabu/urupu.py"),
                   ("எண்ணுப்பெயர்", "senthamil_marabu/en.py")]:
    for n in _re.findall(r"எழு\. (\d+)", (ROOT / path).read_text("utf-8")):
        NIRAL.setdefault(f"எழு. {n}", name)
rows, count = [], defaultdict(int)
for r in sm.sutras():
    if r["padalam"] != "ezhuthu" or not 103 <= r["sutra"] <= 483:
        continue
    k = f"எழு. {r['sutra']}"
    if k in in_pori:
        st, c = "பொறியில் (" + ", ".join(in_pori[k]) + ")", "பொறி"
    elif k in NIRAL:
        st, c = NIRAL[k] + " நிரலில்", "நிரல்"
    elif k in in_thani:
        st, c = "தனிச்சொல் — சுட்டு மட்டும்: " + ", ".join(in_thani[k][:6]), "சுட்டு"
    else:
        st, c = "இன்னும் இல்லை", "இல்லை"
    count[c] += 1
    rows.append(f"| {r['sutra']} | {r['moolam'].splitlines()[0]} | {st} |")
head = (f"# புணர்ச்சிப் பொறி — விரிவு (எழு. 103–483)\n\nஉருமாற்றுப் பொறியில்: {count['பொறி']} · "
        f"பிற நிரலில் (தனிச்சொல் விதி, உருபு, எண்ணுப்பெயர்): {count['நிரல்']} · தனிச்சொல் — சுட்டு மட்டும்: {count['சுட்டு']} · "
        f"இன்னும் இல்லை: {count['இல்லை']}\n\n"
        "«இன்னும் இல்லை» என்பவை பெரும்பாலும் வரையறை, செய்யுள் விதி, புறனடை.\n\n"
        "| சூத்திரம் | முதலடி | நிலை |\n|---|---|---|\n")
sys.path.insert(0, str(ROOT / "scripts"))
from thoguppu import ezhuthu as _ezhuthu  # noqa: E402
_ezhuthu("punarchi_virivu", head + "\n".join(rows))
print("விரிவு:", dict(count))
sys.exit(1 if bad else 0)
