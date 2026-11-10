"""இலக்கணச் சரிபார்ப்பு — மொழிமுதல் (எழு. 59–66), மொழியிறுதி (69–78), மெய்ம்மயக்கம் (22–30, 48, 49), வட எழுத்து (சொல். 401).

    from senthamil_marabu.ilakkanam import check
    check("ரவி பஸ்ஸில் சென்றான்")["findings"]

நிலை: «மாறு» நூலுக்கு மாறு · «இல்லை» நூலில் இல்லை · «ஒருதலை» ஒருதலை அன்மை · «புணர்ச்சி» மீறல் அல்ல.
நூலின் 1602 சூத்திரத்தில் «மாறு» 0 (tests/test_api.py). karuvi/logic.js-இன் இணை; இரண்டும் ஒரே முடிவு தர வேண்டும்.
"""
from functools import lru_cache
from .ezhuthu import words, is_short, letter_name, VAL, MEL, IRUTHI


@lru_cache(maxsize=1)
def _bookwords():
    import senthamil_marabu as sm
    return frozenset(w for r in sm.sutras() for w in r["moolam"].split())


def check(text, book_exceptions=True):
    W, F = words(text), []
    BW = _bookwords() if book_exceptions else frozenset()

    def add(w, rule, nilai, msg):
        if nilai == "மாறு" and w["s"] in BW:
            nilai, msg = "ஒருதலை", msg + " — ஆனால் இச்சொல் நூலுள்ளேயே வருகிறது"
        F.append(dict(word=w["s"], start=w["start"], end=w["end"], rule=rule, nilai=nilai, msg=msg))

    for wi, w in enumerate(W):
        L = w["ls"]
        if any(l["vada"] for l in L):
            add(w, "சொல். 401", "இல்லை", "வட எழுத்து — நூலின் முப்பது எழுத்துள் அடங்காதது")
        if len(L) == 1 or letter_name(w):
            continue                                                   # எழு. 66
        f = L[0]
        if not f["vada"]:
            if f["k"] in ("மெய்", "ஆய்தம்"):
                add(w, "எழு. 60", "மாறு", f"«{f['s']}» — உயிர்மெய் அல்லாதது மொழிமுதல் ஆகாது")
            elif f["k"] == "உயிர்மெய்":
                c, v = f["c"], f["v"]
                if c in "கதநபம":
                    pass
                elif c == "ச":
                    if v in "அஐஔ": add(w, "எழு. 62", "மாறு", f"சகரம் {v}-வோடு மொழிமுதல் ஆகாது")
                elif c == "வ":
                    if v in "உஊஒஓ": add(w, "எழு. 63", "மாறு", f"வகரம் {v}-வோடு மொழிமுதல் ஆகாது")
                elif c == "ஞ":
                    if v not in "ஆஎஒ": add(w, "எழு. 64", "மாறு", "ஞகரம் ஆ, எ, ஒ-வோடு மட்டுமே மொழிமுதல்")
                elif c == "ய":
                    if v != "ஆ": add(w, "எழு. 65", "மாறு", "யகரம் ஆகாரத்தோடு மட்டுமே மொழிமுதல்")
                else:
                    add(w, "எழு. 61", "மாறு", f"«{c}» மொழிமுதல் எழுத்துகளுள் இல்லை (எழு. 61–65)")
        z = L[-1]
        if not z["vada"]:
            if z["k"] == "உயிர்மெய்":
                if z["v"] == "ஔ" and z["c"] not in "கவ": add(w, "எழு. 70", "மாறு", "ஔ ககர வகரத்தோடு மட்டுமே இறுதி")
                if z["v"] == "எ": add(w, "எழு. 71", "மாறு", "எகரம் உயிர்மெய்யாக மொழியிறுதி ஆகாது")
                if z["v"] == "ஒ" and z["c"] != "ந": add(w, "எழு. 72", "மாறு", "ஒகரம் நகரத்தோடு மட்டுமே உயிர்மெய் இறுதி")
                if z["c"] == "ஞ" and z["v"] in "ஏஓ": add(w, "எழு. 73", "மாறு", "ஞகரத்தோடு ஏ, ஓ இறுதி இல்லை")
                if z["c"] in "நவ" and z["v"] in "உஊ":
                    add(w, "எழு. 74", "ஒருதலை", "நகர வகரத்தோடு உ, ஊ — நூலே «அளவு», «பிரிவு» போன்ற சொற்களை ஆள்வதால் இவ்விலக்கின் எல்லை ஒருதலை அன்மை")
            elif z["k"] == "உயிர்" and z["v"] == "ஔ":
                add(w, "எழு. 69", "மாறு", "ஔ தனித்து மொழியிறுதி ஆகாது")
            elif (z["k"] == "மெய்" and z["c"] not in IRUTHI) or z["k"] == "ஆய்தம்":
                nx = W[wi + 1] if wi + 1 < len(W) else None
                touching = nx and text[w["end"]:nx["start"]].strip() == ""
                if touching and nx["ls"][0]["k"] == "உயிர்மெய்" and nx["ls"][0]["c"] in VAL:
                    add(w, "எழு. 108", "புணர்ச்சி", f"«{z['s']}» — அடுத்த சொல்லின் வல்லின முதலோடு புணர்ந்த ஒற்று; மொழியிறுதி அன்று")
                else:
                    add(w, "எழு. 78", "மாறு", f"«{z['s']}» — புள்ளியிறுதி பதினொன்றுள் இல்லை")
        if len(L) == 2 and is_short(L[0]) and L[1]["k"] == "மெய்" and L[1]["c"] in "ரழ":
            add(w, "எழு. 49", "ஒருதலை", f"«{w['s']}» — குறிலை அடுத்து ர், ழ் ஒற்றாக நிற்கும் ஈரெழுத்துச் சொல்; நூற்பாவின் பொருள் எல்லை ஒருதலை அன்மை")
        for i in range(len(L) - 1):
            a, b = L[i], L[i + 1]
            if a["k"] != "மெய்" or not b["c"] or a["vada"] or b["vada"]:
                continue
            X, Y = a["c"], b["c"]
            ok, rule = False, "எழு. 22"
            if X == Y:
                ok, rule = X not in "ரழ", "எழு. 30"
            elif X in "டறலள" and Y in "கசப": ok = True
            elif X in "லள" and Y in "யவ": ok = True
            elif X in MEL and VAL[MEL.index(X)] == Y: ok = True
            elif X in "ணன" and Y in "கசஞபமயவ": ok = True
            elif X in "ஞநமவ" and Y == "ய": ok = True
            elif X == "ம" and Y == "வ": ok = True
            elif X in "யரழ" and Y in "கசதநபமவயஞங": ok = True
            if not ok:
                if X in IRUTHI and Y in "கசதநபமவஞய":
                    add(w, rule, "ஒருதலை", f"«{a['s']}{b['s']}» — ஒரு சொல்லுள் இம்மயக்கம் நூலில் இல்லை; இரு சொல் இடைவெளியின்றி எழுதப்பட்டிருக்கலாம் (புணர்ச்சி — எழு. 108)")
                else:
                    add(w, rule, "மாறு", f"«{a['s']}{b['s']}» — இம்மெய்ம்மயக்கம் நூலில் கூறப்படவில்லை (எழு. 22–30)")
            if b["k"] == "மெய்" and i + 2 < len(L) and L[i + 2]["c"]:
                if not (X in "யரழ" and Y in "கசதபஙஞநம"):
                    add(w, "எழு. 48", "மாறு", f"«{a['s']}{b['s']}» — ஈரொற்று ய, ர, ழ-வுக்குப் பின் மட்டும்")
    return {"words": len(W), "findings": F}
