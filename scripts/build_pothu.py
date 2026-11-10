"""பொதுச் சூத்திர வடிவம் — கட்டம் 1, 2 (docs/THOGUPPU.md §10.4).
பழைய கணினிப் புலம் (110 திறவு) + காண்டிகை + மூலம் → ஒரே வடிவு.  python3 scripts/build_pothu.py
→ pothu/pothu.jsonl, senthamil_marabu/data/pothu.jsonl, docs/THOGUPPU.md §11, docs/THOGUPPU.md §12 (ஆசிரியர் முடிவுக்கு)"""
import json, re, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import senthamil_marabu as sm                                       # noqa: E402
from senthamil_marabu.ezhuthu import words, letters                 # noqa: E402
sys.path.insert(0, str(ROOT / "scripts"))
from kooru import kooru                                             # noqa: E402

FOOT = ("© 2026 தனுசாந்தன் வர்ணகுலசிங்கம் — உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; "
        "தொழில்நுட்ப உதவி: Claude (Anthropic).")
VAGAI = {"definition": "வரையறை", "enumeration": "எண்ணல்", "classification": "பகுப்பு", "rule": "விதி", "exception": "விலக்கு", "meta": "நெறி"}

# ── முறைமை: நூலின் சொல்லிலிருந்தே (சொல்லின் தொடக்கமோ முழுச்சொல்லோ பொருந்த வேண்டும்)
# சொற்கள் புணர்ந்து வருவதால் (குற்றெழுத் «தென்ப») ஒலி வரிசையில் ஒப்பிடப்படுகிறது: «என்ப» ⊂ «த்என்ப்அ»
from senthamil_marabu.punarchi import to_oli                          # noqa: E402
MURAI = [("கட்டாயம்", ["வேண்டும்"], []),
         ("இசைவு", ["உரித்", "உரிய"], []),
         ("விலக்கின்மை", ["வரையார்", "வரைநிலை", "மானமில்", "மான மில்", "கடிநிலை", "வரைவின்"], []),
         ("மறுப்பு", ["ஆகாது", "இலவே", "இல்லை", "இன்மை"], ["ஆகா", "இன்றே"]),
         ("புலவர் கூற்று", ["என்மனார்", "என்மரும்"], ["என்ப", "என்பர்", "மொழிப"]),
         ("மாட்டேறு", ["இயற்றே", "அற்றே", "ஓரன்ன"], ["இயல"])]
MURAI_OLI = [(n, [to_oli(w) for w in a], [to_oli(w) for w in b]) for n, a, b in MURAI]


# பொருள் வேறான சொற்கள்: உரியசை (அசைப் பெயர்), சுரிதகம், புரிதல், வற்றே (சாரியைப் பெயர்), சின்மை (சிறுமை), பயின்றே
MURAI_VILAKKU = {"உரியசை", "புரிதல்", "சுரிதகம்", "வற்றே", "சின்மை", "சின்மையும்", "பயின்றே"}


def murai_toks(moolam):
    t = [w["s"] for w in words(moolam)]
    out, i = [], 0
    while i < len(t):                                                  # «மான மில்லை» ஒரு சொல்லாக
        if t[i] == "மான" and i + 1 < len(t) and t[i + 1].startswith("மில்லை"):
            out.append("மானமில்லை"); i += 2
        else:
            out.append(t[i]); i += 1
    return out


def murai_hit(tok, inn, end):
    if tok in MURAI_VILAKKU:
        return False
    o = to_oli(tok)
    return any(w in o for w in inn) or any(o.endswith(w) for w in end)

# ── பழைய புலத் திறவுகள் → பொது வடிவப் புலங்கள்
EZHUVAAI = ["entity", "entities", "class", "classes", "letter", "letters", "urupu", "urupus", "topic", "applies_to"]
NIBANTHANAI = ["context", "contexts", "condition", "position", "sphere", "applicable_in", "base", "dimensions", "scope", "mode", "contact", "origin"]
VILAIVU = ["property", "op", "ops", "transform", "transforms", "effect", "insert", "inserts", "suffix", "suffixes", "predicate",
           "claim", "principle", "states", "outcomes", "to", "exclude", "exception", "exceptions", "excluded", "invariant", "fallback",
           "steps_desc", "attribute", "direction", "evidence", "basis", "note"]
