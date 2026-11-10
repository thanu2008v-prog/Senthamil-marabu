"""புணர்ச்சிப் பொறி — எழுத்ததிகாரப் புணர்ச்சி விதிகள் (எழு. 103–483) உருமாற்றும் பொறிகளாக (finite-state transducers).

    from senthamil_marabu.punarchi import punar
    punar("மண்", "குடம்", "வேற்றுமை")      # → [{'sol': 'மட்குடம்', 'vithi': [...], 'nilai': 'நூலில் நேரடியாக'}]

வடிவமைப்பு
- நூல் எழுத்தை மெய்யும் உயிருமாகக் காண்கிறது: உயிர்மெய் = மெய் + உயிர் (எழு. 138, 139). அதனால் பொறி «ஒலி வரிசை»யில்
  இயங்குகிறது: «கடல்» → «க்அட்அல்». விளைவில் மீண்டும் தமிழ் எழுத்தாக்கப்படும்.
- உள்ளீடு: <இனம்><நிலைமொழி><சந்தி><வருமொழி> (இனக் குறி சொல்லின் தொடக்கத்தை உணர்த்தும்). சந்தி «+» = அல்வழி, «=» = வேற்றுமை (எழு. 112).
  இனம் (நிலைமொழி வகை): p பெயர் (இயல்பு), m மரப்பெயர், s சுட்டு (அ இ உ), S சுட்டுமுதல் சொல் (அது, இது…),
  v வினையெச்சம், t தொழிற்பெயர். இவ்வுள் குறிகள் கணினிக்கு மட்டும்; நூலின் சொற்களே புறப்பெயர்.
- ஒவ்வொரு விதியும் ஒரு மாற்றுப் பொறி: «எது → எதுவாக / இடச்சூழல்». கட்டாய விதி ஒரு விளைவு; விருப்ப (உறழ்ச்சி) விதி
  மாறாத வடிவையும் சேர்த்து இரு விளைவு. விதிகள் வரிசையாகத் தொடுக்கப்படுகின்றன (composition).
- மிகும் ஒற்று நிலைமொழியின் இறுதியில் (சந்திக்கு முன்) இடப்படுகிறது; ஆகவே ஒரு விதி இருமுறை இயங்காது.
- «ஒருதலை அன்மை» விதிகள் விளைவிலும் அந்நிலையோடே வரும்.
- சொல்லுக்கெனத் தனி விதி உள்ள சொற்கள் (பனை, புளி, நீ, எண்ணுப்பெயர் முதலியன) இப்பதிப்பில் பொது விதியால் முடிக்கப்படுவதில்லை;
  அவை «தனி விதி» என்று சுட்டப்படும் (punarchi/THANI.json).
"""
import json
import unicodedata
from functools import lru_cache
from pathlib import Path

UYIR = "அஆஇஈஉஊஎஏஐஒஓஔ"
MEY = "கஙசஞடணதநபமயரலவழளறன"
SIGN = {"ா": "ஆ", "ி": "இ", "ீ": "ஈ", "ு": "உ", "ூ": "ஊ", "ெ": "எ", "ே": "ஏ", "ை": "ஐ", "ொ": "ஒ", "ோ": "ஓ", "ௌ": "ஔ"}
TOSIGN = {v: k for k, v in SIGN.items()}
P = "்"
KU = "ு"            # உள் குறி: குற்றியலுகரம் (எழு. 406) — ஒலி வரிசையில் உயிர் தனி எழுத்தாக வருவதால் இக்குறி வேறு பொருளின்றிக் கிடைக்கிறது
VAL, MEL = "கசடதபற", "ஙஞணநமன"
INAM = dict(zip(VAL, MEL))                      # எழு. 143 — க ச த ப முன் ங ஞ ந ம (ட ற முன் ண ன)
VAGAI = {"அல்வழி": "+", "வேற்றுமை": "="}
INAMKURI = {"பெயர்": "p", "மரப்பெயர்": "m", "சுட்டு": "s", "சுட்டுமுதல்": "S", "வினையெச்சம்": "v", "தொழிற்பெயர்": "t"}
NILAI = {"ந": "நூலில் நேரடியாக", "ஒ": "ஒருதலை அன்மை"}


