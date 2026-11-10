"""மரபு ஒருங்குறி மாதிரியின் சோதனை — 1602 சூத்திரம்; பண்புக் கோப்பு (panbu.tsv) உருவாக்கம்.
python3 orunguri/sothanai.py → orunguri/panbu.tsv, orunguri/sothanai_mudivu.json
"""
import json, sys, collections, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from senthamil_marabu import orunguri as O  # noqa: E402

M = json.loads((HERE.parent / "sources/moolam.json").read_text("utf-8"))


def main():
    R = {"round_trip_bad": [], "invalid": [], "cp": collections.Counter()}
    words = set()
    for sid, t in M.items():
        m = O.to_model(t)
        if O.to_unicode(m) != t:
            R["round_trip_bad"].append(sid)
        if not O.valid(m):
            R["invalid"].append(sid)
        R["cp"]["unicode_tamil"] += sum(1 for ch in t if "஀" <= ch <= "௿")
        R["cp"]["model_tamil"] += sum(1 for ch in m if O.BASE <= ord(ch) < O.BASE + 128)
        R["cp"]["unicode_utf8"] += len(t.encode("utf-8"))
        R["cp"]["model_utf8"] += len(m.encode("utf-8"))
        if not sid.startswith("ezhu"):
            words.update(re.split(r"\s+", t.strip()))
    words = sorted(w for w in words if w)
    by_uni = sorted(words)                                   # யூனிகோடு குறி வரிசை (இருமக் கூட்டு)
    by_nool = sorted(words, key=O.collate_key)               # நூல் வரிசை
    R["words"] = len(words)
    R["order_same_position"] = sum(a == b for a, b in zip(by_uni, by_nool))
    # யூனிகோடு வரிசை நூல் வரிசைக்கு மாறும் எடுத்துக்காட்டு: ன/ற/ழ/வ
    pairs = [("ன", "ப"), ("ற", "ல"), ("ழ", "வ"), ("க்", "க")]
    R["order_examples"] = []
    for a, b in pairs:
        R["order_examples"].append({"pair": [a, b], "unicode": sorted([a, b]), "nool": sorted([a, b], key=O.collate_key)})
    R["cp"] = dict(R["cp"])
    R["assigned"] = len(O.CHART)
    R["by_kind"] = dict(collections.Counter(c["kind"] for c in O.CHART.values()))
    (HERE / "sothanai_mudivu.json").write_text(json.dumps(R, ensure_ascii=False, indent=1), "utf-8")
    cols = ["குறி", "வடிவம்", "பெயர்", "வகை", "இனம்", "அளவு", "மாத்திரை", "பிறப்பு", "மொழிமுதல்", "மொழியிறுதி", "குறிப்பு", "சான்று"]
    rows = ["\t".join(cols)]
    for off in sorted(O.CHART):
        c = O.CHART[off]
        pp = c.get("pirappu"); mu = c.get("muthal"); ir = c.get("iruthi")
        rows.append("\t".join([f"U+{c['cp']:04X}", c["uni"] or "◌", c["name"], c["kind"], c.get("inam", ""),
                               c.get("alavu", ""), c.get("maathirai", ""),
                               f"{pp[0]} (எழு. {pp[1]})" if pp else "",
                               (f"{mu[0]} (எழு. {mu[1]})" if mu else ""), (f"{ir[0]} (எழு. {ir[1]})" if ir else ""),
                               c.get("note", ""), c.get("saanru", "")]))
    (HERE / "panbu.tsv").write_text("\n".join(rows) + "\n", "utf-8")
    print(json.dumps(R, ensure_ascii=False))
    if R["round_trip_bad"] or R["invalid"]:
        sys.exit("சோதனைப் பிழை")


if __name__ == "__main__":
    main()