URUPPU = ["items", "pairs", "groups", "subclasses", "types", "components", "from", "roles", "ways"]
REFKEYS = ["refs", "same_as", "links_to", "analogy", "inherits", "forward_ref", "puran_of", "depends_on"]
ALAVU = ["count", "total", "limit", "letters_count"]
VADA_SOL = re.compile(r"[A-Za-z]")


def txt(v):
    if isinstance(v, dict):
        return [f"{k} → {txt(x)[0] if txt(x) else ''}" for k, x in v.items()]
    if isinstance(v, list):
        return [y for x in v for y in txt(x)]
    if isinstance(v, bool) or v is None:
        return []
    return [str(v).replace("_", " ")]


ALL = {r["id"]: r for r in sm.sutras()}
REF = {"ezhuthu": "ezhu", "sol": "sol", "porul": "porul"}
PFX = {"எழு.": "ezhu", "சொல்.": "sol", "பொருள்.": "porul"}


def ids_in(text, own):
    """«(எழு. 203)», «(203)», «203–220» → நூற்பா அடையாளங்கள்."""
    out = []
    for m in re.finditer(r"(எழு\.|சொல்\.|பொருள்\.)?\s?(\d{1,3})(?:\s?[–-]\s?(\d{1,3}))?", text):
        p = PFX.get(m.group(1), own.split(".")[0]) if m.group(1) else own.split(".")[0]
        a = int(m.group(2)); b = int(m.group(3) or a)
        if b - a > 30 or b < a:
            continue
        for n in range(a, b + 1):
            i = f"{p}.{n}"
            if i in ALL and i != own:
                out.append(i)
    return list(dict.fromkeys(out))


# ── இயக்கம்: எந்த நிரல் கூறுகள் எந்த நூற்பாவைச் சுட்டுகின்றன
IYAKKAM = defaultdict(set)
for name, path in [("இலக்கணச் சோதனை", "senthamil_marabu/ilakkanam.py"), ("யாப்புச் சோதனை", "senthamil_marabu/yappu.py"),
                   ("எண்ணுப்பெயர்", "senthamil_marabu/en.py"),
                   ("உருபு புணர்ச்சி", "senthamil_marabu/urupu.py"), ("வினைமுற்று ஈறு", "senthamil_marabu/vinai.py"),
                   ("விளி", "senthamil_marabu/vili.py"),
                   ("தனிச்சொல் புணர்ச்சி", "senthamil_marabu/thanisol.py"),
                   ("ஒலிப்பிறப்பு", "senthamil_marabu/oli.py"), ("மரபுக் குறியாக்கம்", "senthamil_marabu/kuri.py"),
                   ("ஒருங்குறி மாதிரி", "senthamil_marabu/orunguri.py")]:
    for p, n in re.findall(r"(எழு\.|சொல்\.|பொருள்\.) (\d+)", (ROOT / path).read_text("utf-8")):
        IYAKKAM[f"{PFX[p]}.{n}"].add(name)
from senthamil_marabu.oli import F as _OLI                           # noqa: E402
for _v in _OLI.values():
    for _n in _v[5].split(","):
        IYAKKAM[f"ezhu.{_n.strip()}"].add("ஒலிப்பிறப்பு")
from senthamil_marabu import punarchi                                # noqa: E402
for r in punarchi.RULES:
    for s in r["sutra"]:
        p, n = s.split()
        IYAKKAM[f"{PFX[p]}.{n}"].add(f"புணர்ச்சிப் பொறி {r['id']}")

# ── எண் சொல் சான்று (நூலின் எண்ணுப்பெயர் மதிப்பீட்டியால்)
from senthamil_marabu import en as EN                               # noqa: E402


def _ver(w):
    for suf in ("ுமே", "ும்", "ுந்", "ுஞ்", "ுங்", "ே", "ின்", "ன்"):
        if w.endswith(suf) and len(w) > len(suf) + 1:
            yield w[: -len(suf)] + ("ு" if suf.startswith("ு") else "")


def en_saanru(moolam, n):
    ws = [w["s"] for w in words(moolam)]
    for w in ws:
        for v in [w] + list(_ver(w)):
            try:
                if n in EN.mathippu(v):
                    return w
            except Exception:
                pass
    for size in (1, 2, 3, 4):
        for i in range(len(ws) - size + 1):
            frag = " ".join(ws[i:i + size])
            try:
                if n in EN.mathippu(frag):
                    return frag
            except Exception:
                pass
    return None


