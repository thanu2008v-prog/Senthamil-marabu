# © 2026 Thanushanthan Varnakulasingam (தனுசாந்தன் வர்ணகுலசிங்கம்) — செந்தமிழ் மரபு · தமிழ் குறியியல்.
# அனைத்து உரிமைகளும் காக்கப்பட்டவை. All rights reserved.
# உரியவரின் எழுத்து அனுமதியின்றி நகலெடுத்தல், மாற்றுதல், வணிகப் பயன், எந்த AI / இயந்திரக் கற்றல் அமைப்பின் பயிற்சிக்கோ உருவாக்கத்துக்கோ பயன்படுத்துதல் கூடாது.
# No copying, modification, commercial use, or use in training or building any AI / machine-learning system without the owner's written permission.
# மூல நூல் (தொல்காப்பிய நூற்பாப் பாடம்) பொது உடைமை; இவ்வுரிமை இத்தொகுப்பு, விதி வடிவமைப்பு, குறியீடு ஆகியவற்றுக்கு.
"""தமிழ் குறியியல் — முதல் நூலின் எழுத்து விதிகள் ௧௫ பிட்டுக் குறியாக (எழுத்து வடிவம் / வரைவு இதில் இல்லை).
௧௫ பிட்டு: [ஒற்று][இடம் ௪][இனம் ௨][இணை][புள்ளி ௨][அங்காத்தல், நா விளிம்பு, இதழ் குவிதல், இடை உயரம், நெடில்]
விதிகள்: பிறப்பு (எழுத்து.௮௪–௧௦௦), உயிர்மெய் (௧௭–௧௮, ௧௩௯), மெய்ம்மயக்கம் (௨௩–௩௦), மொழிமுதல் (௫௯–௬௫), மொழியிறுதி (௬௯–௮௧).
சரிபார்ப்பு: python kuri.py  →  ஒருமை ௨௪௭, மெய்ம்மயக்கம் ௮௬/௮௬, மொழிமுதல் ௨௪௭/௨௪௭, மொழியிறுதி ௨௪௭/௨௪௭."""
import json, pathlib
H = pathlib.Path(__file__).parent
UYIR = "அ ஆ இ ஈ உ ஊ எ ஏ ஐ ஒ ஓ ஔ".split()
MEI = "க ங ச ஞ ட ண த ந ப ம ய ர ல வ ழ ள ற ன".split()
TD = "௦௧௨௩௪௫௬௭௮௯"; T = lambda n: "".join(TD[int(c)] for c in str(n))
# பிறப்பிடம் (பின் → முன்), எழுத்து.௮௯–௯௯
IDAM = {"க": (0, "எழுத்து.௮௯"), "ங": (0, "எழுத்து.௮௯"), "ச": (1, "எழுத்து.௯௦"), "ஞ": (1, "எழுத்து.௯௦"),
        "ட": (2, "எழுத்து.௯௧"), "ண": (2, "எழுத்து.௯௧"), "ற": (3, "எழுத்து.௯௪"), "ன": (3, "எழுத்து.௯௪"), "ர": (3, "எழுத்து.௯௫"), "ழ": (3, "எழுத்து.௯௫"),
        "ல": (4, "எழுத்து.௯௬"), "ள": (4, "எழுத்து.௯௬"), "த": (5, "எழுத்து.௯௩"), "ந": (5, "எழுத்து.௯௩"), "வ": (6, "எழுத்து.௯௮"), "ப": (7, "எழுத்து.௯௭"), "ம": (7, "எழுத்து.௯௭"),
        "ய": (8, "எழுத்து.௯௯")}   # ய தனிப் பிறப்பு: அண்ணம் சேர்ந்த மிடற்று வளி (௯௯) — நூல் வரிசையில் இறுதி