# ── தமிழ் எழுத்து ↔ ஒலி வரிசை
def to_oli(text):
    t, out, i = unicodedata.normalize("NFC", text), [], 0
    while i < len(t):
        c, nx = t[i], t[i + 1] if i + 1 < len(t) else ""
        if c in MEY:
            if nx == P:
                out.append(c + P); i += 2
            elif nx in SIGN:
                out.append(c + P + SIGN[nx]); i += 2
            else:
                out.append(c + P + "அ"); i += 1
        else:
            out.append(c); i += 1
    return "".join(out)


def from_oli(s):
    s = s.replace(KU, "உ")
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c in MEY and i + 1 < len(s) and s[i + 1] == P:
            v = s[i + 2] if i + 2 < len(s) else ""
            if v and v in UYIR:
                out.append(c + TOSIGN.get(v, "")); i += 3
            else:
                out.append(c + P); i += 2
        else:
            out.append(c); i += 1
    return "".join(out)


# ── விதிகள். ஒவ்வொன்றும்: id, சூத்திரம், நிலை (ந/ஒ), கட்டாயமா, விளக்கம், மாற்றங்கள் [(எது, எதுவாக, இடம், வலம்)]
# எழுத்துத் தொகுதிகள் pyfoma குறியீட்டில்: $C மெய், $V உயிர், $VAL வல்லின மெய், $J சந்தி.
C_ = f"[{MEY}]{P}"
V_ = f"[{UYIR}]"
VAL_ = f"[{VAL}]{P}"
MEL_ = f"[{MEL}]{P}"
J_ = r"[\+\=]"
AL, VE = r"\+", r"\="
KURIL = "[அஇஉஎஒ]"


def m(x):                      # மெய் x
    return f"({x}{P})"


def each_val(left, kind="copy", only=VAL):
    """வருமொழி முதல் வல்லினம் ஒவ்வொன்றுக்கும்: copy = அதே ஒற்று மிகும்; inam = இன மெல்லொற்று மிகும் (எழு. 143)."""
    return [("''", m(k if kind == "copy" else INAM[k]), left, f"{J_} {m(k)}") for k in only]


R = []
def rule(id, sutra, nilai, kattayam, vilakkam, changes, vilakku=None):
    """vilakku: விதி «வேண்டும்» எனினும் நூல் விலக்கு கூறுமிடத்து (விருப்ப விதியாக்கி) மாறா வடிவுக்குச் சுட்டும் விலக்கு நூற்பா."""
    R.append(dict(id=id, sutra=sutra, nilai=nilai, kattayam=kattayam, vilakkam=vilakkam, changes=changes, vilakku=vilakku))


# 1. குற்றியலுகரம் அறிதல் (எழு. 406; 267 — குறிலை அடுத்த ஈரெழுத்துச் சொல்லில் உகரம் நிற்கும்)
rule("406", ["எழு. 406"], "ந", True, "வல்லின மெய்யின் மேல் இறுதி உகரம் குறுகும்",
     [("உ", KU, rf"[pmsSvt] .+ {VAL_}", J_)])
rule("267", ["எழு. 267"], "ந", True, "குறிலை அடுத்த ஈரெழுத்துச் சொல்லில் உகரம் குறுகாது",
     [(KU, "உ", rf"[pmsSvt] ({C_})? {KURIL} {VAL_}", J_)])
rule("411", ["எழு. 411"], "ந", False,
     "ஈரெழுத்து, உயிர்த்தொடர் குற்றியலுகரம் — வேற்றுமையாயின் ஒற்றிடை இனமிகும்",
     [("''", m(k), V_, f"{m(k)} {KU} {VE}") for k in VAL],
     vilakku=dict(id="412", sutra=["எழு. 412"], vilakkam="ஒற்றிடை இனமிகா மொழியும் உள; அவற்றுக்கு வல்லெழுத்து மிகலும் இல்லை"))
rule("414ஆ", ["எழு. 414"], "ந", True, "மென்றொடர் குற்றியலுகரம் — வேற்றுமையில் மெல்லொற்று வல்லொற்றாகும்",
     [(m(INAM[k]), m(k), "", f"{m(k)} {KU} {VE}") for k in VAL])