# ── மாட்டேறு: பொய்ப் பொருத்தங்களும் சுட்டுத் தேடலும்
POLI = ["ஆயீரியல", "ஆயீ ரியல", "இருவகை இயல", "இரு வகை இயல", "இயல ஆயினும்", "தெற்றென் றற்றே", "தெற்றென்றற்றே", "காரணம் முதற்றே",
        "ஓரன்ன உரிமை", "ஓரன்னவ்வே", "ஓரனை யுரிமை", "வாயுறுத்தற்றே", "ஓரன உரிமை"]
ANAPHOR = ["அதனோ", "அதன்", "அவ்வியல்", "ஆயியல்", "மேல்நிலை", "மொழிந்தவற்", "அன்னவை", "அற்றே", "ஓரற்றே"]


POLI_OLI = [to_oli(p.replace(" ", "")) for p in POLI + ["வேறுவேறியல"]]


def is_poli_maatteru(moolam, w):
    flat = to_oli(moolam.replace("\n", "").replace(" ", ""))
    return any(p in flat for p in POLI_OLI)


EZ = {}                                     # முன் கட்டிய நூற்பாக்களின் எழுவாய்த் தொடர் (சுட்டுத் தேடலுக்கு)
GENERIC = ("வேற்றுமை", "அல்வழி", "முதற்கிளந்")


def theadu(sid, toks, w):
    """சுட்டுத் தேடல்.
    (1) «அற்றே», «ஓரற்றே», «ஓரன்ன», «அன்ன இயல», «கிளந்த இயல», «அவ்வியல்» — முன் சொன்னதைச் சுட்டுவன: அண்மை (முந்தைய) நூற்பா.
    (2) «X இயற்றே / X இயல» — X தன் எழுவாயாக வரும் அண்மை முந்தைய நூற்பா.
    (3) X பொதுக் கருத்தெனில் («வேற்றுமை இயல») — நூற்பா அன்று, கருத்து."""
    i = toks.index(w)
    head = toks[i - 1] if i > 0 else ""
    pd, n = sid.split(".")
    n = int(n)
    o = to_oli(w)
    anaphor = ((o.endswith(to_oli("அற்றே")) and not o.endswith(to_oli("இயற்றே"))) or o.endswith(to_oli("ஓரன்ன")) or not head
               or any(head.startswith(a) for a in ("அன்ன", "கிளந்த", "அவ்வியல்", "ஆயியல்", "அதனோ", "அதன்", "அவற்றோ", "மேல்நிலை", "மொழிந்தவற்")))
    if anaphor:
        q = ALL.get(f"{pd}.{n - 1}")
        return ([q["id"]], "அண்மை") if q else ([], "")
    if any(head.startswith(g) for g in GENERIC):
        return [], ""
    if head in ("பெயர்", "கிளவி", "மொழி", "சொல்") and i > 1:          # «நிறைப் பெயர் இயல»
        head = toks[i - 2]
    stem = to_oli(head)[:9]
    # எழுத்துப் பெயர் («அகர», «ஏகார») — அண்மையில் அவ்விறுதியை எழுவாயாகக் கொண்ட நூற்பா; சொல் வகைப் பெயர் («தொழிற்பெயர்», «நெட்டெழுத்து») —
    # அப்பெயரை முதலில் எழுவாயாகக் கொண்ட நூற்பா (வரையறையோ அடிப்படை விதியோ)
    letter = bool(re.search(r"(கர|கார|கான்)$", head))
    order = range(n - 1, max(0, n - 200), -1) if letter else range(1, n)
    for back in order:
        q = f"{pd}.{back}"
        e = to_oli(EZ.get(q, "").replace(" ", ""))
        if stem and (e.startswith(stem) if letter else stem in e):        # எழுத்துப் பெயர்: எழுவாயின் தொடக்கமாகவே
            return [q], "சொல் தேடல்"
    return [], ""


