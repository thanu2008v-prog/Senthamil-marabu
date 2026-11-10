"""விளி — பெயர் விளி ஏற்கும் வடிவு (சொல். 120–156, விளிமரபு).

    from senthamil_marabu.vili import vili
    vili("நம்பி")                       # நம்பீ — சொல். 123
    vili("ஊரன்")                        # ஊரா — சொல். 132; அண்மையில் ஊர (133)
    vili("வந்தான்", vagai="தொழில்")       # வந்தாய் — சொல். 135
    vili("மரம்", thinai="அஃறிணை")        # மரமே — சொல். 153
    vili("அவன்")                        # [] — சுட்டுமுதற் பெயர் விளி கொள்ளாது (139)

நெறி: விளி கொள்ளும் ஈறுகளும் திரிபும் நூற்பா கூறியவை மட்டும். நூல் விளி ஏலாது என்பவற்றுக்கு வெற்றுப் பட்டியல்.
`vagai`: None, «முறை» (முறைப்பெயர்), «தொழில்» (தொழிலால் கூறும் பெயர்), «பண்பு» (பண்பு கொள் பெயர்), «அளபெடை».
"""
from .punarchi import to_oli, from_oli, punar

N, O = "நூலில் நேரடியாக", "ஒருதலை அன்மை"
NEDIL = set("ஆஈஊஏஐஓஔ")
NEEL = {"அ": "ஆ", "இ": "ஈ", "உ": "ஊ", "எ": "ஏ", "ஒ": "ஓ"}
import re
SUTTU_MUTHAL = re.compile(r"^[அஇஉ](வன்|வள்|வர்|து|வை|ஃது|வ்)$")            # சொல். 139, 144
VINAA = re.compile(r"^(யா|எ)(வன்|வள்|வர்|து|வை)$|^யாஅர்$|^யார்$|^எவன்$")    # சொல். 139, 150
THANMAI = re.compile(r"^(தம|நம|நும|எம)(ன்|ர்|ள்)$")                         # சொல். 156


def _r(sol, sutra, vilakkam, nilai=N):
    return dict(sol=sol, sutra=sutra, vilakkam=vilakkam, nilai=nilai)


def _ae(w):
    """பெயர் + ஏ — புணர்ச்சிப் பொறியால், உடம்படுமெய் உள்ள வடிவு முன்."""
    rs = punar(w, "ஏ", "அல்வழி", thani_vithi=False)
    o = lambda s: to_oli(s)
    rs.sort(key=lambda r: any(a in "அஆஇஈஉஊஎஏஐஒஓஔ" and b in "அஆஇஈஉஊஎஏஐஒஓஔ" for a, b in zip(o(r["sol"]), o(r["sol"])[1:])))
    return rs[0]["sol"]


