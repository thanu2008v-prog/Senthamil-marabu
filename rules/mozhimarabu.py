"""மொழிமரபு — மொழிமுதல் (எழு. 59–66), மொழியிறுதி (எழு. 69–78).

check_word(சொல்) → [{sutra, kind, status, note}]
  status: "ஒத்தது" | "மாறு" | "விலக்கு" (எழு. 66 தம்பெயர்) | "ஒருதலை அன்மை"
check_text(தொடர்) → சொல்வாரியாக; அடுத்த சொல்லைக் கொண்டு புணர்ச்சி ஒற்றைப் பிரிக்கும்.
"""
import re
from .ezhuthu_base import ezhuthu, show, UYIR, PULLI

# மொழிமுதல் — நூற்பாச் சொல்லிலேயே
INITIAL = {
    "க": ("எழு. 61", set(UYIR)), "த": ("எழு. 61", set(UYIR)), "ந": ("எழு. 61", set(UYIR)),
    "ப": ("எழு. 61", set(UYIR)), "ம": ("எழு. 61", set(UYIR)),
    "ச": ("எழு. 62", set(UYIR) - set("அஐஔ")),       # "அ ஐ ஔ எனும் மூன்றலங் கடையே"
    "வ": ("எழு. 63", set(UYIR) - set("உஊஒஓ")),       # "உஊ ஒஓ … வருத லில்லை"
    "ஞ": ("எழு. 64", set("ஆஎஒ")),                    # "ஆ எ ஒ … ஞகாரத் துரிய"
    "ய": ("எழு. 65", {"ஆ"}),                          # "ஆவோ டல்லது யகர முதலாது"
}
# மொழியிறுதிப் புள்ளி — "அப்பதி னொன்றே புள்ளி யிறுதி" (எழு. 78)
FINAL_PULLI = set("ஞணநமனயரலவழள")


def is_tampeyar(word):
    """எழுத்தைத் தன் பெயரால் கூறுதல் — "முதலா ஏன தம்பெயர் முதலும்" (எழு. 66)."""
    return bool(re.fullmatch(r"[஀-௿]{1,2}", word)) or \
        bool(re.match(r"^[கஙசஞடணதநபமயரலவழளறன]?[அ-ஔ]?(கர|கார|ஃகான்|கான்)", word))


def check_word(word):
    e = ezhuthu(word)
    if not e:
        return []
    res = []
    m, u = e[0]
    tam = is_tampeyar(word)
    # --- முதல் ---
    if m == "":
        res.append(dict(sutra="எழு. 59", kind="முதல்", status="ஒத்தது",
                        note=f"உயிர் {u} மொழிமுதல்"))
    elif u == PULLI:
        res.append(dict(sutra="எழு. 60", kind="முதல்", status="விலக்கு" if tam else "மாறு",
                        note="மெய் மொழிமுதலாகாது" + (" — தம்பெயர் (எழு. 66)" if tam else "")))
    elif m in INITIAL:
        s, ok = INITIAL[m]
        st = "ஒத்தது" if u in ok else ("விலக்கு" if tam else "மாறு")
        res.append(dict(sutra=s, kind="முதல்", status=st, note=f"{show(e[0])} முதல்"
                        + (" — தம்பெயர் (எழு. 66)" if st == "விலக்கு" else "")))
    elif m != "ஃ":
        res.append(dict(sutra="எழு. 61–65", kind="முதல்", status="விலக்கு" if tam else "மாறு",
                        note=f"{m} மொழிமுதல் பட்டியலில் இல்லை" + (" — தம்பெயர் (எழு. 66)" if tam else "")))
    # --- இறுதி ---
    m, u = e[-1]
    if u == PULLI:
        ok = m in FINAL_PULLI
        res.append(dict(sutra="எழு. 78", kind="இறுதி", status="ஒத்தது" if ok else "மாறு",
                        note=f"{m}{PULLI} இறுதி"))
    elif m == "":
        st = "மாறு" if u == "ஔ" else "ஒத்தது"
        res.append(dict(sutra="எழு. 69", kind="இறுதி", status=st, note=f"உயிர் {u} இறுதி"))
    elif m != "ஃ":
        st, s = "ஒத்தது", "எழு. 69, 77"
        if u == "ஔ":
            s, st = "எழு. 70", ("ஒத்தது" if m in "கவ" else "மாறு")
        elif u == "எ":
            s, st = "எழு. 71", "மாறு"
        elif u == "ஒ":
            s, st = "எழு. 72", ("ஒத்தது" if m == "ந" else "மாறு")
        elif m == "ஞ" and u in "ஏஓ":
            s, st = "எழு. 73", "மாறு"
        elif m in "நவ" and u in "உஊ":
            s, st = "எழு. 74", "ஒருதலை அன்மை"     # நூலே வு-ஈற்றை ஆள்கிறது (ஆய்வு 16)
        if tam and st == "மாறு":
            st = "விலக்கு"
        res.append(dict(sutra=s, kind="இறுதி", status=st, note=f"{show(e[-1])} இறுதி"))
    return res


def check_text(text):
    words = re.findall(r"[஀-௿]+", text)
    out = []
    for j, w in enumerate(words):
        r = check_word(w)
        e = ezhuthu(w)
        nxt = ezhuthu(words[j + 1]) if j + 1 < len(words) else []
        for f in r:
            if f["kind"] == "இறுதி" and f["status"] == "மாறு" and e and e[-1][1] == PULLI and nxt \
                    and nxt[0][0] and (nxt[0][0] == e[-1][0] or (e[-1][0] in "டற" and nxt[0][0] in "கசதப")
                                     or (e[-1][0] == "ங" and nxt[0][0] == "க")):
                f["status"] = "புணர்ச்சி"
                f["note"] += f" — அடுத்த சொல் {words[j + 1]} உடன் புணர்ந்த ஒற்று (மொழியிறுதி அன்று)"
        out.append((w, r))
    return out