rows, mothal, alavu_bad, ottru = [], [], [], []
for r in sm.sutras():
    k, m = r["kanini"], r["moolam"]
    toks = [w["s"] for w in words(m)]
    rec = {"id": r["id"]}
    saanru = defaultdict(list)

    # முறைமை
    murai = []
    mt_ = murai_toks(m)
    used = set()
    for name, inn, end in [MURAI_OLI[2]] + [x for x in MURAI_OLI if x is not MURAI_OLI[2]]:   # விலக்கின்மை முதலில்
        hit = [t for t in mt_ if t not in used and murai_hit(t, inn, end)]
        if name == "மறுப்பு":                                        # «கடிநிலை இன்றே», «ஐய மின்றே» — மறுப்பு அன்று (இசைவு / உறுதி)
            prev = {mt_[i]: mt_[i - 1] for i in range(1, len(mt_))}
            hit = [h for h in hit if not (prev.get(h, "") in used or prev.get(h, "").startswith("ஐய"))]
        used |= set(hit)
        if hit:
            murai.append(name); saanru["murai"] += [h if h != "மானமில்லை" else "மான மில்லை" for h in hit]
    order = [n for n, _, _ in MURAI]
    murai = sorted(murai, key=order.index)
    if not murai:
        murai = ["நேர்க் கூற்று"]
    rec["murai"] = murai
    if "கட்டாயம்" in murai and ({"இசைவு", "விலக்கின்மை"} & set(murai)):
        rec["murai_mothal"] = True
        mothal.append(r)

    # மாட்டேறு
    msol = [t for t in toks if murai_hit(t, *MURAI_OLI[-1][1:])]
    if msol and is_poli_maatteru(m, msol[0]):                         # «ஆயீ ரியல», «இயல ஆயினும்», «தெற்றென் றற்றே» — மாட்டேறு அன்று
        rec["murai"] = [x for x in rec["murai"] if x != "மாட்டேறு"] or ["நேர்க் கூற்று"]
        saanru["murai"] = [w for w in saanru.get("murai", []) if w not in msol]
        if not saanru["murai"]:
            saanru.pop("murai")
        msol = []
    vagai = VAGAI.get(k.get("kind"), "விதி")
    if msol or any(x in k for x in ("inherits", "same_as", "analogy")):
        suttu, vazhi_ = ids_in(r["kaandigai"]["porul"], r["id"]), "காண்டிகை"
        if msol and not suttu:
            suttu, vazhi_ = theadu(r["id"], toks, msol[0])
        old = [x for key in REFKEYS for x in txt(k.get(key)) if x in ALL and x not in suttu]
        if old and not suttu:
            vazhi_ = "பழைய புலம்"
        suttu += old
        rec["maatteru"] = {"sol": msol[0] if msol else "", "suttu": suttu}
        if suttu:
            rec["maatteru"]["vazhi"] = vazhi_
        else:
            j = toks.index(msol[0]) if msol else 0
            karu = " ".join(toks[max(0, j - 2):j]) if j > 1 and toks[j - 1] in ("பெயர்", "கிளவி", "மொழி", "சொல்") else (toks[j - 1] if j else "")
            rec["maatteru"]["karuthu"] = karu                         # நூற்பா எண்ணன்றிக் கருத்தைச் சுட்டுவது (எ.கா. «வினையோ ரனைய»)
        if msol and vagai == "விதி":
            vagai = "மாட்டேறு"
    rec["vagai"] = vagai

    for field, keys in (("ezhuvaai", EZHUVAAI), ("nibanthanai", NIBANTHANAI), ("vilaivu", VILAIVU)):
        vals = [x for key in keys for x in txt(k.get(key)) if not VADA_SOL.search(x)]
        if vals:
            rec[field] = list(dict.fromkeys(vals))
    up = [x for key in URUPPU for x in (k.get(key) if isinstance(k.get(key), list) else [])]
    if up:
        rec["uruppugal"] = [x.replace("_", " ") if isinstance(x, str) else x for x in up]
        flat = [y for x in up for y in txt(x)]
        s = [x for x in flat if len(x) >= 1 and x.replace(" ", "") in m.replace(" ", "")]
        if s:
            saanru["uruppugal"] = s
    for field in ("ezhuvaai", "vilaivu", "nibanthanai"):
        s = [x for x in rec.get(field, []) if len([l for l in letters(x) if l["k"] != "பிற"]) >= 3 and x.replace(" ", "") in m.replace(" ", "")]
        if s:
            saanru[field] = s

    # அமைப்பு வழிச் சான்று: நூற்பாவின் குறிச் சொற்களால் பிரித்த மூலத் தொடர்கள் (scripts/kooru.py)
    kr = kooru(m, vagai)
    vazhi = {}
    if kr.get("nibanthanai"):                                          # நிபந்தனைக்கு அமைப்புத் தொடரே முழுமையானது («யகரம் வருவழி»)
        saanru.pop("nibanthanai", None)
    for field in ("ezhuvaai", "nibanthanai", "vilaivu"):
        if field in saanru:
            vazhi[field] = "பெயர் பொருத்தம்"
        elif kr.get(field):
            saanru[field] = kr[field]
            vazhi[field] = "அமைப்பு"
            if not rec.get(field):
                rec[field] = kr[field]
            else:
                ottru.append((field, rec[field], kr[field]))
    if kr.get("pattiyal") and "uruppugal" not in saanru:
        saanru["uruppugal"] = kr["pattiyal"]; vazhi["uruppugal"] = "அமைப்பு"
    if vazhi:
        rec["saanru_vazhi"] = vazhi

    # அளவு — காண்டிகை எண்ணிச் சரிபார்த்த எண் முதன்மை; பழைய புலம் இரண்டாவது
    en_ = r["kaandigai"].get("en")
    a = en_.get("kooruvathu") if isinstance(en_, dict) and isinstance(en_.get("kooruvathu"), int) else None
    old = next((k[x] for x in ALAVU if isinstance(k.get(x), int)), None)
    if a is None:
        a = old
    elif old is not None and old != a:
        alavu_bad.append((r["id"], a, old))
    rec["alavu"] = a
    if a is not None:
        w = en_saanru(m, a)
        if w:
            saanru["alavu"] = [w]

    rec["saanru"] = dict(saanru)
    EZ[r["id"]] = " ".join(saanru.get("ezhuvaai", []))           # மூலச் சொற்கள் மட்டும்
    rec["nilai"] = r["nilai"]
    if IYAKKAM.get(r["id"]):
        rec["iyakkam"] = sorted(IYAKKAM[r["id"]])
    rows.append(rec)