# 2. குற்றியலுகரம் — யகரம் வர இகரமாகும்; உயிர் வர மெய்யீறு போல் (புள்ளியொடு) நின்று உயிர் ஏறும்
rule("410", ["எழு. 410"], "ந", True, "யகரம் வர குற்றியலுகரம் இகரமாகக் குறுகும்", [(KU, "இ", "", rf"{J_} {m('ய')}")])
rule("105", ["எழு. 105", "எழு. 138"], "ந", True, "குற்றியலுகர ஈறு மெய்யீறு போல் நிற்க, வரும் உயிர் மெய்யோடு சேரும்",
     [(KU, "''", "", rf"{J_} {V_}")])
# 3. சுட்டு (அ, இ, உ)
rule("207", ["எழு. 206", "எழு. 207"], "ஒ", True, "சுட்டின் முன் உயிர் வர வகர ஒற்று", [("''", m("வ"), r"s " + V_, f"{J_} {V_}")])
rule("206", ["எழு. 206"], "ந", True, "சுட்டின் முன் ய, வ வர வகர ஒற்று", [("''", m("வ"), r"s " + V_, f"{J_} [யவ]{P}")])
rule("205", ["எழு. 205"], "ந", True, "சுட்டின் முன் ஞ, ந, ம வர அவ்வொற்று மிகும்",
     [("''", m(k), r"s " + V_, f"{J_} {m(k)}") for k in "ஞநம"])
rule("204", ["எழு. 204", "எழு. 236"], "ந", True, "சுட்டின் முன்னும் வினையெச்சத்தின் முன்னும் வல்லெழுத்து மிகும்",
     each_val(r"s " + V_) + each_val(rf"v .* [அஇ]"))
rule("222", ["எழு. 222"], "ந", True, "«செய்யா» வினையெச்சத்தின் முன்னும் வல்லெழுத்து மிகும்", each_val(r"v .* ஆ"))
rule("160", ["எழு. 160"], "ந", True, "குறிலை அடுத்த ஒற்று, உயிர் வர இரட்டும் (தன்னுரு இரட்டல்)",
     [("''", m(c), f"[pmsSvt] ({C_})? {KURIL} {m(c)}", f"{J_} {V_}") for c in MEY])
# 4. உடம்படுமெய் (எழு. 140) — எந்த உயிர்க்கு எது என்பதை நூல் கூறவில்லை; இரண்டும் விருப்பாக
rule("140", ["எழு. 140"], "ஒ", False, "உயிர் முன் உயிர் வர உடம்படுமெய் (ய், வ்)",
     [("''", f"({m('ய')}|{m('வ')})", V_, f"{J_} {V_}")])
# 5. உயிரீற்றுப் பெயர் முன் வல்லினம்
rule("217", ["எழு. 217"], "ந", True, "அகர ஈற்று மரப்பெயர் முன் வல்லினம் வர இன மெல்லெழுத்து மிகும்", each_val(r"m .* அ", "inam"))
rule("203", ["எழு. 203", "எழு. 221", "எழு. 249", "எழு. 254", "எழு. 264", "எழு. 274", "எழு. 289"], "ந", True,
     "அகர ஈற்றுப் பெயரும், அதன் இயல்பின ஆ, ஈ, உ, ஊ, ஏ, ஓ ஈறுகளும் — அல்வழியில் வல்லினம் வர அவ்வொற்று மிகும்",
     [(a, b, l, r.replace(J_, AL)) for a, b, l, r in each_val(r"[pm] .* [அஆஈஉஊஏஓ]")])
rule("235", ["எழு. 235", "எழு. 280"], "ந", True, "இகர, ஐகார ஈற்றுப் பெயர் — வேற்றுமையில் வல்லினம் வர அவ்வொற்று மிகும்",
     [(a, b, l, r.replace(J_, VE)) for a, b, l, r in each_val(r"[pm] .* [இஐ]")])
rule("158", ["எழு. 158"], "ந", False, "இகர, ஐகார ஈற்றுப் பெயர் — அல்வழியில் இயல்பு, மிகுதல், உறழ்தல் மூன்றும் உள; சொல்லைப் பொறுத்தது",
     [(a, b, l, r.replace(J_, AL)) for a, b, l, r in each_val(r"[pm] .* [இஐ]")])
