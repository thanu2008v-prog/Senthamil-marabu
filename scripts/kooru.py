"""நூற்பாவைக் கூறுகளாகப் பிரித்தல் — எழுவாய், நிபந்தனை, விளைவு, கூற்றுரிமை — நூற்பாவின் சொல் அமைப்புக் குறிகளால் மட்டும்.

குறிகள் நூலின் சொல்லே (ஒலி வரிசையில் சொல் இறுதியால் ஒப்பிடப்படுகிறது; புணர்ந்த வடிவும் பொருந்தும்):
- முன் நிலை: «முன்னர்», «முன்», «மிசை», «மேல்» — இவற்றோடு முடியும் தொடர் நிலைமொழி/எழுவாய் (எ.கா. «அகர இறுதிப் பெயர்நிலை முன்னர்»)
- நிபந்தனை: «வரின்», «தோன்றின்», «இயையின்», «காலை», «வருவழி», «ஆயின்», «எனின்», «புணரின்», «கண்ணும்», «மருங்கின்», «இடத்து», «அல்வழி»
- கூற்றுரிமை: «என்ப», «என்பர்», «மொழிப», «என்மனார் புலவர்», «என்மனார்»
- பட்டியல் முடிவு: «என்னும்», «எனும்», «என்ற», «என்றா»
"""
from senthamil_marabu.ezhuthu import words
from senthamil_marabu.punarchi import to_oli

MUN = ["முன்னர்", "முன்னர்த்", "முன்", "மிசை", "மேல்", "முன்னும்"]
NIB = ["வரின்", "வரினே", "வரினும்", "வரிற்", "வரிற்", "தோன்றிற்", "இயையிற்", "ஆயிற்", "புணரிற்", "வழிக்", "காலையுங்", "காலைக்", "வேண்டின்", "நாடின்", "நோக்கின்", "கொளினே", "கொளின்", "தோன்றின்", "இயையின்", "இயையினும்", "காலை", "காலைத்", "காலையும்", "வருவழி", "வருவழித்",
       "ஆயின்", "ஆயினும்", "எனின்", "புணரின்", "சிவணின்", "கண்ணும்", "மருங்கின்", "இடத்து", "அல்வழி", "அல்வழிக்", "வழியும்"]
ATTR = ["என்ப", "என்பர்", "மொழிப", "என்மனார்", "என்மரும்", "புலவர்", "உணர்ந்திசினோரே"]
LIST = ["என்னும்", "எனும்", "என்ற", "என்றா"]
OPEN = {"அவற்றுள்", "அவைதாம்", "அவைதாஅம்", "அவ்வழிப்", "அவ்வழி"}
_O = {k: [to_oli(w) for w in v] for k, v in dict(MUN=MUN, NIB=NIB, ATTR=ATTR, LIST=LIST).items()}


def _is(tok, kind):
    o = to_oli(tok)
    if kind == "NIB":                                                # «தேருங்காலை» — புணர்ந்த நிபந்தனைச் சொல்லும்
        return any(o.endswith(w) for w in _O[kind])
    return any(o == w or (len(w) > 6 and o.endswith(w)) or (o.endswith(w) and len(o) - len(w) <= 4) for w in _O[kind])


def _enn(tok):
    from senthamil_marabu import en
    for v in (tok, tok[:-2] + "ு" if tok.endswith("ும்") else tok, tok[:-1] if tok.endswith("ே") else tok):
        try:
            if en.mathippu(v):
                return True
        except Exception:
            pass
    return False