INAM = {**{m: "வல்" for m in "க ச ட த ப ற".split()}, **{m: "மெல்" for m in "ங ஞ ண ந ம ன".split()}, **{m: "இடை" for m in "ய ர ல வ ழ ள".split()}}
INAI2 = {"ழ", "ள"}                                   # வடிவமைப்புத் தேர்வு (௯௫, ௯௬ ஒரே நூற்பா)
KUZHU = {**dict.fromkeys(["அ", "ஆ"], "அங்காத்தல்"), **dict.fromkeys(["இ", "ஈ", "எ", "ஏ", "ஐ"], "நா விளிம்பு"), **dict.fromkeys(["உ", "ஊ", "ஒ", "ஓ", "ஔ"], "இதழ் குவிதல்")}
NEDIL = set("ஆ ஈ ஊ ஏ ஐ ஓ ஔ".split()); IDAI_UYARAM = set("எ ஏ ஒ ஓ".split())    # ௮௮ சிறு திரிபு

def en_ezhuthu(n):
    """நூல் எண் கணக்கு (எழுத்து.௧, ௮, ௯, ௨௨): ௧–௧௨ உயிர்; ௧௩–௩௦ மெய்; ௩௧–௨௪௬ = ௩௦ + ௧௨(மெ−௧) + உ; ௨௪௭ ஆய்தம்."""
    if 1 <= n <= 12: return {"வகை": "உயிர்", "உயிர்": UYIR[n - 1], "மெய்": "", "கணக்கு": f"{T(n)} ≤ ௧௨ — உயிர்"}
    if 13 <= n <= 30: return {"வகை": "மெய்", "உயிர்": "", "மெய்": MEI[n - 13], "கணக்கு": f"{T(n)} − ௧௨ = {T(n - 12)} — மெய்"}
    if 31 <= n <= 246:
        m, u = divmod(n - 31, 12); return {"வகை": "உயிர்மெய்", "உயிர்": UYIR[u], "மெய்": MEI[m], "கணக்கு": f"{T(n)} = ௩௦ + ௧௨ × {T(m)} + {T(u + 1)}"}
    if n == 247: return {"வகை": "ஆய்தம்", "உயிர்": "", "மெய்": "", "கணக்கு": "௧௨ + ௧௮ + ௨௧௬ + ௧ = ௨௪௭"}
    return None

def ezhuthu(e):
    if e["வகை"] == "உயிர்": return e["உயிர்"]
    if e["வகை"] == "மெய்": return e["மெய்"] + "்"
    if e["வகை"] == "ஆய்தம்": return "ஃ"
    S = dict(zip(UYIR, ["", "ா", "ி", "ீ", "ு", "ூ", "ெ", "ே", "ை", "ொ", "ோ", "ௌ"])); return e["மெய்"] + S[e["உயிர்"]]

NAMES = ["ஒற்று", "இடம்₃", "இடம்₂", "இடம்₁", "இடம்₀", "இனம்₁", "இனம்₀", "இணை", "புள்ளி₁", "புள்ளி₀", "அங்காத்தல்", "நா விளிம்பு", "இதழ் குவிதல்", "இடை உயரம்", "நெடில்"]
INAM_B = {"வல்": 0, "மெல்": 1, "இடை": 2}
def uyir_bits(u):
    k = KUZHU[u]; b = 0
    if k == "அங்காத்தல்" or u in ("ஐ", "ஔ"): b |= 1 << 4
    if k == "நா விளிம்பு": b |= 1 << 3
    if k == "இதழ் குவிதல்": b |= 1 << 2
    if u in IDAI_UYARAM: b |= 1 << 1
    if u in NEDIL: b |= 1
    if u == "ஐ": b = (1 << 4) | (1 << 3) | 1           # ௫௪: அ + இ, ஈரளபு
    if u == "ஔ": b = (1 << 4) | (1 << 2) | 1           # ௫௫: அ + உ, ஈரளபு
    return b