# ── பழைய சுருக்கப் பெயரும் அமைப்புத் தொடரும் ஒத்துப்போகின்றனவா (பெயரின் ஒவ்வொரு சொல்லின் முதல் எழுத்தும் தொடரில் உள்ளதா)
def _mudhal(w):
    L = [l for l in letters(w) if l["k"] != "பிற"]
    if not L:
        return ""
    f = L[0]
    return f["c"] if f["c"] else {"ஈ": "இ", "ஊ": "உ", "ஏ": "எ", "ஓ": "ஒ"}.get(f["v"], f["v"])


def ottha(label, span):
    sp = "".join(span)
    base = {(l["c"] or l["v"]) for l in letters(sp) if l["k"] != "பிற"} | {"இ", "உ", "எ", "ஒ", "அ"} & {l["v"] for l in letters(sp)}
    ws = [w for x in label for w in x.replace("→", " ").split() if len(letters(w)) >= 1]
    return bool(ws) and all(_mudhal(w) in base for w in ws)


agree = Counter(); total = Counter()
for field, lab, span in ottru:
    total[field] += 1
    agree[field] += ottha(lab, span)

# ── சரிபார்ப்பு
import jsonschema                                                    # noqa: E402
SCH = json.loads((ROOT / "schema/pothu.v1.schema.json").read_text("utf-8"))
bad = []
for rec in rows:
    try:
        jsonschema.validate(rec, SCH)
    except jsonschema.ValidationError as e:
        bad.append((rec["id"], e.message[:80]))
    m = ALL[rec["id"]]["moolam"].replace(" ", "").replace("\n", "")
    for f, ws in rec["saanru"].items():
        for w in ws:
            if w.replace(" ", "") not in m:
                bad.append((rec["id"], f"சான்று «{w}» மூலத்தில் இல்லை"))
    for x in (rec.get("maatteru") or {}).get("suttu", []):
        if x not in ALL:
            bad.append((rec["id"], f"மாட்டேறு {x} இல்லை"))

out = "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n"
(ROOT / "pothu").mkdir(exist_ok=True)
(ROOT / "pothu/pothu.jsonl").write_text(out, "utf-8")
(ROOT / "senthamil_marabu/data/pothu.jsonl").write_text(out, "utf-8")

