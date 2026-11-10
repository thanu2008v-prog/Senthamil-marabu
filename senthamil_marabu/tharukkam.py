"""ஒரு நூற்பாவின் தருக்க வாய்பாட்டை இயக்கிப் பார்த்தல் (THOGUPPU §24).

    python3 -m senthamil_marabu.tharukkam எழு.3
    python3 -m senthamil_marabu.tharukkam ezhu.401
"""
import sys
import senthamil_marabu as sm

PAD = {"எழு": "ezhu", "சொல்": "sol", "பொருள்": "porul"}
KAD = {"ezhu": "ezhuthu", "sol": "sol", "porul": "porul"}


def id_of(s):
    a, n = s.replace(" ", "").rstrip(".").rsplit(".", 1)
    return f"{PAD.get(a, a)}.{int(n)}"


def kaattu(sid):
    t = sm.tharukkam(sid)
    a, n = sid.split(".")
    m = next(r["moolam"] for r in sm.sutras() if r["padalam"] == KAD[a] and r["sutra"] == int(n))
    out = [f"நூற்பா  : {sid}", "மூலம்   : " + m.replace("\n", " / "), f"வகை     : {t['vagai']}  ({', '.join(t['murai'])})",
           f"வாய்பாடு: {t['vaaipaadu']}", f"நிலை    : {t['nilai']}", f"இயக்கம் : {t['iyakka_nilai']}"]
    out += [f"   • {s['vagai']}: {s['vilaivu']} — {'சரி' if s['sari'] else 'தீரவில்லை' if s['sari'] is None else 'மாறுபாடு'}" for s in t.get("seyal", [])]
    return "\n".join(out)


if __name__ == "__main__":
    for arg in sys.argv[1:] or ["எழு.3"]:
        print(kaattu(id_of(arg)), end="\n\n")
