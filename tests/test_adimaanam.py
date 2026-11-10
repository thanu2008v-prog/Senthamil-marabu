"""கலப்பு அடிமானம் (§18) — 247 கட்டம், இரு வழி மாற்றம், நூலின் இணைகள் எண் செயலாதல்."""
from senthamil_marabu.adimaanam import en, ezhuthu, sol_en, en_sol, RA, RB


def test_247_kattam():
    assert (RA, RB) == (19, 13)
    allv = [ezhuthu(n) for n in range(RA * RB)]
    assert len(set(allv)) == 247
    assert all(en(e) == n for n, e in enumerate(allv))
    assert ezhuthu(0) == "ஃ" and ezhuthu(1) == "அ" and ezhuthu(13) == "க்" and ezhuthu(14) == "க" and ezhuthu(246) == "னௌ"


def test_sol():
    for w in ["தமிழ்", "அஃது", "எழுத்து", "நூல்", "கண்ணிமை", "மாத்திரை"]:
        assert en_sol(sol_en(w)) == w
    assert sol_en("தமிழ்") == [92, 133, 195]


def test_ina_mellezhuthu_plus_13():
    # எழு. 143 இன மெல்லெழுத்து; வல்–மெல் இணை ஒரே பிறப்பிடம் (எழு. 89–97)
    for val, mel in zip("கசடதபற", "ஙஞணநமன"):
        assert en(mel) - en(val) == RB


def test_kuril_nedil_plus_1():
    # எழு. 3, 4 — குறில் ஐந்துக்கும் நெடில் இணை
    for k, n in zip("அஇஉஎஒ", "ஆஈஊஏஓ"):
        assert en(n) - en(k) == 1


def test_uyirmei_kootal():
    # எழு. 17 — மெய் (புள்ளியொடு) + உயிர் = உயிர்மெய்: எண்ணில் கூட்டல்
    for m in ["க்", "ழ்", "ன்"]:
        for u in "அஇஔ":
            assert en(m) + en(u) == en(ezhuthu(en(m) + en(u)))
    assert en("க்") + en("அ") == en("க")