def vili(peyar, thinai="உயர்திணை", vagai=None, anmai=False):
    """→ [{sol, sutra, vilakkam, nilai}] — விளி கொள்ளாத பெயருக்கு []."""
    w, o = peyar, to_oli(peyar)
    if thinai == "அஃறிணை":
        return [_r(_ae(w), ["சொல். 153"], "அஃறிணைப் பெயர் எல்லாம் விளியில் தெளிநிலை ஏகாரம் பெறும்")]
    # விளி கொள்ளாதவை
    if w in ("தான்", "யான்", "தாம்", "யாம்", "நாம்"):
        return []                                                   # சொல். 139
    if SUTTU_MUTHAL.match(w) or VINAA.match(w) or THANMAI.match(w):
        return []                                                   # சொல். 139, 144, 150, 156
    out = []
    if anmai:
        out.append(_r(w, ["சொல். 129"], "அண்மைச் சொல் இயற்கையாகும்"))
    last = o[-1]
    if last in "அஆஇஈஉஊஎஏஐஒஓஔ":                                     # உயிரீறு — சொல். 122: இ, உ, ஐ, ஓ மட்டும்
        if last == "இ":
            out.append(_r(from_oli(o[:-1] + "ஈ"), ["சொல். 123"], "இ ஈ ஆகும்"))
            if vagai == "அளபெடை":
                out.append(_r(w, ["சொல். 127"], "அளபெடை மிகூஉம் இகர இறு பெயர் இயற்கையும் ஆகும்"))
        elif last == "ஐ":
            out.append(_r(from_oli(o[:-1] + "ஆய்"), ["சொல். 123"], "ஐ ஆய் ஆகும்"))
            if vagai == "முறை":
                out.append(_r(from_oli(o[:-1] + "ஆ"), ["சொல். 128"], "முறைப்பெயர் ஐ ஈறு ஆவொடு வருதற்கு உரியவும் உள"))
        elif last == "ஓ":
            out.append(_r(_ae(w), ["சொல். 124"], "ஓ ஏயொடு சிவணும்"))
        elif last == "உ":
            from .urupu import _kutriyalukaram
            if _kutriyalukaram(w):
                out.append(_r(_ae(w), ["சொல். 124", "சொல். 125"], "குற்றியலுகரம் ஏயொடு சிவணும்"))
            else:
                return out                                          # சொல். 125 — முற்றியலுகரம் அன்று
        else:
            return out                                              # சொல். 126 — ஏனை உயிர் விளி கொள்ளா
        return out
    tail = o[-2:]
    if tail not in ("ன்", "ர்", "ல்", "ள்"):
        return out                                                  # சொல். 130, 131
    prev = o[-3] if len(o) >= 3 else ""
    if tail == "ன்":
        if vagai == "முறை":
            out.append(_r(_ae(w), ["சொல். 138"], "முறைப்பெயர் ஏயொடு வரும்"))
        elif prev == "ஆ" and vagai in ("தொழில்", "பண்பு"):
            out.append(_r(from_oli(o[:-3] + "ஆய்"), ["சொல். 135" if vagai == "தொழில்" else "சொல். 136"], "தொழிலின் / பண்பின் கூறும் ஆன் ஈறு ஆய் ஆகும்"))
        elif prev == "ஆ":
            out.append(_r(w, ["சொல். 134"], "ஆன் ஈறு இயற்கையாகும்"))
        elif prev == "அ":
            out.append(_r(from_oli(o[:-3] + "ஆ"), ["சொல். 132"], "அன் ஈறு ஆ ஆகும்"))
            out.append(_r(from_oli(o[:-3] + "அ"), ["சொல். 133"], "அண்மைச் சொல்லிற்கு அகரமும் ஆகும்"))
        elif vagai == "அளபெடை":
            out.append(_r(w, ["சொல். 137"], "அளபெடைப் பெயர் அளபெடை இயல"))
    elif tail == "ர்":
        if prev in ("அ", "ஆ"):
            out.append(_r(from_oli(o[:-3] + "ஈர்"), ["சொல். 140"], "ஆரும் அருவும் ஈரொடு சிவணும்", O))
            if vagai in ("தொழில்", "பண்பு"):
                out.append(_r(_ae(w), ["சொல். 141" if vagai == "தொழில்" else "சொல். 142"], "தொழிற்பெயர் / பண்பு கொள் பெயர் — ஏகாரம் வருதலும் வழுக்கு இன்று"))
    else:                                                           # ல், ள்
        if tail == "ள்" and prev == "ஆ" and vagai in ("தொழில்", "பண்பு"):
            out.append(_r(from_oli(o[:-3] + "ஆய்"), ["சொல். 148"], "வினையினும் பண்பினும் தோன்றும் ஆள் ஈறு ஆய் ஆகும்"))
        elif vagai == "முறை" and tail == "ள்":
            out.append(_r(_ae(w), ["சொல். 149", "சொல். 138"], "முறைப்பெயர் முறைப்பெயர் இயல — ஏயொடு"))
        elif prev in NEDIL:
            out.append(_r(w, ["சொல். 147"], "அயல் நெடிதாயின் இயற்கையாகும்"))
        elif prev in NEEL:
            out.append(_r(from_oli(o[:-3] + NEEL[prev] + tail), ["சொல். 146"], "நின்ற ஈற்றயல் நீட்டம் வேண்டும்", O))
    return out
