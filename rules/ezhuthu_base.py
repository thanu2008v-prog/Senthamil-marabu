"""எழுத்துப் பகுப்பு — நூன்மரபு (எழு. 1–33) அடிப்படையில்.

உயிர் பன்னிரண்டு (எழு. 8), மெய் பதினெட்டு (எழு. 9), குறில் ஐந்து (எழு. 3),
நெடில் ஏழு (எழு. 4). ஒரு சொல்லை எழுத்துகளாகப் (மெய், உயிர்) பிரிக்கிறது.
"""
UYIR = "அஆஇஈஉஊஎஏஐஒஓஔ"                 # எழு. 8
MEY = "கஙசஞடணதநபமயரலவழளறன"            # எழு. 9 (வரிசை எழு. 19–21)
KURIL = "அஇஉஎஒ"                        # எழு. 3
NEDIL = "ஆஈஊஏஐஓஔ"                      # எழு. 4
VALLINAM, MELLINAM, IDAIYINAM = "கசடதபற", "ஙஞணநமன", "யரலவழள"  # எழு. 19–21
_SIGN = {"": "அ", "ா": "ஆ", "ி": "இ", "ீ": "ஈ", "ு": "உ", "ூ": "ஊ",
         "ெ": "எ", "ே": "ஏ", "ை": "ஐ", "ொ": "ஒ", "ோ": "ஓ", "ௌ": "ஔ"}
PULLI = "்"


def ezhuthu(word):
    """சொல்லை (மெய், உயிர்) இணைகளாகப் பிரிக்கும்.
    உயிர் மட்டும் → ("", உயிர்); மெய் மட்டும் → (மெய், "்"); உயிர்மெய் → (மெய், உயிர்);
    ஆய்தம் → ("ஃ", "")."""
    out, i = [], 0
    while i < len(word):
        ch = word[i]
        if ch in UYIR:
            out.append(("", ch)); i += 1
        elif ch in MEY:
            nxt = word[i + 1] if i + 1 < len(word) else ""
            if nxt == PULLI:
                out.append((ch, PULLI)); i += 2
            elif nxt in _SIGN and nxt:
                out.append((ch, _SIGN[nxt])); i += 2
            else:
                out.append((ch, "அ")); i += 1
        elif ch == "ஃ":
            out.append(("ஃ", "")); i += 1
        else:
            i += 1
    return out


def show(e):
    m, u = e
    if m == "ஃ":
        return "ஃ"
    if not m:
        return u
    return m + PULLI if u == PULLI else m + ("" if u == "அ" else
                                             [k for k, v in _SIGN.items() if v == u][0])
