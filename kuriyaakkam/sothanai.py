"""மரபுக் குறியின் சோதனை — 1602 சூத்திரத்திலும் (sources/moolam.json).
1. முன்–பின் மாற்றம்: யூனிகோடு → மரபுக் குறி → யூனிகோடு, எழுத்துக்கு எழுத்து ஒத்தல்.
2. அளவு: யூனிகோடு குறிப்புள்ளி, UTF-8, UTF-16, மரபுக் குறி.
3. நூல் விதிகள் பிட் செயலாக — எழு. 30, 59–66, 69–78, 143; மாத்திரைக் கூட்டு; சார்பெழுத்து.
python3 kuriyaakkam/sothanai.py  → kuriyaakkam/sothanai_mudivu.json
"""
import json, sys, collections
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from senthamil_marabu import kuri as K  # noqa: E402

M = json.loads((HERE.parent / "sources/moolam.json").read_text("utf-8"))
ADH = {"ezhu": "எழுத்து", "sol": "சொல்", "porul": "பொருள்"}


def words(codes):
    w, cur = [], []
    for c in codes:
        if K.is_ezhuthu(c):
            cur.append(c)
        else:
            if cur: w.append(cur)
            cur = []
    if cur: w.append(cur)
    return w


def main():
    R = {"round_trip_bad": [], "size": collections.Counter(), "maathirai": {}, "maathirai_none": 0,
         "saarbu": collections.Counter(), "vithi": {}, "distinct": set()}
    allw = []
    for sid, text in M.items():
        c = K.encode(text)
        if K.decode(c) != text:
            R["round_trip_bad"].append(sid)
        c = K.saarbu_kuri(c)
        if K.decode(c) != text:
            R["round_trip_bad"].append(sid + " (சார்பு)")
        R["size"]["unicode_cp"] += len(text)
        R["size"]["utf8"] += len(text.encode("utf-8"))
        R["size"]["utf16"] += len(text.encode("utf-16-le"))
        R["size"]["marabu_units"] += len(c)
        R["size"]["ezhuthu"] += sum(1 for x in c if K.is_ezhuthu(x))
        R["size"]["tamil_cp"] += sum(1 for ch in text if "஀" <= ch <= "௿")
        a = sid.split(".")[0]
        for x in c:
            if K.is_ezhuthu(x):
                R["distinct"].add(x & ~(7 << 12))
                f = K.fields(x)
                if f["saarbu"]:
                    R["saarbu"][K.SAARBU[f["saarbu"]]] += 1
                m = K.maathirai(x)
                if m is None:
                    R["maathirai_none"] += 1
                else:
                    R["maathirai"][a] = R["maathirai"].get(a, Fraction(0)) + m
        allw += [(sid, w) for w in words(c)]
    F = K.fields
    V = collections.defaultdict(list)
    NEXT = {}
    for (s1, w1), (s2, w2) in zip(allw, allw[1:]):
        if s1 == s2:
            NEXT[id(w1)] = w2
    # விதிச் சோதனை சொல், பொருள் அதிகாரப் பாடத்தில் மட்டும் — எழுத்ததிகாரப் பாடம் பழைய அச்சுச் சொற்பிரிப்பு
    # (எ.கா. "எழுத்தெனப் படுப"); ஓரெழுத்துச் சொல் எழுத்தின் தம் பெயராக வருவது விலக்கு (எழு. 66).
    for sid, w in allw:
        if sid.startswith("ezhu") or len(w) == 1:
            continue
        f0, fl = F(w[0]), F(w[-1])
        if f0["inam"] and f0["uyir"] == 0:
            V["எழு. 60 — மெய் மொழிமுதல்"].append((sid, K.decode(w)))
        if (f0["inam"], f0["idam"]) == (3, 3) and f0["uyir"] in (3, 5):          # வ + உ ஊ ஒ ஓ (எழு. 63)
            V["எழு. 63 — வு வூ வொ வோ மொழிமுதல்"].append((sid, K.decode(w)))
        if (f0["inam"], f0["idam"]) == (3, 0) and not (f0["uyir"] == 1 and f0["alavu"] == 1):   # எழு. 65
            V["எழு. 65 — யா அல்லாத யகர முதல்"].append((sid, K.decode(w)))
        if fl["uyir"] == 7:
            V["எழு. 69 — ஔ இறுதி"].append((sid, K.decode(w)))
        if fl["inam"] and fl["uyir"] == 0 and (fl["inam"] == 1 or (fl["inam"], fl["idam"]) == (2, 0)):
            nxt = NEXT.get(id(w))
            fn = F(nxt[0]) if nxt else None
            if fn and fn["inam"] == 1:                 # அடுத்த சொல் வல்லின முதல் — புணர்ச்சியால் வந்த ஒற்று (எழு. 108, 109)
                V["எழு. 78 — புணர்ச்சி ஒற்று (வருமொழி வல்லினம்)"].append((sid, K.decode(w)))
            else:
                V["எழு. 78 — வல்லினம் / ங புள்ளியிறுதி"].append((sid, K.decode(w)))
        for x, y in zip(w, w[1:]):
            fx, fy = F(x), F(y)
            if fx["inam"] == 3 and fx["idam"] in (1, 4) and fx["uyir"] == 0 and (fy["inam"], fy["idam"]) == (fx["inam"], fx["idam"]):
                V["எழு. 30 — ர்ர, ழ்ழ"].append((sid, K.decode(w)))
    # எழு. 143 — இன மெல்லெழுத்து பிட் செயலால், பிறப்பு நூற்பாக்களோடு ஒப்பு
    pair = {K.decode([x]): K.decode([K.ina_mellezhuthu(x)]) for x in K.encode("கசடதபற")}
    R["vithi"] = {k: {"meeral": len(v), "edu": v[:5]} for k, v in V.items()}
    for k in ["எழு. 60 — மெய் மொழிமுதல்", "எழு. 63 — வு வூ வொ வோ மொழிமுதல்", "எழு. 65 — யா அல்லாத யகர முதல்",
              "எழு. 69 — ஔ இறுதி", "எழு. 78 — வல்லினம் / ங புள்ளியிறுதி", "எழு. 30 — ர்ர, ழ்ழ",
              "எழு. 78 — புணர்ச்சி ஒற்று (வருமொழி வல்லினம்)"]:
        R["vithi"].setdefault(k, {"meeral": 0, "edu": []})
    R["ina_mellezhuthu_143"] = pair
    R["words"] = len(allw)
    R["distinct"] = len(R["distinct"])
    R["maathirai"] = {ADH[k]: str(v) for k, v in R["maathirai"].items()}
    R["maathirai_mottham"] = str(sum(Fraction(v) for v in R["maathirai"].values()))
    R["size"] = dict(R["size"]); R["saarbu"] = dict(R["saarbu"])
    (HERE / "sothanai_mudivu.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), "utf-8")
    print(json.dumps({k: R[k] for k in ["round_trip_bad", "size", "distinct", "words", "maathirai",
                                         "maathirai_mottham", "maathirai_none", "saarbu", "ina_mellezhuthu_143"]},
                     ensure_ascii=False))
    for k, v in R["vithi"].items():
        print(k, v["meeral"], v["edu"][:3])
    if R["round_trip_bad"]:
        sys.exit("முன்–பின் மாற்ற வேறுபாடு")


if __name__ == "__main__":
    main()
