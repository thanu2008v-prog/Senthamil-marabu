"""v1 JSONL (data/sutras) + இருக்கும் உரை (sources/urai.json) → v2 JSONL (data_v2).

நூல் கூறும் அடுக்குப் பிரிப்பு (பொருள். 647–650):
  * உரைப் பத்தியின் "எடுத்துக்காட்டு (648): …" பகுதி காண்டிகைக்கு நகர்கிறது
    (ஏதுவும் எடுத்துக்காட்டும் காண்டிகையின் பணி — பொருள். 648).
  * "இயைபு (649): …" பகுதியில் சுட்டப்படும் நூற்பாக்கள் urai.iyaipu ஆகின்றன.
  * "மறுதலைக் கடாஅ (650): … ? விடை: …" → urai.maruthalai.
  * "வகை (645): விதி | விலக்கு (எழு. N-க்கு) | விதி-விலக்கு ·" → urai.vagai, urai.vilakkukkuriyathu.
python3 scripts/migrate_v2.py
"""
import json, glob, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from thunivu import split_text, reconcile, dedup_ethu
from utthi import tag as utthi_tag
from aayvugal import build as _aayvu_build, remap as _remap
_A2N = _aayvu_build()[2]   # «ஆய்வு N» — நூலின் பிற்சேர்க்கை எண்ணுக்கு (மூலத்தில் 29–33 இருமுறை)  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
PRE = {"எழு": "ezhu", "சொல்": "sol", "பொருள்": "porul"}
ADH = {"ezhuthu": "ezhu", "sol": "sol", "porul": "porul"}
LABEL = r"(வகை \(645\)|இயைபு \(649\)|எடுத்துக்காட்டு \(648\)|எண் \(நூலுள்[^)]*\)|எண்|நிலை|மறுதலைக் கடாஅ \(650\)|கடாஅ \(650\)|மறுதலை|அளவு|ஐயம்)\s*:"
NILAI = {"DIRECT": "நூலில் நேரடியாக", "AMBIGUOUS": "ஒருதலை அன்மை", "NOT_IN_TEXT": "நூலில் இல்லை",
         "SCOPE_DECLARED": "ஒருதலை அன்மை", "DERIVED": "ஒருதலை அன்மை", "OTHER_SOURCE": "நூலில் இல்லை"}


def refs_in(text, default_adh):
    out = []
    for a, rng in re.findall(r"(எழு|சொல்|பொருள்)\.\s*([\d,\s–\-]+)", text):
        for part in re.split(r",\s*", rng.strip(" ,")):
            m = re.match(r"(\d+)\s*[–\-]\s*(\d+)$", part)
            nums = range(int(m[1]), int(m[2]) + 1) if m else [int(part)] if part.isdigit() else []
            out += [f"{PRE[a]}.{n}" for n in nums]
    return list(dict.fromkeys(out))


def segments(text):
    """உரைப் பத்தியை (குறி, உள்ளடக்கம்) பகுதிகளாகப் பிரிக்கும்."""
    parts = re.split(LABEL, text)
    segs = [("", parts[0].strip())] if parts[0].strip() else []
    for i in range(1, len(parts), 2):
        segs.append((parts[i], parts[i + 1].strip()))
    return segs


MOOLAM = json.loads((ROOT / "sources/moolam.json").read_text("utf-8"))
_n = lambda s: re.sub(r"[\s/]+", "", s)


def owner(q, own):
    """எண் சுட்டப்படாத மேற்கோளின் உரிய நூற்பா: தன் நூற்பாவில் இருந்தால் அது; இல்லையேல் நூலுள் ஒரே இடம்."""
    if _n(q) in _n(MOOLAM[own]):
        return own
    hits = [k for k, v in MOOLAM.items() if _n(q) in _n(v)]
    return hits[0] if len(hits) == 1 else None


def quotes(text, own):
    out = []
    for m in re.finditer(r'"([^"]+)"\s*(?:\((எழு|சொல்|பொருள்)\.\s*(\d+))?', text):
        frm = f"{PRE[m[2]]}.{m[3]}" if m[2] else owner(m[1], own)
        if frm:                      # பெயர்க் குறி ("-கரம்" போன்றவை) மேற்கோள் அல்ல
            out.append({"text": m[1], "from": frm})
    return out


def load_struct():
    import importlib.util
    out = {}
    for p in sorted((ROOT / "sources").glob("urai_othu*.py")):
        spec = importlib.util.spec_from_file_location(p.stem, p)
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        out.update(mod.U)
    # வேறு தளத்தில் எழுதப்பட்ட உரை (urai_kit/KATTALAI.md வடிவம்): sources/urai_*othu*.json
    for p in sorted((ROOT / "sources").glob("urai_*othu*.json")):
        for d in json.loads(p.read_text("utf-8")):
            e = {k: d[k] for k in ("ethu", "urai") if d.get(k)}
            if d.get("eduthukkaattu"):
                e["edu"] = d["eduthukkaattu"]
            out[d["id"]] = e
    return out


STRUCT = load_struct()
ETHU654 = {k: v for k, v in json.loads((ROOT / "sources/ethu_654.json").read_text("utf-8")).items() if k != "_"}
ETHU648 = {k: v for k, v in json.loads((ROOT / "sources/ethu_648.json").read_text("utf-8")).items() if k != "_"}


