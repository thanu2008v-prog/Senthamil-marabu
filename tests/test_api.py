"""ஆய்வாளர் தொகுப்பின் சோதனைகள் — pytest tests/test_api.py"""
import json, subprocess, shutil
from pathlib import Path
import pytest
import senthamil_marabu as sm
from senthamil_marabu import ilakkanam, yappu, kuri, orunguri

ROOT = Path(__file__).resolve().parent.parent
MOOLAM = json.loads((ROOT / "sources/moolam.json").read_text("utf-8"))


def test_counts():
    i = sm.info()
    assert i["sutras"] == 1602 and i["padalam"] == {"ezhuthu": 483, "sol": 463, "porul": 656}
    assert sum(i["nilai"].values()) == 1602


def test_moolam_unchanged():                         # பொருள். 652
    assert all(sm.get(k)["moolam"] == v for k, v in MOOLAM.items())


def test_packed_data_in_sync():
    import glob
    repo = {json.loads(l)["id"]: json.loads(l) for p in glob.glob(str(ROOT / "data_v2/*/*.jsonl")) for l in open(p, encoding="utf-8")}
    packed = {json.loads(l)["id"]: json.loads(l) for l in open(ROOT / "senthamil_marabu/data/sutras.jsonl", encoding="utf-8")}
    assert repo == packed, "python3 scripts/pack_data.py இயக்குக"


def test_schema():
    jsonschema = pytest.importorskip("jsonschema")
    S = json.loads((ROOT / "schema/sutra.v2.schema.json").read_text("utf-8"))
    v = jsonschema.Draft202012Validator(S)
    assert not [r["id"] for r in sm.sutras() if list(v.iter_errors(r))]


def test_examples_are_in_cited_sutra():              # பொருள். 648
    N = lambda s: "".join(s.replace("/", " ").split())
    for r in sm.sutras():
        for e in r["kaandigai"].get("eduthukkaattu", []):
            assert N(e["text"]) in N(sm.get(e["from"])["moolam"]), (r["id"], e)


def test_api():
    assert sm.get("ezhu.1")["padalam"] == "ezhuthu"
    assert all(r["nilai"] == "ஒருதலை அன்மை" for r in sm.by_nilai("ஒருதலை அன்மை"))
    assert sm.search("கண்ணிமை", fields=("moolam",))[0]["id"] == "ezhu.7"
    assert len(sm.by_othu("ezhuthu", 1)) > 0 and sm.cited_by("ezhu.8")
    with pytest.raises(ValueError):
        sm.by_nilai("தவறு")


def test_kel_entrypoint():
    sutra = sm.kel("ezhu.3")
    assert sutra["type"] == "sutra" and sutra["id"] == "ezhu.3"
    punar = sm.kel("மரம் + கிளை")
    assert punar["type"] == "punarchi" and punar["results"]
    search = sm.kel("தேடு: நிலம்")
    assert search["type"] == "search" and search["results"]
    count = sm.kel("247 எழுத்தால்")
    assert count["type"] == "count" and count["count"] == 247


def test_kel_natural_question_returns_nool_evidence():
    result = sm.kel("நிலம் எதை குறிக்கிறது?")
    assert result["type"] == "evidence"
    assert result["results"]
    assert any("நிலம்" in item["matched_terms"] for item in result["results"])
    assert all(item["sutra"]["id"] for item in result["results"])
    assert sm.kel("இயற்பியல் அணுவைப் பற்றி என்ன சொல்கிறது?")["type"] == "not_found"


def test_grammar_book_has_no_violation():
    for k, v in MOOLAM.items():
        assert not [f for f in ilakkanam.check(v)["findings"] if f["nilai"] == "மாறு"], k


def test_grammar_cases():
    rules = lambda t: [(f["word"], f["rule"], f["nilai"]) for f in ilakkanam.check(t)["findings"]]
    assert ("ரவி", "எழு. 61", "மாறு") in rules("ரவி வந்தான்")
    assert ("பஸ்", "சொல். 401", "இல்லை") in rules("பஸ் வந்தது")
    assert ("ஊருக்குச்", "எழு. 108", "புணர்ச்சி") in rules("ஊருக்குச் சென்றான்")
    assert ("பேக்", "எழு. 78", "மாறு") in rules("பேக் எடுத்தான்")
    assert rules("தமிழ் மொழி இனிது") == []


def test_asai():                                      # பொருள். 312, 313
    P = lambda w: [a["peyar"] for a in yappu.asai(w)]
    assert P("அகர") == ["நிரை", "நேர்"]
    assert P("காது") == ["நேர்பு"] and P("வரகு") == ["நிரைபு"] and P("அது") == ["நிரை"]
    assert P("எழுத்தெல்லாம்") == ["நிரை", "நேர்", "நேர்"]
    assert yappu.adi_vagai(10)[0] == "நேரடி"


def test_encodings_round_trip():
    for v in MOOLAM.values():
        assert kuri.decode(kuri.encode(v)) == v
        assert orunguri.to_unicode(orunguri.to_model(v)) == v


@pytest.mark.skipif(not shutil.which("node"), reason="node இல்லை")
def test_python_matches_web_page():
    js = r"""
const K=require(process.argv[1]+'/karuvi/logic.js');K.setBookWords(require(process.argv[1]+'/karuvi/bookwords.json'));
const t=process.argv[2];process.stdout.write(JSON.stringify(K.checkGrammar(t).findings.map(f=>[f.word,f.rule,f.nilai])));"""
    t = "ரவி நேற்று பஸ்ஸில் ஊருக்குச் சென்றான். தன் பேக் எடுத்துக்கொண்டு டாக்டர் வீட்டுக்குப் போனான். அளவு"
    out = subprocess.run(["node", "-e", js, str(ROOT), t], capture_output=True, text=True, check=True).stdout
    assert json.loads(out) == [[f["word"], f["rule"], f["nilai"]] for f in ilakkanam.check(t)["findings"]]