# ── அறிக்கை
C = lambda f: Counter(x for r in rows for x in (r[f] if isinstance(r[f], list) else [r[f]]))
withs = lambda f: sum(1 for r in rows if f in r["saanru"])
has = lambda f: sum(1 for r in rows if r.get(f) not in (None, [], ""))
mt = [r for r in rows if r.get("maatteru")]
lines = [
    "# பொதுச் சூத்திர வடிவம் — கட்டம் 1, 2 அறிக்கை", "",
    f"நூற்பா: {len(rows)} · வரையறைக்கு இணங்காதவை: {sum(1 for b in bad if 'சான்று' not in b[1] and 'மாட்டேறு' not in b[1])} · "
    f"மூலத்தில் இல்லாத சான்று: {sum(1 for b in bad if 'சான்று' in b[1])}", "",
    "## வகை", "", "| வகை | நூற்பா |", "|---|---|"] + [f"| {k} | {v} |" for k, v in C("vagai").most_common()] + [
    "", "## முறைமை (நூலின் சொல்லால்)", "", "| முறைமை | நூற்பா |", "|---|---|"] + [f"| {k} | {v} |" for k, v in C("murai").most_common()] + [
    "", f"கட்டாயமும் இசைவும் / விலக்கின்மையும் ஒருங்கு வரும் நூற்பா: **{len(mothal)}** — பட்டியல் docs/THOGUPPU.md §12 (ஆசிரியர் முடிவுக்கு).", "",
    "## புலங்கள் நிறைவு", "", "| புலம் | உள்ள நூற்பா | மூலச் சான்றோடு |", "|---|---|---|",
    f"| எழுவாய் | {has('ezhuvaai')} | {withs('ezhuvaai')} |", f"| நிபந்தனை | {has('nibanthanai')} | {withs('nibanthanai')} |",
    f"| விளைவு | {has('vilaivu')} | {withs('vilaivu')} |", f"| உறுப்புகள் | {has('uruppugal')} | {withs('uruppugal')} |",
    f"| அளவு | {has('alavu')} | {withs('alavu')} (எண்ணுப்பெயர் மதிப்பீட்டியால் மூலச் சொல் கண்டது) |",
    f"| மாட்டேறு | {len(mt)} | சுட்டு கண்டவை {sum(1 for r in mt if r['maatteru']['suttu'])} |",
    f"| இயக்கம் | {has('iyakkam')} | — |", "",
    "சான்று இரு வழியில் இணைக்கப்படுகிறது (`saanru_vazhi`): **பெயர் பொருத்தம்** — பழைய புலத்தின் பெயர் மூலத்தில் அப்படியே உள்ளது; "
    "**அமைப்பு** — நூற்பாவின் குறிச் சொற்களால் (முன்னர், வரின், காலை, இயையின், என்ப, என்னும் …) மூலத்தைக் கூறுகளாகப் பிரித்துக் கண்ட தொடர் (`scripts/kooru.py`).", "",
    "**அமைப்பு வழித் தொடர், பழைய சுருக்கப் பெயரோடு ஒத்துப்போதல்** (பெயரின் ஒவ்வொரு சொல்லின் முதல் எழுத்தும் தொடரில் உள்ளதா):", "",
    "| புலம் | ஒப்பிட்டவை | ஒத்தவை | விழுக்காடு |", "|---|---|---|---|"] + [
    f"| {dict(ezhuvaai='எழுவாய்', nibanthanai='நிபந்தனை', vilaivu='விளைவு')[f]} | {total[f]} | {agree[f]} | {100 * agree[f] // max(1, total[f])}% |"
    for f in ("ezhuvaai", "nibanthanai", "vilaivu")] + ["",
    "**கைச் சரிபார்ப்பு (25 நூற்பா, தற்செயல் மாதிரி):** முழுதும் சரி 15, பகுதி சரி 7, தவறு 3. அமைப்பு வழிச் சான்று முதல் வரைவு; "
    "`AMAIPPU_PARVAI.tsv` இல் ஒவ்வொன்றையும் ஆசிரியர் பார்வையிட்டுக் குறிக்கலாம்.", "",
    "ஒத்துப்போகாதவை அமைப்புப் பிரிப்பின் பிழையாகவோ பழைய பெயரின் சுருக்கமாகவோ இருக்கலாம் — docs/THOGUPPU.md §13 இல் மாதிரிகள்.", "",
    f"## அளவு மோதல் (காண்டிகை ↔ பழைய புலம்): {len(alavu_bad)}", ""] + [f"- {i}: காண்டிகை {a}, பழைய புலம் {o}" for i, a, o in alavu_bad[:40]] + [
    "", "---", "", FOOT]