def main():
    urai_src = json.loads((ROOT / "sources/urai.json").read_text("utf-8"))
    out_dir = ROOT / "data_v2"; out_dir.mkdir(exist_ok=True)
    n = moved = 0
    for p in sorted(glob.glob(str(ROOT / "data/sutras/*/*.jsonl"))):
        recs = []
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            v = r.get("verification") or {}
            k = {"porul": r["kaandigai"]}
            if v.get("stated") is not None or v.get("computed") is not None:
                k["en"] = {"kooruvathu": v.get("stated"), "enniyathu": v.get("computed")}
            rec = {"id": r["id"], "pindam": 1, "padalam": r["adhikaram"], "othu": r["othu"],
                   "sutra": r["sutra"], "moolam": r["verse"], "kaandigai": k,
                   "nilai": NILAI.get(r["kuri"], "ஒருதலை அன்மை"),
                   "kanini": r["computer"], "links": r.get("links", [])}
            t = urai_src.get(r["id"])
            if t:
                u = {"iyaipu": [], "text": ""}
                keep = []
                for lab, body in segments(t):
                    if lab.startswith("எடுத்துக்காட்டு"):
                        k.setdefault("eduthukkaattu", []).extend(quotes(body, r["id"]))
                        k["ethu"] = (k.get("ethu", "") + " " + body).strip()
                        moved += 1
                        continue
                    if lab.startswith("வகை"):     # "வகை (645): விலக்கு (எழு. 4-க்கு) ·"
                        head, _, rest = body.partition(" · ")
                        vm = re.match(r"(விதி-விலக்கு|விலக்கு|விதி)", head)
                        if vm:
                            u["vagai"] = vm[1]
                            vl = re.search(r"\(([^()]*)-க்கு\)", head)
                            if vl:
                                u["vilakkukkuriyathu"] = refs_in(vl[1], ADH[r["adhikaram"]])
                        if rest.strip():
                            keep.append(rest.strip())
                        continue
                    if lab.startswith("இயைபு"):
                        u["iyaipu"] += [x for x in refs_in(body, ADH[r["adhikaram"]]) if x != r["id"]]
                    if lab.startswith("மறுதலை") or lab.startswith("கடாஅ"):
                        m = re.match(r"(.+?\?)\s*(?:விடை:)?\s*(.*)", body)
                        if m:
                            u["maruthalai"] = [{"kadaa": m[1], "maattram": m[2] or body,
                                                "saanru": quotes(body, r["id"])}]
                    if lab.startswith("நிலை") and len(body) <= 300:
                        u["thunivu"] = body
                    else:
                        if lab.startswith("ஐயம்") or lab.startswith("நிலை"):
                            u["_aiyam"] = body
                        keep.append(f"{lab}: {body}" if lab else body)
                if not u["iyaipu"]:          # குறியிடாத உரை: உரையுள் சுட்டப்படும் நூற்பாக்களே இயைபு (649)
                    u["iyaipu"] = [x for x in refs_in(t, ADH[r["adhikaram"]]) if x != r["id"]]
                u["iyaipu"] = list(dict.fromkeys(u["iyaipu"]))
                u["text"] = " ".join(keep)
                rec["urai"] = u
            up = STRUCT.get(r["id"])
            if up:                                   # கட்டமைந்த உரை (sources/urai_othuNN.py)
                if up.get("ethu"):
                    k["ethu"] = up["ethu"]
                if up.get("edu"):
                    k.setdefault("eduthukkaattu", []).extend(up["edu"])
                u = rec.setdefault("urai", {"iyaipu": [], "text": ""})
                for f in ("vagai", "vilakkukkuriyathu"):
                    if f in up:
                        u[f] = up[f]
                for f, v in (up.get("urai") or {}).items():
                    u[f] = v
            if not k.get("ethu") and rec["id"] in ETHU648:   # ஏதுவும் எடுத்துக்காட்டும் இல்லாதவை (648) — sources/ethu_648.json
                k["ethu"] = ETHU648[rec["id"]]
                k.setdefault("eduthukkaattu", []).extend(quotes(k["ethu"], rec["id"]))
            if rec["id"] in ETHU654:                 # பொருளையே மீண்டும் கூறிய ஏதுவுக்கு மாற்று (654) — sources/ethu_654.json
                k["ethu"] = ETHU654[rec["id"]]
                k["eduthukkaattu"] = quotes(k["ethu"], rec["id"])
            if k.get("ethu"):                        # கூறியது கூறல் நீக்கம் (654)
                k["ethu"] = dedup_ethu(k["porul"], k["ethu"])
            u = rec.get("urai")
            if u:                                    # ஒரே துணிவு (650) — scripts/thunivu.py
                txt, tail = split_text(u.get("text", ""))
                u["text"] = txt
                u["thunivu"], rec["nilai"] = reconcile(rec["nilai"], u.get("thunivu") or tail, u.pop("_aiyam", ""))
            k["porul"] = _remap(k["porul"], _A2N)
            if k.get("ethu"):
                k["ethu"] = _remap(k["ethu"], _A2N)
            if rec.get("urai"):
                rec["urai"]["text"] = _remap(rec["urai"]["text"], _A2N)
                rec["urai"]["thunivu"] = _remap(rec["urai"]["thunivu"], _A2N)
            ut = utthi_tag(rec["id"], rec["moolam"])  # முப்பத்திரு உத்தி — சூத்திரச் சொல் அடையாளம் (644, 656)
            if ut:
                rec["utthi"] = ut
            recs.append(rec); n += 1
        a, o = Path(p).parent.name, Path(p).name
        (out_dir / a).mkdir(exist_ok=True)
        with open(out_dir / a / o, "w", encoding="utf-8") as f:
            for rec in recs:
                f.write(json.dumps(rec, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"v2: {n} records; உரையிலிருந்து காண்டிகைக்கு நகர்ந்த எடுத்துக்காட்டுப் பகுதிகள்: {moved}")


if __name__ == "__main__":
    main()
