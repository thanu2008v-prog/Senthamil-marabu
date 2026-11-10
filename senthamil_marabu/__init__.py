"""செந்தமிழ் மரபு — 1602 தொல்காப்பிய நூற்பா, காண்டிகை, உரை, துணிவு: ஆய்வாளர் பயன்பாட்டுக்கான Python தொகுப்பு.

    import senthamil_marabu as sm
    sm.get("ezhu.1")["moolam"]
    len(sm.sutras())                          # 1602
    sm.by_nilai("ஒருதலை அன்மை")               # நூல் தீர்க்காதவை
    sm.search("மாத்திரை", fields=("moolam",))
    df = sm.to_dataframe()                    # pandas இருந்தால்

தரவின் புலங்கள்: docs/TARAVU.md. உரிமம்: CC BY-NC 4.0 (சூத்திரங்கள் பொதுவுடைமை).
மேற்கோள்: Varnakulasingam, T. (2026). செந்தமிழ் மரபு. DOI 10.5281/zenodo.24011591.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

__version__ = "1.0.0"
DOI = "10.5281/zenodo.24011590"
LICENSE = "CC-BY-NC-4.0"
PADALAM = {"ezhuthu": "எழுத்து", "sol": "சொல்", "porul": "பொருள்"}
NILAI = ("நூலில் நேரடியாக", "ஒருதலை அன்மை", "நூலில் இல்லை")

_HERE = Path(__file__).resolve().parent


def _data_files():
    packed = _HERE / "data" / "sutras.jsonl"
    if packed.exists():
        return [packed]
    repo = sorted((_HERE.parent / "data_v2").glob("*/*.jsonl"))     # களஞ்சியத்திலிருந்து நேரடியாக
    if repo:
        return repo
    raise FileNotFoundError("தரவு இல்லை: senthamil_marabu/data/sutras.jsonl அல்லது data_v2/")


@lru_cache(maxsize=1)
def _load():
    recs = [json.loads(l) for p in _data_files() for l in p.open(encoding="utf-8") if l.strip()]
    order = {"ezhu": 0, "sol": 1, "porul": 2}
    recs.sort(key=lambda r: (order[r["id"].split(".")[0]], int(r["id"].split(".")[1])))
    return recs, {r["id"]: r for r in recs}


def sutras():
    """எல்லாப் பதிவும், நூல் வரிசையில் (எழு. 1 … பொருள். 656)."""
    return list(_load()[0])


def get(sid):
    """ஒரு பதிவு — «ezhu.1», «sol.401», «porul.656»."""
    return _load()[1][sid]


@lru_cache(None)
def _pothu():
    for p in (Path(__file__).resolve().parent / "data/pothu.jsonl", Path(__file__).resolve().parent.parent / "pothu/pothu.jsonl"):
        if p.exists():
            return {r["id"]: r for r in (json.loads(l) for l in p.open(encoding="utf-8") if l.strip())}
    return {}


def pothu(sid):
    """பொதுச் சூத்திர வடிவம் — வகை, எழுவாய், நிபந்தனை, விளைவு, முறைமை, அளவு, மாட்டேறு, சான்று, நிலை (schema/pothu.v1.schema.json)."""
    return _pothu()[sid]


@lru_cache(None)
def _tharukkam():
    for p in (Path(__file__).resolve().parent / "data/tharukkam.jsonl", Path(__file__).resolve().parent.parent / "pothu/tharukkam.jsonl"):
        if p.exists():
            return {r["id"]: r for r in (json.loads(l) for l in p.open(encoding="utf-8") if l.strip())}
    return {}


def tharukkam(sid):
    """தருக்க வாய்பாடு, இயக்க விளைவு (seyal), இயக்க நிலை — docs/THOGUPPU.md §24."""
    return _tharukkam()[sid]


def by_murai(murai):
    """முறைமையால்: கட்டாயம், இசைவு, விலக்கின்மை, மறுப்பு, புலவர் கூற்று, மாட்டேறு, நேர்க் கூற்று."""
    return [_load()[1][i] for i, r in _pothu().items() if murai in r["murai"]]


def by_vagai(vagai):
    """வகையால்: வரையறை, எண்ணல், பகுப்பு, விதி, விலக்கு, மாட்டேறு, நெறி."""
    return [_load()[1][i] for i, r in _pothu().items() if r["vagai"] == vagai]


def maatteru_sangili(sid):
    """மாட்டேற்றுச் சங்கிலி: «ஓகார இறுதி ஏகார இயற்றே» → … → அடிப்படை விதி."""
    out, seen = [sid], {sid}
    while True:
        m = _pothu().get(out[-1], {}).get("maatteru")
        nxt = (m or {}).get("suttu") or []
        if not nxt or nxt[0] in seen:
            return out
        out.append(nxt[0]); seen.add(nxt[0])


def by_padalam(padalam):
    return [r for r in _load()[0] if r["padalam"] == padalam]


def by_othu(padalam, othu):
    return [r for r in _load()[0] if r["padalam"] == padalam and r["othu"] == othu]


def by_nilai(nilai):
    """துணிவின் நிலை: «நூலில் நேரடியாக», «ஒருதலை அன்மை», «நூலில் இல்லை»."""
    if nilai not in NILAI:
        raise ValueError(f"நிலை இவற்றுள் ஒன்று: {NILAI}")
    return [r for r in _load()[0] if r["nilai"] == nilai]


def by_utthi(peyar):
    """சூத்திரச் சொல்லில் அடையாளம் உள்ள உத்தி (பொருள். 656) — எ.கா. «ஆணை கூறல்»."""
    return [r for r in _load()[0] if any(u["peyar"] == peyar for u in r.get("utthi", []))]


def iyaipu(sid):
    """உரை கூறும் இயைபுச் சூத்திரங்கள் (பொருள். 649)."""
    return [get(x) for x in (get(sid).get("urai") or {}).get("iyaipu", []) if x in _load()[1]]


def cited_by(sid):
    """இச்சூத்திரத்தைக் காண்டிகையோ உரையோ சுட்டும் பதிவுகள்."""
    out = []
    for r in _load()[0]:
        refs = set(r.get("links", [])) | set((r.get("urai") or {}).get("iyaipu", []))
        refs |= {e["from"] for e in r["kaandigai"].get("eduthukkaattu", [])}
        if sid in refs and r["id"] != sid:
            out.append(r)
    return out


def _fields(r):
    k, u = r["kaandigai"], r.get("urai") or {}
    return {"moolam": r["moolam"], "kaandigai": k["porul"] + " " + (k.get("ethu") or ""),
            "urai": u.get("text", ""), "thunivu": u.get("thunivu", "")}


def search(text, fields=("moolam", "kaandigai", "urai", "thunivu")):
    """உரைத் தேடல் (இடைவெளி, வரி முறிவு புறக்கணிக்கப்படும்)."""
    norm = lambda s: "".join(s.split())
    t = norm(text)
    return [r for r in _load()[0] if any(t in norm(v) for f, v in _fields(r).items() if f in fields)]


def flat(r):
    """ஒரு பதிவை அட்டவணை வரியாக்கல்."""
    k, u = r["kaandigai"], r.get("urai") or {}
    return {"id": r["id"], "padalam": r["padalam"], "othu": r["othu"], "sutra": r["sutra"], "pindam": r.get("pindam"),
            "moolam": r["moolam"], "kaandigai_porul": k["porul"], "kaandigai_ethu": k.get("ethu", ""),
            "eduthukkaattu_count": len(k.get("eduthukkaattu", [])), "urai": u.get("text", ""), "vagai": u.get("vagai", ""),
            "iyaipu": ";".join(u.get("iyaipu", [])), "thunivu": u.get("thunivu", ""), "nilai": r["nilai"],
            "utthi": ";".join(x["peyar"] for x in r.get("utthi", [])), "kanini_kind": (r.get("kanini") or {}).get("kind", "")}


def to_dataframe():
    """pandas DataFrame — ஒவ்வொரு சூத்திரமும் ஒரு வரி."""
    import pandas as pd
    return pd.DataFrame([flat(r) for r in _load()[0]])


def info():
    recs = _load()[0]
    from collections import Counter
    return {"title": "செந்தமிழ் மரபு", "version": __version__, "doi": DOI, "license": LICENSE, "sutras": len(recs),
            "padalam": dict(Counter(r["padalam"] for r in recs)), "nilai": dict(Counter(r["nilai"] for r in recs))}


def _sid_from_text(text):
    s = text.strip().replace(" ", "")
    if not s:
        return None
    pad = {"ezhu": "ezhu", "எழு": "ezhu", "ezhuthu": "ezhu", "எழுத்து": "ezhu",
           "sol": "sol", "சொல்": "sol", "porul": "porul", "பொருள்": "porul"}
    m = re.fullmatch(r"(?:[eE]zhu|[eE]zhuthu|[sS]ol|[pP]orul|எழு|எழுத்து|சொல்|பொருள்)\.?\d+", s)
    if m:
        name = re.match(r"[A-Za-zஅ-ஊ]+", s).group(0).lower()
        n = int(re.search(r"\d+", s).group(0))
        return f"{pad.get(name, name)}.{n}"
    return None


_QUERY_STOPWORDS = {
    "அது", "அதில்", "அதன்", "அந்த", "என்ன", "என்னும்", "எது", "எதை", "எவை",
    "எங்கே", "எங்கு", "எப்போது", "ஏன்", "எப்படி", "எவ்வாறு", "எதனால்", "எதற்கு",
    "யார்", "யாது", "பற்றி", "குறித்து", "சொல்", "சொல்லுங்கள்", "கூறு", "கூறுங்கள்",
    "சொல்கிறது", "கூறுகிறது", "விளக்கு", "விளக்குங்கள்", "விளக்குகிறது", "குறிக்கிறது",
    "என்பது", "என்று", "என", "ஆகிய", "மற்றும்", "ஒரு", "நூல்", "நூலில்",
    "தொல்காப்பியம்", "தொல்காப்பியத்தில்",
    "the", "what", "which", "who", "where", "when", "why", "how", "does", "do",
    "is", "are", "was", "were", "about", "tell", "explain", "please", "this", "that",
}
_QUESTION_MARKERS = (
    "?", "என்ன", "எது", "எதை", "எவை", "எங்கே", "எங்கு", "எப்போது", "ஏன்",
    "எப்படி", "எவ்வாறு", "எதனால்", "எதற்கு", "யார்", "யாது", "பற்றி", "குறித்து",
    "what", "which", "who", "where", "when", "why", "how", "explain", "tell me",
)
_TAMIL_SUFFIXES = (
    "களுக்கு", "களினால்", "களிலிருந்து", "களுக்குள்", "களிடம்", "களோடு",
    "களில்", "களால்", "களின்", "களை", "த்திற்கு", "த்திலிருந்து", "த்தினால்",
    "த்தில்", "த்தால்", "த்துக்கு", "உடைய", "இருந்து", "உடன்", "ஆனது",
    "ஆகிய",     "ஆல்", "இல்", "இன்", "க்கு", "ஐ", "ஓடு", "ஆக", "கள்", "உம்", "ப்",
)


def _query_groups(question):
    terms = re.findall(r"[A-Za-z]+|[\u0B80-\u0BFF]+", question.lower())
    groups = []
    for term in terms:
        if term in _QUERY_STOPWORDS or len(term) < 2:
            continue
        forms = [term]
        if re.search(r"[\u0B80-\u0BFF]", term):
            stem = term
            for _ in range(2):
                suffix = next(
                    (suffix for suffix in _TAMIL_SUFFIXES
                     if stem.endswith(suffix) and len(stem) - len(suffix) >= 3),
                    None,
                )
                if not suffix:
                    break
                stem = stem[:-len(suffix)]
                if stem not in _QUERY_STOPWORDS and stem not in forms:
                    forms.append(stem)
        groups.append(forms)
    return groups


def _is_natural_question(question):
    q = question.lower()
    return any(marker in q for marker in _QUESTION_MARKERS)


def _nool_evidence(question, max_results):
    groups = _query_groups(question)
    if not groups:
        return {"type": "not_found", "query": question, "results": []}

    ranked = []
    for record in _load()[0]:
        fields = _fields(record)
        normalized = {name: "".join(text.lower().split()) for name, text in fields.items()}
        matches = []
        score = 0
        for forms in groups:
            weights = {"moolam": 3, "kaandigai": 2, "urai": 2, "thunivu": 1}
            found = [
                (weight, form)
                for form in forms
                for name, weight in weights.items()
                if "".join(form.split()) in normalized[name]
            ]
            if found:
                best_weight, matched_form = max(found, key=lambda match: match[0])
                matches.append(matched_form)
                score += best_weight
        if matches:
            ranked.append((len(matches), score, record, matches))

    ranked.sort(key=lambda item: (-item[0], -item[1], item[2]["id"]))
    required_matches = min(2, len(groups))
    ranked = [item for item in ranked if item[0] >= required_matches]
    return {
        "type": "evidence" if ranked else "not_found",
        "query": question,
        "results": [
            {"sutra": record, "matched_terms": matches}
            for _, _, record, matches in ranked[:max_results]
        ],
    }


def kel(question, max_results=5):
    """ஒரே நுழைவாயில்: நூல் சான்று, இலக்கணம், புணர்ச்சி, தேடல்.
    இயல்பான வினாக்களுக்கு பொருந்தும் நூற்பாக்களைத் திருப்பும்; புதிய விதியை உருவாக்காது.
    """
    q = (question or "").strip()
    if not q:
        raise ValueError("வினா இல்லை")

    if q.startswith("தேடு:"):
        term = q[4:].strip()
        return {"type": "search", "query": term, "results": search(term, fields=("moolam", "kaandigai", "urai", "thunivu"))[:max_results]}

    if q.startswith("சோதி:"):
        term = q[5:].strip()
        sid = _sid_from_text(term)
        if sid:
            return {"type": "sutra", "id": sid, "sutra": get(sid)}
        return {"type": "search", "query": term, "results": search(term, fields=("moolam", "kaandigai", "urai", "thunivu"))[:max_results]}

    sid = _sid_from_text(q)
    if sid:
        return {"type": "sutra", "id": sid, "sutra": get(sid)}

    if re.search(r"[+\=]", q):
        if "+" in q:
            left, right = [p.strip() for p in q.split("+", 1)]
        else:
            left, right = [p.strip() for p in q.split("=", 1)]
        if left and right:
            from .punarchi import punar
            out = punar(left, right)
            return {"type": "punarchi", "query": q, "results": out[:max_results]}

    m = re.fullmatch(r"(\d+)\s*(எழுத்தால்|எழுத்து|சொல்லால்|சொல்|பொருளால்|பொருள்|நூற்பா|சூத்திரம்)", q)
    if m:
        count = int(m.group(1))
        target = m.group(2)
        return {"type": "count", "query": q, "count": count, "target": target,
                "note": "முனைநிலை எண்/வகை வினா — நூற்பா/எழுத்து/சொல் பகுப்பு இன்னும் விரிவடைய வேண்டியுள்ளது."}

    if re.fullmatch(r"\d+\s*எழுத்தால்", q):
        count = int(re.match(r"\d+", q).group(0))
        return {"type": "count", "query": q, "count": count, "note": "எழுத்தால் பகுப்பின் தனியுரிமையை இங்கு நிரலாக்கவில்லை; இது ஒரு முனைநிலை வினா."}

    if _is_natural_question(q):
        return _nool_evidence(q, max_results)

    if re.search(r"[\u0B80-\u0BFF]", q):
        try:
            from .ilakkanam import check
            findings = check(q)["findings"]
            return {"type": "grammar", "query": q, "findings": findings[:max_results]}
        except Exception:
            pass

    results = search(q, fields=("moolam", "kaandigai", "urai", "thunivu"))[:max_results]
    if results:
        return {"type": "search", "query": q, "results": results}
    return _nool_evidence(q, max_results)