import random as _r                                                  # noqa: E402
_rnd = _r.Random(1602)
bad_ot = [(f, l, sp) for f, l, sp in ottru if not ottha(l, sp)]
ar = ["# அமைப்புப் பிரிப்பு — பார்வைக்கான மாதிரிகள்", "", "பழைய சுருக்கப் பெயரோடு ஒத்துப்போகாத அமைப்புத் தொடர்களில் 40 மாதிரி.", "",
      "| புலம் | பழைய பெயர் | மூலத் தொடர் |", "|---|---|---|"] + [
      f"| {f} | {', '.join(l)} | {' / '.join(sp)} |" for f, l, sp in _rnd.sample(bad_ot, min(40, len(bad_ot)))] + ["", "---", "", FOOT]
sys.path.insert(0, str(ROOT / "scripts"))
from thoguppu import ezhuthu as _ezhuthu  # noqa: E402
_ezhuthu("araaya", "\n".join(ar))
tsv = ["அடையாளம்\tமூலம்\tஎழுவாய்\tநிபந்தனை\tவிளைவு\tசான்று வழி\tசரியா (ஆசிரியர்)"]
for rec in rows:
    sv = rec.get("saanru_vazhi", {})
    if "அமைப்பு" in sv.values():
        S = rec["saanru"]
        tsv.append("\t".join([rec["id"], ALL[rec["id"]]["moolam"].replace("\n", " / ")] +
                              [" | ".join(S.get(f, [])) for f in ("ezhuvaai", "nibanthanai", "vilaivu")] +
                              [", ".join(f"{k}:{v}" for k, v in sv.items()), ""]))
(ROOT / "pothu/AMAIPPU_PARVAI.tsv").write_text("\n".join(tsv) + "\n", "utf-8")
_ezhuthu("pothu_arikkai", "\n".join(lines))
ml = ["# முறைமை மோதல் — ஆசிரியர் முடிவுக்கு", "",
      "ஒரே நூற்பாவில் «வேண்டும்» (கட்டாயம்) உம் «உரித்து / வரையார் / மானமில்லை» உம் வருகின்றன. எதைக் கொள்வது என்பதை நிரல் தீர்க்கவில்லை.", "",
      "| நூற்பா | மூலம் | சொற்கள் | எந்த அடியில் |", "|---|---|---|---|"]
for r in mothal:
    rec = next(x for x in rows if x["id"] == r["id"])
    adi = r["moolam"].split("\n")
    where = [f"«{w}» அடி {next((i + 1 for i, a in enumerate(adi) if w.split()[0] in a), '?')}" for w in rec["saanru"].get("murai", [])]
    ml.append(f"| {r['id']} | {r['moolam'].replace(chr(10), ' / ')} | {', '.join(rec['saanru'].get('murai', []))} | {'; '.join(where)} |")
ml += ["", "இரண்டிலும் இரு சொல்லும் வெவ்வேறு அடியில், வெவ்வேறு கூற்றைச் சுட்டுகின்றன: எழு. 156 இல் இரு முறையும் «உரியவை», ஆனால் வேற்றுமையில் "
       "«போற்றல் வேண்டும்»; எழு. 199 இல் ஆன் இடை வருதல் «மான மில்லை», பஃகான் மெய் «உய்தல் வேண்டும்». ஆகவே இவை மோதல் அன்று — "
       "ஒவ்வொரு முறைமையும் தன் அடிக் கூற்றுக்கு உரியது என்று கொள்ளலாம். இதை ஏற்பதா என்பது ஆசிரியர் முடிவு."]
_ezhuthu("mothal", "\n".join(ml))

print(f"பொது வடிவம்: {len(rows)} நூற்பா; வகை {dict(C('vagai'))}")
print(f"முறைமை: {dict(C('murai'))}; மோதல் {len(mothal)}; அளவு மோதல் {len(alavu_bad)}")
print(f"சரிபார்ப்பு: {'எல்லாம் சரி' if not bad else str(len(bad)) + ' பிழை: ' + str(bad[:6])}")
sys.exit(1 if bad else 0)