def mei_bits(m):
    return (1 << 14) | (IDAM[m][0] << 10) | (INAM_B[INAM[m]] << 8) | ((m in INAI2) << 7)
def code(e):
    v = e["வகை"]
    if v == "உயிர்": return uyir_bits(e["உயிர்"])
    if v == "ஆய்தம்": return 0b11 << 5
    if v == "மெய்": return mei_bits(e["மெய்"]) | (0b01 << 5)
    return mei_bits(e["மெய்"]) | uyir_bits(e["உயிர்"])
def bits(c): return format(c, "015b")
def maathirai(c):
    if (c >> 5) & 3 == 3: return 0.5                    # ஆய்தம் (௧௧ சார்பு அரை)
    if (c >> 5) & 3 == 1: return 0.5                    # மெய் அரை (௧௧)
    return 2 if c & 1 else (1 if c & 0b11100 else 0)
def soodhanai():
    E = [en_ezhuthu(n) for n in range(1, 248)]; C = [code(e) for e in E]; R = {}
    R["ஒருமை (247 குறியும் வேறு)"] = len(set(C)) == 247
    um = [(e, c) for e, c in zip(E, C) if e["வகை"] == "உயிர்மெய்"]
    R["உயிர்மெய் = மெய் OR உயிர் (௧௭–௧௮)"] = sum(c == (mei_bits(e["மெய்"]) | uyir_bits(e["உயிர்"])) for e, c in um) == 216
    R["உயிர் நீக்கின் மெய் வடிவு (௧௩௯)"] = all((c & ~0b11111) | (0b01 << 5) == code({"வகை": "மெய்", "மெய்": e["மெய்"], "உயிர்": ""}) for e, c in um)
    R["ஐ = அ OR இ (+நெடில்) (௫௪)"] = uyir_bits("ஐ") == uyir_bits("அ") | uyir_bits("இ") | 1
    R["ஔ = அ OR உ (+நெடில்) (௫௫)"] = uyir_bits("ஔ") == uyir_bits("அ") | uyir_bits("உ") | 1
    pairs = [("அ", "ஆ"), ("இ", "ஈ"), ("உ", "ஊ"), ("எ", "ஏ"), ("ஒ", "ஓ")]
    R["குறில்–நெடில் ஒரு பிட்டு (௩–௪)"] = all(bin(uyir_bits(a) ^ uyir_bits(b)).count("1") == 1 for a, b in pairs)
    vm = list(zip("க ச ட த ப ற".split(), "ங ஞ ண ந ம ன".split()))
    R["வல்–மெல் இணை: பிறப்பிடம் ஒன்று, இனம் மட்டும் வேறு (௧௦௦)"] = all((mei_bits(a) ^ mei_bits(b)) >> 8 & 0b111111 in (1, 3) and (mei_bits(a) ^ mei_bits(b)) >> 10 == 0 for a, b in vm)
    R["மாத்திரை பிட்டிலிருந்து (௩–௪, ௧௧)"] = all(maathirai(c) == (0.5 if e["வகை"] in ("மெய்", "ஆய்தம்") else (2 if e["உயிர்"] in NEDIL else 1)) for e, c in zip(E, C))
    # ஒப்பீடு: எண் வரிசை n இன் இருமம்
    N = {ezhuthu(e): n for n, e in enumerate(E, 1)}
    R["ஒப்பீடு — n இருமம்: உயிர்மெய் = மெய் OR உயிர்?"] = sum(N[ezhuthu(e)] == (N[e["மெய்"] + "்"] | N[e["உயிர்"]]) for e, c in um) == 216
    return R, C

VAL, MEL, IDAI = 0, 1, 2
def F(m):
    c = mei_bits(m); return c >> 10 & 15, c >> 8 & 3          # (இடம், இனம்)