def kooru(moolam, vagai=None):
    """→ {ezhuvaai: [தொடர்], nibanthanai: [தொடர்…], vilaivu: [தொடர்], kootru: [தொடர்], pattiyal: [தொடர்]} — எல்லாம் மூலச் சொற்களே."""
    lines = [[w["s"] for w in words(l)] for l in moolam.split("\n")]
    lines = [l for l in lines if l]
    while lines and len(lines[0]) == 1 and lines[0][0] in OPEN:      # தொடக்கத்தில் மட்டும் «அவற்றுள்», «அவைதாம்»
        lines = lines[1:]
    out = {"ezhuvaai": [], "nibanthanai": [], "vilaivu": [], "kootru": [], "pattiyal": []}
    # அடியின் நடுவில் கூற்றுரிமைச் சொல் — «உயர்திணை என்மனார் மக்கட் சுட்டே»: பெயர் | வரையறை
    mid = [l for l in lines if any(_is(t, "ATTR") for t in l[:-1]) and l[0] not in OPEN]
    if mid and len(mid) >= 1 and any(_is(t, "ATTR") for l in lines for t in l[:-1]):
        for l in lines:
            while l and _is(l[-1], "ATTR"):                            # அடி இறுதிக் கூற்றுரிமை
                out["kootru"].append(l[-1]); l = l[:-1]
            if not l:
                continue
            j = next((i for i, t in enumerate(l[:-1]) if _is(t, "ATTR")), None)
            if j is not None and j > 0:
                out["ezhuvaai"].append(" ".join(l[:j])); out["kootru"].append(l[j]); out["vilaivu"].append(" ".join(l[j + 1:]))
            else:
                out["vilaivu"].append(" ".join(l))
        return {k: v for k, v in out.items() if v and v != [""]}
    T = [t for l in lines for t in l]
    while T and T[0] in OPEN:
        T = T[1:]
    # கூற்றுரிமை — இறுதியிலிருந்து
    k = len(T)
    while k > 1 and _is(T[k - 1], "ATTR"):
        k -= 1
    if k < len(T):
        out["kootru"] = [" ".join(T[k:])]
    T = T[:k]
    # பட்டியல்
    for i, t in enumerate(T):
        if _is(t, "LIST") and i > 0:
            out["pattiyal"] = [" ".join(T[:i])]
            T = T[i + 1:]
            break
    # தொகுதிகள்
    cur, segs = [], []
    for t in T:
        cur.append(t)
        if _is(t, "MUN"):
            segs.append(("MUN", cur)); cur = []
        elif _is(t, "NIB"):
            segs.append(("NIB", cur)); cur = []
    tail = cur
    for kind, s in segs:
        (out["ezhuvaai"] if kind == "MUN" and not out["nibanthanai"] else out["nibanthanai"]).append(" ".join(s))
    if not segs and vagai in ("வரையறை", "எண்ணல்", "பகுப்பு") and out["kootru"] and len(tail) >= 2:
        if tail[-1] in ("என", "எனப்", "என்று") and len(tail) >= 3:     # «… கலி என மொழிப» — மேற்கோள் «என»
            tail = tail[:-1]
        j = len(tail) - 1
        if j >= 1 and _enn(tail[j]):                                 # «… நகை நான்கு என்ப» — எண்ணுக்கு முந்தையது பெயர்
            j -= 1
        out["ezhuvaai"] = [tail[j]]
        if j:
            out["vilaivu"] = [" ".join(tail[:j])]                    # தொடர் தொடர்ச்சியாகவே — எண் சொல் «அளவு» சான்றில்
        return {k: v for k, v in out.items() if v and v != [""]}
    if False:
        out["ezhuvaai"] = [tail[-1]]                             # «… குற்றெழுத் தென்ப» — வரையறுக்கப்படும் பெயர் கூற்றுரிமைக்கு முன்
        out["vilaivu"] = [" ".join(tail[:-1])]
        return {k: v for k, v in out.items() if v and v != [""]}
    if not segs:
        if len(tail) >= 3:
            n = 2 if len(tail) >= 4 else 1
            out["ezhuvaai"] = [" ".join(tail[:-n])]
            tail = tail[-n:]
    elif not out["ezhuvaai"] and out["nibanthanai"] and len(out["nibanthanai"][0].split()) >= 3:
        # «ணகார இறுதி வல்லெழுத் தியையின்» — நிபந்தனைத் தொடரின் முன்பகுதி எழுவாய்: குறியை உள்ள சொல்லும் அதற்கு முந்தைய ஒன்றும் நிபந்தனை
        f = out["nibanthanai"][0].split()
        out["ezhuvaai"] = [" ".join(f[:-2])]
        out["nibanthanai"][0] = " ".join(f[-2:])
    if tail:
        out["vilaivu"] = [" ".join(tail)]
    return {k: v for k, v in out.items() if v and v != [""]}
