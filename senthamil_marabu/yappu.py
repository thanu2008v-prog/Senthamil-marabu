"""யாப்புச் சோதனை — அசை (பொருள். 312–315), சீர் (320–335), அடி (340–354), தொடை (397–404). karuvi/logic.js-இன் இணை.

    from senthamil_marabu.yappu import check, asai
    check("யாயும் ஞாயும் யாரா கியரோ\\nஎந்தையும் நுந்தையும் எம்முறைக் கேளிர்")
"""
from .ezhuthu import words, is_short, has_uyir


def _syllables(L):
    S = []
    for l in L:
        if has_uyir(l):
            S.append({"head": l, "tail": []})
        elif S:
            S[-1]["tail"].append(l)
        else:
            S.append({"head": None, "tail": [l]})
    return S


def asai(word):
    """ஒரு சொல்லை (words() தரும் வடிவு, அல்லது உரை) அசைகளாக: [{peyar, s}]."""
    if isinstance(word, str):
        ws = words(word)
        word = ws[0] if ws else {"ls": []}
    S, A, i = _syllables(word["ls"]), [], 0
    while i < len(S):
        s = S[i]
        if s["head"] and is_short(s["head"]) and not s["tail"] and i + 1 < len(S) and S[i + 1]["head"]:
            a = {"peyar": "நிரை", "parts": [s, S[i + 1]]}; i += 2
        else:
            a = {"peyar": "நேர்", "parts": [s]}; i += 1
        if i < len(S) and i == len(S) - 1 and S[i]["head"] and S[i]["head"]["v"] == "உ":
            a["peyar"] += "பு"; a["parts"].append(S[i]); i += 1
        a["s"] = "".join((p["head"]["s"] if p["head"] else "") + "".join(t["s"] for t in p["tail"]) for p in a["parts"])
        A.append({"peyar": a["peyar"], "s": a["s"]})
    return A


def adi_vagai(n):
    for lo, hi, name, ref in [(4, 6, "குறளடி", "பொருள். 344"), (7, 9, "சிந்தடி", "பொருள். 345"), (10, 14, "நேரடி", "பொருள். 346"),
                              (15, 17, "நெடிலடி", "பொருள். 347"), (18, 20, "கழிநெடிலடி", "பொருள். 348")]:
        if lo <= n <= hi:
            return name, ref
    return ("நூல் கூறும் அளவுக்குக் குறைவு" if n < 4 else "நூல் கூறும் அளவுக்கு மேல்"), "பொருள். 342"


def _seer_vagai(A):
    P = [a["peyar"] for a in A]
    uri = any(p.endswith("பு") for p in P)
    if len(A) == 1: return "அசைச்சீர்", "பொருள். 335"
    if len(A) == 2: return ("ஆசிரிய உரிச்சீர்" if uri else "இயற்சீர்"), "பொருள். 321"
    if len(A) == 3:
        if not any(p.endswith("பு") for p in P[:2]) and P[2] == "நேர்": return "வெண்சீர்", "பொருள். 327"
        return "வஞ்சிச்சீர்", "பொருள். 328"
    return "நூல் கூறும் சீர் அளவுக்கு மேல்", "பொருள். 320"


def _same(a, b):
    return bool(a and b and a["c"] == b["c"] and a["v"] == b["v"])


def _kilai(a, b):
    return bool(a and b and ((a["c"] and a["c"] == b["c"]) or (not a["c"] and not b["c"] and a["v"] and b["v"])))


def check(text):
    lines = [s.strip() for s in text.split("\n") if s.strip()]
    out = []
    for line in lines:
        W = words(line)
        seer = []
        for w in W:
            A = asai(w)
            v, ref = _seer_vagai(A)
            seer.append({"s": w["s"], "asai": A, "vagai": v, "ref": ref, "ok": 2 <= len(A) <= 3})
        n = sum(1 for w in W for l in w["ls"] if has_uyir(l))           # பொருள். 351
        vagai, vref = adi_vagai(n)
        sec = lambda w: w["ls"][1] if len(w["ls"]) > 1 else None
        within = []
        if len(W) >= 3 and _same(sec(W[0]), sec(W[2])): within.append(("பொழிப்பு எதுகை", "பொருள். 403"))
        if len(W) >= 4 and _same(sec(W[0]), sec(W[3])): within.append(("ஒரூஉ எதுகை", "பொருள். 404"))
        if any(any(i > 0 and l["k"] == "உயிர்" and has_uyir(w["ls"][i - 1]) for i, l in enumerate(w["ls"])) for w in W):
            within.append(("அளபெடை", "பொருள். 402"))
        adi = {4: ("நாற்சீர் அடி", "பொருள். 340"), 2: ("இருசீர் அடி (வஞ்சி)", "பொருள். 352"),
               3: ("முச்சீர் அடி", "பொருள். 354")}.get(len(W), (f"{len(W)} சீர்", "பொருள். 340"))
        out.append({"line": line, "W": W, "seer": seer, "ezhuthu": n, "vagai": vagai, "vref": vref, "adi": adi, "within": within})
    pairs = []
    for i in range(len(out) - 1):
        a, b = out[i]["W"], out[i + 1]["W"]
        if not a or not b:
            continue
        fa, fb = a[0]["ls"][0], b[0]["ls"][0]
        sa = a[0]["ls"][1] if len(a[0]["ls"]) > 1 else None
        sb = b[0]["ls"][1] if len(b[0]["ls"]) > 1 else None
        mo = "மோனை" if _same(fa, fb) else ("கிளை மோனை" if _kilai(fa, fb) else "")
        pairs.append({"i": i, "mo": mo, "eth": "எதுகை" if _same(sa, sb) else "",
                      "iy": "இயைபு" if _same(a[-1]["ls"][-1], b[-1]["ls"][-1]) else ""})
    for o in out:
        del o["W"]
    return {"lines": out, "pairs": pairs}
