"""எழுத்துப் பகுப்பு — உரையை நூல் கூறும் எழுத்துகளாக (உயிர், மெய், உயிர்மெய், ஆய்தம்) பிரித்தல். karuvi/logic.js-இன் இணை."""
import re
import unicodedata

UYIR = "அஆஇஈஉஊஎஏஐஒஓஔ"
KURIL = "அஇஉஎஒ"
MEY = "கஙசஞடணதநபமயரலவழளறன"
VADA = "ஜஶஷஸஹ"
SIGN = {"ா": "ஆ", "ி": "இ", "ீ": "ஈ", "ு": "உ", "ூ": "ஊ", "ெ": "எ", "ே": "ஏ", "ை": "ஐ", "ொ": "ஒ", "ோ": "ஓ", "ௌ": "ஔ"}
PULLI = "்"
VAL, MEL = "கசடதபற", "ஙஞணநமன"
IRUTHI = "ஞணநமனயரலவழள"                         # எழு. 78


def letters(text):
    """உரை → எழுத்துப் பட்டியல்: {k, c (மெய்), v (உயிர்), vada, s, at}."""
    text = unicodedata.normalize("NFC", text)
    out, i, n = [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch in MEY or ch in VADA:
            nx = text[i + 1] if i + 1 < n else ""
            vada = ch in VADA
            if nx == PULLI:
                out.append(dict(k="மெய்", c=ch, v="", vada=vada, s=ch + nx, at=i)); i += 2
            elif nx in SIGN:
                out.append(dict(k="உயிர்மெய்", c=ch, v=SIGN[nx], vada=vada, s=ch + nx, at=i)); i += 2
            else:
                out.append(dict(k="உயிர்மெய்", c=ch, v="அ", vada=vada, s=ch, at=i)); i += 1
        elif ch in UYIR:
            out.append(dict(k="உயிர்", c="", v=ch, vada=False, s=ch, at=i)); i += 1
        elif ch == "ஃ":
            out.append(dict(k="ஆய்தம்", c="", v="", vada=False, s=ch, at=i)); i += 1
        else:
            out.append(dict(k="பிற", c="", v="", vada=False, s=ch, at=i)); i += 1
    return out


def words(text):
    """தமிழ் எழுத்துத் தொடர்கள் (சொற்கள்), உரையில் தொடக்க–முடிவு இடத்தோடு."""
    W, cur = [], []
    for l in letters(text):
        if l["k"] == "பிற":
            if cur:
                W.append(cur)
            cur = []
        else:
            cur.append(l)
    if cur:
        W.append(cur)
    return [dict(ls=ls, s="".join(l["s"] for l in ls), start=ls[0]["at"], end=ls[-1]["at"] + len(ls[-1]["s"])) for ls in W]


def is_short(l):
    return l["k"] in ("உயிர்", "உயிர்மெய்") and l["v"] in KURIL


def has_uyir(l):
    return l["k"] in ("உயிர்", "உயிர்மெய்")


def letter_name(w):
    return bool(re.match(r"^[க-ஹ](கர|கார|ஃகான்|கான்|னஃகான்)", w["s"]) or re.match(r"^[அ-ஔ](கர|கார)", w["s"]))
