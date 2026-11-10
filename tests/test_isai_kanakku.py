"""பிறன் கோள் — சப்த தாளம், மேளகர்த்தா (pirankol/). மூலத்தோடு ஒப்பிட்டுச் சோதனை."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pirankol.isai_kanakku import thaalam, thaalangal, melakartha, melakarthagal, en_of

# karnatik.com «Taala table» — திஸ்ர, சதுஸ்ர, கண்ட, மிஸ்ர, சங்கீர்ண
TABLE = {"துருவ": [11, 14, 17, 23, 29], "மட்டிய": [8, 10, 12, 16, 20], "ரூபக": [5, 6, 7, 9, 11], "ஜம்பை": [6, 7, 8, 10, 12],
         "திரிபுடை": [7, 8, 9, 11, 13], "அட": [10, 12, 14, 18, 22], "ஏக": [3, 4, 5, 7, 9]}


def test_35_thaalam():
    t = thaalangal()
    assert len(t) == 35 and [x["en"] for x in t] == list(range(1, 36))
    for x in t:
        j = ["திஸ்ர", "சதுஸ்ர", "கண்ட", "மிஸ்ர", "சங்கீர்ண"].index(x["jaathi"])
        assert x["aksharam"] == TABLE[x["thaalam"]][j], x
    assert thaalam("திரிபுடை", "சதுஸ்ர")["aksharam"] == 8          # ஆதி தாளம்


def test_72_melakartha():
    m = melakarthagal()
    assert len({tuple(x["arai"]) for x in m}) == 72
    for x in m:
        a = x["arai"]
        assert a == sorted(a) and len(set(a)) == 7 and a[0] == 0 and a[4] == 7
        assert en_of(a) == x["en"]
    assert melakartha(29)["arai"] == [0, 2, 4, 5, 7, 9, 11]          # தீரசங்கராபரணம்
    assert melakartha(22)["arai"] == [0, 2, 3, 5, 7, 9, 10]          # கரகரப்பிரியா
    assert melakartha(15)["suram"] == ["ஸ", "ரி1", "க3", "ம1", "ப", "த1", "நி3"]   # மாயாமாளவகௌளை
    assert melakartha(65)["suram"] == ["ஸ", "ரி2", "க3", "ம2", "ப", "த2", "நி3"]   # மேசகல்யாணி
    assert melakartha(8)["suram"] == ["ஸ", "ரி1", "க2", "ம1", "ப", "த1", "நி2"]    # ஹனுமத்தோடி
    assert melakartha(28)["suram"] == ["ஸ", "ரி2", "க3", "ம1", "ப", "த2", "நி2"]   # ஹரிகாம்போஜி
    assert melakartha(1)["chakram"] == "இந்து" and melakartha(72)["chakram"] == "ஆதித்ய"
    assert melakartha(37)["suram"][3] == "ம2" and melakartha(36)["suram"][3] == "ம1"


def test_ezh_perum_paalai():
    from pirankol.isai_kanakku import paalaigal
    # நா. மம்மது (கீற்று): செம்பாலை = அரிகாம்போதி தொடங்கி — கணக்கும் அதே வரிசை தர வேண்டும்
    assert [x[2] for x in paalaigal(28)] == [28, 20, None, 29, 22, 8, 65]
    assert paalaigal(28)[2][1] == [0, 1, 3, 5, 6, 8, 10]              # இரு மத்திமம் (5, 6), பஞ்சமம் (7) இல்லை
    # Wikipedia «Pann»: செம்பாலை = சங்கராபரணம் தொடங்கி — முதல் ஆறு
    assert [x[2] for x in paalaigal(29)][:6] == [29, 22, 8, 65, 28, 20]
    assert paalaigal(29)[6][2] is None
