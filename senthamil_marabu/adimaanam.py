"""கலப்பு அடிமானம் — எழுத்தை எண்ணாகவும் எண்ணை எழுத்தாகவும் (THOGUPPU §18).

    from senthamil_marabu.adimaanam import en, ezhuthu, sol_en, en_sol
    en("க")            # 14   (மெய் 1 × 13 + உயிர் 1)
    ezhuthu(14)        # "க"
    sol_en("தமிழ்")     # [92, 133, 195]
    en_sol([92, 133, 195])  # "தமிழ்"

ஓர் எழுத்து = இரு இலக்கம்: மெய் இலக்கம் A (0 = மெய் இல்லை; 1–18, எழு. 9 «னகார இறுவாய்») ×
உயிர் இலக்கம் B (0 = உயிர் இல்லை; 1–12, எழு. 8 «ஔகார இறுவாய்»). மதிப்பு = A × 13 + B, வீச்சு 0–246.
(0, 0) = ஆய்தம்.

நிலை: இவ்வடிமானம் இவ்வாய்வின் கணக்கு — ஒருதலை அன்மை. உள் வரிசை (அ ஆ இ ஈ …, க ங ச ஞ …) நூலின் முதல், இறுதி
எழுத்தால் (எழு. 1, 8, 9) மட்டும் சுட்டப்படுகிறது; இடையுள்ள வரிசை நூலில் ஒரே இடத்தில் பட்டியலாக இல்லை (ஒருதலை அன்மை).
குற்றியலிகரம், குற்றியலுகரம் இகர உகரக் கட்டத்துள் அடங்கும் (எழு. 34, 36) — தனி மதிப்பு இல்லை.
"""
from .punarchi import UYIR, MEY, to_oli, from_oli

RA, RB = len(MEY) + 1, len(UYIR) + 1          # 19, 13
AAYTHAM = "ஃ"
PULLI = "்"


def _kooru(ch):
    """எழுத்து → (A, B)."""
    if ch == AAYTHAM:
        return 0, 0
    o = to_oli(ch)
    if o in UYIR:
        return 0, UYIR.index(o) + 1
    if len(o) == 2 and o[0] in MEY and o[1] == PULLI:
        return MEY.index(o[0]) + 1, 0
    if len(o) == 3 and o[0] in MEY and o[1] == PULLI and o[2] in UYIR:
        return MEY.index(o[0]) + 1, UYIR.index(o[2]) + 1
    raise ValueError(f"நூலின் எழுத்து அன்று: {ch!r}")


def en(ch):
    a, b = _kooru(ch)
    return a * RB + b


def ezhuthu(n):
    if not 0 <= n < RA * RB:
        raise ValueError(f"வீச்சுக்கு வெளியே: {n}")
    a, b = divmod(n, RB)
    if a == 0:
        return AAYTHAM if b == 0 else UYIR[b - 1]
    m = MEY[a - 1] + PULLI
    return from_oli(m + (UYIR[b - 1] if b else ""))


def pirippu(sol):
    """சொல் → எழுத்துகள் (உயிர்மெய் ஒன்றாக)."""
    out = []
    for ch in sol:
        if out and (ch == PULLI or "ா" <= ch <= "ௌ" or ch == "ௗ"):
            out[-1] += ch
        else:
            out.append(ch)
    return out


def sol_en(sol):
    return [en(e) for e in pirippu(sol)]


def en_sol(ennkal):
    return "".join(ezhuthu(n) for n in ennkal)


def ottrai_en(sol):
    """சொல் முழுவதும் ஒரே எண் — அடிமானம் 247 (எழுத்து ஒவ்வொன்றும் ஓர் இலக்கம்)."""
    v = 0
    for n in sol_en(sol):
        v = v * RA * RB + n
    return v
