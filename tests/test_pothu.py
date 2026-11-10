"""பொதுச் சூத்திர வடிவம் — வரையறை, சான்று, மாட்டேறு."""
import json
from pathlib import Path
import jsonschema
import senthamil_marabu as sm

ROOT = Path(__file__).resolve().parent.parent
SCH = json.loads((ROOT / "schema/pothu.v1.schema.json").read_text("utf-8"))


def test_ellaam_varaiyaraikku_inangum():
    ids = {r["id"] for r in sm.sutras()}
    P = [sm.pothu(i) for i in ids]
    assert len(P) == 1602
    V = jsonschema.Draft202012Validator(SCH)                    # ஒருமுறை தொகுத்து 1602-க்கும் (முன்பு ஒவ்வொன்றுக்கும் மறு தொகுப்பு)
    for r in P:
        V.validate(r)


def test_saanru_moolathil():
    for r in sm.sutras():
        m = r["moolam"].replace(" ", "").replace("\n", "")
        for f, ws in sm.pothu(r["id"])["saanru"].items():
            for w in ws:
                assert w.replace(" ", "") in m, (r["id"], f, w)


def test_maatteru_sangili():
    # ஓகார இறுதி ஏகார இயற்றே (289) → ஏ ஊ இயற்றே (274) → ஊ ஆ இயற்றே (264) → ஆ அ இயற்றே (221) → அகர இறுதி (203)
    assert sm.maatteru_sangili("ezhu.289") == ["ezhu.289", "ezhu.274", "ezhu.264", "ezhu.221", "ezhu.203"]


def test_murai():
    assert {r["id"] for r in sm.by_murai("கட்டாயம்")} >= {"ezhu.156", "ezhu.199"}
    assert "ezhu.3" in {r["id"] for r in sm.by_murai("புலவர் கூற்று")}


def test_maatteru_vattam_illai():
    import re
    for r in sm.sutras():
        c = sm.maatteru_sangili(r["id"])
        assert len(c) == len(set(c))


def test_punarchi_porul_maatteruvodu_ottathu():
    """புணர்ச்சிப் பொறியின் விதி 203 அ, ஆ, ஈ, உ, ஊ, ஏ, ஓ ஈறுகளுக்கு ஒன்றே — மாட்டேற்று வரைபடமும் அவ்வைந்தையும் எழு. 203 க்கே கொண்டுசெல்ல வேண்டும்."""
    from senthamil_marabu.punarchi import RULES
    r203 = next(r for r in RULES if r["id"] == "203")
    for s in r203["sutra"][1:]:
        sid = "ezhu." + s.split()[1]
        assert sm.maatteru_sangili(sid)[-1] == "ezhu.203", sid


def test_tharukkam_iyakkam():
    """§24 — ஒவ்வொரு நூற்பாவுக்கும் வாய்பாடு; இயக்கியவற்றுள் மாறுபாடு இல்லை."""
    import senthamil_marabu as sm
    t = sm.tharukkam("ezhu.3")
    assert t["vagai"] == "எண்ணல்" and "= 5" in t["vaaipaadu"] and t["iyakka_nilai"] == "இயங்கியது — சரி"
    assert sm.tharukkam("ezhu.247")["murai"] == ["நேர்க் கூற்று"]          # «ஐய மின்றே» மறுப்பு அன்று
    assert "¬" not in sm.tharukkam("ezhu.389")["vaaipaadu"]               # «கடிநிலை யின்றே» இசைவு
    allr = [sm.tharukkam(r["id"]) for r in sm.sutras()]
    assert len(allr) == 1602
    assert not [x["id"] for x in allr if x["iyakka_nilai"] == "இயங்கியது — மாறுபாடு"]
    assert sum(1 for x in allr if x["iyakka_nilai"] == "இயங்கியது — சரி") >= 540