rule("216", ["எழு. 216", "எழு. 225", "எழு. 252", "எழு. 259", "எழு. 266", "எழு. 276", "எழு. 292"], "ஒ", False,
     "அ, ஆ, ஈ, உ, ஊ, ஏ, ஓ ஈற்றுப் பெயர் — வேற்றுமையிலும் «அதனோரற்றே»; சுட்டுவது எது என நூல் பெயரிடாததால் விருப்பாக",
     [(a, b, l, r.replace(J_, VE)) for a, b, l, r in each_val(r"[pm] .* [அஆஈஉஊஏஓ]")])
# 6. மெய்யீறு
rule("296", ["எழு. 296", "எழு. 297", "எழு. 298", "எழு. 306", "எழு. 327", "எழு. 376", "எழு. 401"], "ந", True,
     "ஞ, ந ஈறும் தொழிற்பெயர் ஈறும் — வல்லினமோ ஞ, ந, ம, வவோ வர உகரம் வரும்",
     [("''", "உ", rf"[pmt] .* [ஞந]{P}", rf"{J_} ([{VAL}ஞநமவ]{P})"), ("''", "உ", rf"t .* {C_}", rf"{J_} ([{VAL}ஞநமவ]{P})")])
rule("299", ["எழு. 299"], "ந", True, "நகர ஈறு வேற்றுமையில் உகரம் கெட்டு அகரம்", [("உ", "அ", rf"[ந]{P}", VE)])
rule("296ஆ", ["எழு. 296"], "ந", True, "(அவ்விடத்து) வல்லினம் மிகும்", each_val(rf"[ஞந]{P} [உஅ]") + each_val(rf"t .* {C_} [உஅ]"))
rule("150", ["எழு. 150"], "ந", True, "ண, ள முன் த, ந — ட, ண ஆகும்",
     [(m("த"), m("ட"), f"[ணள]{P} {J_}", ""), (m("ந"), m("ண"), f"[ணள]{P} {J_}", "")])
rule("149", ["எழு. 149"], "ந", True, "ல, ன முன் த, ந — ற, ன ஆகும்",
     [(m("த"), m("ற"), f"[லன]{P} {J_}", ""), (m("ந"), m("ன"), f"[லன]{P} {J_}", "")])
rule("302", ["எழு. 302", "எழு. 396"], "ந", True, "ண, ள ஈறு — வேற்றுமையில் வல்லினம் வர டகரம்",
     [(f"[ணள]{P}", m("ட"), "", f"{VE} {VAL_}")])
rule("332", ["எழு. 332", "எழு. 366"], "ந", True, "ன, ல ஈறு — வேற்றுமையில் வல்லினம் வர றகரம்",
     [(f"[னல]{P}", m("ற"), "", f"{VE} {VAL_}")])
rule("369", ["எழு. 369", "எழு. 399"], "ந", False, "ல, ள ஈறு — தகரம் வர ஆய்தம் நிற்றலும் உண்டு",
     [(f"[லள]{P}", "ஃ", "", f"{J_} [டற]{P}")])
rule("368", ["எழு. 368"], "ந", False, "லகர ஈறு — அல்வழியில் உறழ்ச்சி (றகரமாதலும் இயல்பும்)", [(m("ல"), m("ற"), "", f"{AL} {VAL_}")])
rule("398", ["எழு. 398"], "ந", False, "ளகர ஈறு — அல்வழியில் உறழ்ச்சி (டகரமாதலும் இயல்பும்)", [(m("ள"), m("ட"), "", f"{AL} {VAL_}")])
rule("367", ["எழு. 367", "எழு. 397"], "ந", True, "ல, ள ஈறு — மெல்லெழுத்து வர ன, ண ஆகும்",
     [(m("ல"), m("ன"), "", f"{J_} {MEL_}"), (m("ள"), m("ண"), "", f"{J_} {MEL_}")])
rule("310", ["எழு. 310"], "ந", True, "மகர ஈறு — வேற்றுமையில் மகரம் கெட்டு வல்லெழுத்து மிகும்",
     [(m("ம"), m(k), "", f"{VE} {m(k)}") for k in VAL])
rule("314", ["எழு. 314", "எழு. 143"], "ந", True, "மகர ஈறு — அல்வழியில் இன மெல்லெழுத்தாகும்",
     [(m("ம"), m(INAM[k]), "", f"{AL} {m(k)}") for k in "கசத"])