VAL, MEL, IDAI = 0, 1, 2
def pin_thogudhi(m):                                                 # ௨௯ இன் பின்னொற்றுத் தொகுதி: வல்/மெல் @ இடம் ௦ ௧ ௫ ௭  +  இடை @ ௬ ௮ (வ ய)
    i, n = F(m); return (n in (VAL, MEL) and i in (0, 1, 5, 7)) or (n == IDAI and i in (6, 8))
VITHI = {
 "ezhu.23": ("ட ற ல ள முன் க ச ப", lambda a, b: ((F(a)[1] == VAL and F(a)[0] in (2, 3)) or F(a) == (4, IDAI)) and F(b)[1] == VAL and F(b)[0] in (0, 1, 7)),
 "ezhu.24": ("ல ள முன் ய வ", lambda a, b: F(a) == (4, IDAI) and F(b)[1] == IDAI and F(b)[0] in (6, 8)),
 "ezhu.25": ("மெல் முன் அதே இடத்து வல் — ஒரே பிட்டு விதி", lambda a, b: F(a)[1] == MEL and F(b)[1] == VAL and F(a)[0] == F(b)[0]),
 "ezhu.26": ("ண ன முன் க ச ஞ ப ம ய வ", lambda a, b: F(a)[1] == MEL and F(a)[0] in (2, 3) and pin_thogudhi(b) and F(b)[0] != 5 and F(b) != (0, MEL)),
 "ezhu.27": ("ஞ ந ம வ முன் ய", lambda a, b: ((F(a)[1] == MEL and F(a)[0] in (1, 5, 7)) or F(a) == (6, IDAI)) and F(b) == (8, IDAI)),
 "ezhu.28": ("ம முன் வ", lambda a, b: F(a) == (7, MEL) and F(b) == (6, IDAI)),
 "ezhu.29": ("ய ர ழ முன் க ங ச ஞ த ந ப ம ய வ", lambda a, b: F(a)[1] == IDAI and (F(a)[0] == 8 or (F(a)[0] == 3)) and pin_thogudhi(b)),
 "ezhu.30": ("இரட்டித்தல்: பிட்டுகள் ஒன்றே, ர ழ நீங்க — ஒரே பிட்டு விதி", lambda a, b: mei_bits(a) == mei_bits(b) and F(a) != (3, IDAI)),
}

def P(c):
    return dict(ott=c >> 14 & 1, idam=c >> 10 & 15, inam=c >> 8 & 3, pul=c >> 5 & 3, ang=c >> 4 & 1, naa=c >> 3 & 1, ith=c >> 2 & 1, idai=c >> 1 & 1, ned=c & 1)
def uy(p, name):                                   # உயிர் அடையாளம் பிட்டுகளிலிருந்தே
    a, n, i, d, ne = p["ang"], p["naa"], p["ith"], p["idai"], p["ned"]
    return {"அ": a and not (n or i or ne), "ஆ": a and ne and not (n or i), "ஐ": a and n, "ஔ": a and i,
            "எ": n and d and not ne, "ஏ": n and d and ne, "ஒ": i and d and not ne, "ஓ": i and d and ne,
            "உஊ": i and not d and not a, "எஒ": d and not ne, "ஏஓ": d and ne}[name]
def mei(p, idam, inam): return p["ott"] and p["idam"] == idam and p["inam"] == inam
def uyirmei(p): return p["ott"] and p["pul"] == 0
def uyir(p): return not p["ott"] and p["pul"] == 0
def mudhal(c):
    p = P(c)
    if uyir(p): return True, "எழுத்து.௫௯"
    if not uyirmei(p): return False, "எழுத்து.௬௦"
    if (p["inam"] == VAL and p["idam"] in (0, 5, 7)) or (p["inam"] == MEL and p["idam"] in (5, 7)): return True, "எழுத்து.௬௧"
    if mei(p, 1, VAL): return not (p["ang"] and not uy(p, "ஆ")), "எழுத்து.௬௨"
    if mei(p, 6, IDAI): return not (p["ith"] and not p["ang"]), "எழுத்து.௬௩"
    if mei(p, 1, MEL): return bool(uy(p, "ஆ") or uy(p, "எஒ")), "எழுத்து.௬௪"
    if mei(p, 8, IDAI): return bool(uy(p, "ஆ")), "எழுத்து.௬௫"
    return False, "எழுத்து.௬௦–௬௫ (பிற மெய் முதலாகா)"