rule("357", ["எழு. 357", "எழு. 362", "எழு. 383"], "ந", True, "ய, ர, ழ ஈறு — வேற்றுமையில் வல்லினம் வர அவ்வொற்று மிகும்",
     [(a, b, l, r.replace(J_, VE)) for a, b, l, r in each_val(f"[யரழ]{P}")])
rule("379", ["எழு. 379", "எழு. 380"], "ந", True, "சுட்டுமுதல் வகர ஈறு — அல்வழியில் வல்லினம் வர ஆய்தம்; மெல்லினம் வர அம்மெல்லெழுத்து",
     [(m("வ"), "ஃ", r"s .*", f"{AL} {VAL_}")] + [(m("வ"), m(k), r"s .*", f"{J_} {m(k)}") for k in MEL])
# 7. குற்றியலுகர ஈறு முன் வல்லினம் (எழு. 411–414, 425–426)
rule("414", ["எழு. 411", "எழு. 414"], "ந", True, "குற்றியலுகர ஈறு — வேற்றுமையில் வந்த வல்லெழுத்து மிகும்",
     [(a, b, l, r.replace(J_, VE)) for a, b, l, r in each_val(f"{VAL_} {VAL_} {KU}")])
rule("413", ["எழு. 413"], "ஒ", True, "இடையொற்று, ஆய்தத் தொடர் — «நடைஆ இயல»: வல்லெழுத்து மிகுதல் (எந்நடை என நூல் சுட்டவில்லை)",
     [(a, b, l, r.replace(J_, VE)) for a, b, l, r in each_val(f"([யரலவழள]{P}|ஃ) {VAL_} {KU}")])
rule("426", ["எழு. 426", "எழு. 409"], "ந", False, "வல்லொற்றுத் தொடர் — அல்வழியிலும் வல்லெழுத்து மிகும் (மிகாது நிற்றலும் உண்டு — 409)",
     [(a, b, l, r.replace(J_, AL)) for a, b, l, r in each_val(f"{VAL_} {VAL_} {KU}")])
RULES = R


# ── தொகுப்பு
@lru_cache(None)
def _fst(i):
    from pyfoma import FST
    r = RULES[i]
    parts = []
    for a, b, l, rt in r["changes"]:
        parts.append(f"$^rewrite(({a}):({b}) / {l} _ {rt})" if a != "''" else f"$^rewrite('':({b}) / {l} _ {rt})")
    f = FST.re(" @ ".join(parts)) if len(parts) > 1 else FST.re(parts[0])
    if not r["kattayam"]:
        f = FST.re("$f | .*", {"f": f})
    return f


def _kairegai():
    """விதி வரையறைகளின் கைரேகை — ஏற்றுமதியான பொறி (.att) இவ்விதிகளிலிருந்தே வந்தது என்பதை உறுதி செய்ய."""
    import hashlib
    return hashlib.sha256(json.dumps([[r["id"], r["kattayam"], r["changes"]] for r in RULES], ensure_ascii=False).encode("utf-8")).hexdigest()


@lru_cache(None)
def _att():
    """முன்னரே தொகுத்த பொறிகள் (data/pori/*.att) — pyfoma இன்றி, தொகுப்பு நேரம் இன்றி இயங்க.
    கைரேகை ஒவ்வாவிடில் (விதி மாறியிருந்தால்) None — அப்போது pyfoma வழி."""
    d = Path(__file__).resolve().parent / "data/pori"
    man = d / "PORI.json"
    if not man.exists():
        return None
    m = json.loads(man.read_text("utf-8"))
    if m.get("kairegai") != _kairegai() or len(m["vithigal"]) != len(RULES):
        return None
    out = []
    for v in m["vithigal"]:
        T, F = {}, set()
        for ln in (d / Path(v["kopu"]).name).read_text("utf-8").splitlines():
            q = ln.split("\t")
            if len(q) == 1:
                F.add(int(q[0]))
            else:
                T.setdefault(int(q[0]), []).append((int(q[1]), "" if q[2] == "@0@" else q[2], "" if q[3] == "@0@" else q[3]))
        out.append((T, F))
    return out


def _run(fst, s):
    T, F = fst
    out, stack, seen, lim = set(), [(0, 0, "")], set(), 3 * len(s) + 20
    while stack:
        q, i, o = stack.pop()
        if (q, i, o) in seen or len(o) > lim:
            continue
        seen.add((q, i, o))
        if i == len(s) and q in F:
            out.add(o)
        for t, a, b in T.get(q, ()):
            if a == "":
                stack.append((t, i, o + b))
            elif i < len(s) and s[i] == a:
                stack.append((t, i + 1, o + b))
    return out