def iruthi(c):
    p = P(c)
    if p["pul"] == 3: return "இல்லை", "எழுத்து.௩௮"
    if uyir(p): return ("இல்லை" if uy(p, "ஔ") else "ஆம்"), "எழுத்து.௬௯"
    if p["pul"] == 1:                                                   # மெய்
        if not ((p["inam"] == MEL and p["idam"] != 0) or p["inam"] == IDAI): return "இல்லை", "எழுத்து.௭௮"
        if mei(p, 5, MEL): return "வரம்பு", "எழுத்து.௭௯"
        if mei(p, 1, MEL): return "வரம்பு", "எழுத்து.௮௦"
        if mei(p, 6, IDAI): return "வரம்பு", "எழுத்து.௮௧"
        return "ஆம்", "எழுத்து.௭௮"
    if uy(p, "ஔ"): return ("ஆம்" if (mei(p, 0, VAL) or mei(p, 6, IDAI)) else "இல்லை"), "எழுத்து.௭௦"
    if uy(p, "எ"): return "இல்லை", "எழுத்து.௭௧"
    if uy(p, "ஒ"): return ("ஆம்" if mei(p, 5, MEL) else "இல்லை"), "எழுத்து.௭௨"
    if uy(p, "ஏஓ") and mei(p, 1, MEL): return "இல்லை", "எழுத்து.௭௩"
    if uy(p, "உஊ") and (mei(p, 5, MEL) or mei(p, 6, IDAI)): return "இல்லை", "எழுத்து.௭௪"
    if uy(p, "உஊ") and not p["ned"] and mei(p, 1, VAL): return "வரம்பு", "எழுத்து.௭௫"
    if uy(p, "உஊ") and not p["ned"] and mei(p, 7, VAL): return "வரம்பு", "எழுத்து.௭௬"
    return "ஆம்", "எழுத்து.௭௭"
def norm(v): return "வரம்பு" if "வரம்பு" in str(v) else ("ஆம்" if v in ("ஆம்", True) else "இல்லை")

def main():
    D = json.loads((H / "tharavu.json").read_text(encoding="utf-8"))
    R, C = soodhanai()
    nool = {}
    for a, b, rs in D["mei_mayakkam"]:
        for r in rs: nool.setdefault(r, set()).add((a[0], b[0]))
    for r in VITHI:
        p = {(a, b) for a in MEI for b in MEI if VITHI[r][1](a, b)}; R[f"மெய்ம்மயக்கம் {r}: {len(p & nool[r])}/{len(nool[r])}, மிகை {len(p - nool[r])}"] = p == nool[r]
    T = {r["ezhuthu"]: r for r in D["ezhuthukkal_247"]}
    E = [en_ezhuthu(n) for n in range(1, 248)]
    R["மொழிமுதல் ௨௪௭/௨௪௭ (௫௯–௬௫)"] = all(mudhal(code(e))[0] == bool(T[ezhuthu(e)].get("mozhimudhal")) for e in E)
    R["மொழியிறுதி ௨௪௭/௨௪௭ (௬௯–௮௧)"] = all(iruthi(code(e))[0] == norm(T[ezhuthu(e)].get("mozhiyiruthi")) for e in E)
    for k, v in R.items(): print("✓" if v else ("○ (எதிர்பார்த்த தோல்வி — எண் வரிசை இருமம் நூல் விதியைக் காக்காது)" if k.startswith("ஒப்பீடு") else "✗"), k)
if __name__ == "__main__": main()