def _apply(i, s):
    A = _att()
    if A:
        r = _run(A[i], s)
        if r:                                                  # மூடிய எழுத்துத் தொகுதிக்கு வெளியே உள்ள உள்ளீடு — pyfoma வழி
            return sorted(r)
    return sorted(set(_fst(i).generate(s)))


def thani():
    for p in (Path(__file__).resolve().parent / "data/punarchi_thani.json", Path(__file__).resolve().parent.parent / "punarchi/THANI.json"):
        if p.exists():
            return json.loads(p.read_text("utf-8"))
    return {}


def punar(nilaimozhi, varumozhi, vagai="அல்வழி", inam="பெயர்", thani_vithi=True):
    """நிலைமொழி + வருமொழி → விளைவுகள். ஒவ்வொன்றும் {sol, vithi: [{id, sutra, nilai, vilakkam}], nilai}.
    நூல் தனி விதி கூறும் சொல்லெனில் (thanisol.py) அவ்விதி முந்தும்."""
    if thani_vithi:
        from .thanisol import punar_thani
        import senthamil_marabu.punarchi as _self
        _self_flag = getattr(_self, "_in_thani", False)
        if not _self_flag:
            _self._in_thani = True
            try:
                r = punar_thani(nilaimozhi, varumozhi, vagai, inam)
            finally:
                _self._in_thani = False
            if r is not None:
                seen, out = set(), []
                for x in r:
                    if x["sol"] not in seen:
                        seen.add(x["sol"]); out.append(x)
                return out
    if vagai not in VAGAI:
        raise ValueError("vagai: அல்வழி அல்லது வேற்றுமை")
    if inam not in INAMKURI:
        raise ValueError("inam: " + ", ".join(INAMKURI))
    s = INAMKURI[inam] + to_oli(nilaimozhi) + VAGAI[vagai] + to_oli(varumozhi)
    forms = {s: []}
    for i, r in enumerate(RULES):
        nxt = {}
        for f, trace in forms.items():
            outs = _apply(i, f)
            for g in outs:
                t = trace + ([dict(id=r["id"], sutra=r["sutra"], nilai=NILAI[r["nilai"]], vilakkam=r["vilakkam"],
                                   viruppu=not r["kattayam"])] if g != f else [])
                if g == f and len(outs) > 1 and r.get("vilakku"):          # «வேண்டும்» விதியின் விலக்கு வடிவு (எ.கா. 412)
                    t = t + [dict(id=r["vilakku"]["id"], sutra=r["vilakku"]["sutra"], nilai=NILAI["ந"],
                                  vilakkam=r["vilakku"]["vilakkam"], viruppu=True)]
                if g not in nxt or len(t) < len(nxt[g]):
                    nxt[g] = t
        forms = nxt
    out = []
    for f, trace in forms.items():
        sol = from_oli(f[1:].replace("+", "").replace("=", ""))
        nl = "ஒருதலை அன்மை" if any(t["nilai"] == "ஒருதலை அன்மை" for t in trace) else "நூலில் நேரடியாக"
        trace = [t for t in trace if t["id"] not in ("406", "267")]
        if not trace:
            trace = [dict(id="108", sutra=["எழு. 108"], nilai="நூலில் நேரடியாக", vilakkam="இயல்பு — திரிபில்லை", viruppu=False)]
        out.append(dict(sol=sol, vithi=trace, nilai=nl))
    th = thani().get(nilaimozhi)
    if th:
        for o in out:
            o["thani"] = th
    out.sort(key=lambda o: (o["nilai"] != "நூலில் நேரடியாக", any(t["id"] in ("412",) for t in o["vithi"]),
                            any(t["viruppu"] for t in o["vithi"]), o["sol"]))
    return out


def poRi():
    """எல்லா விதிகளையும் தொடுத்த ஒரே பொறி (pyfoma FST). ஏற்றுமதிக்கு: .save_att(), .save_foma()."""
    from pyfoma import FST
    f = _fst(0)
    for i in range(1, len(RULES)):
        f = FST.re("$a @ $b", {"a": f, "b": _fst(i)})
    return f
