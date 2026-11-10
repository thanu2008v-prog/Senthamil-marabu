"""பிறன் கோள் — நூலுக்கு வெளியே: கர்நாடக இசையின் சப்த தாளம், மேளகர்த்தா 72 — கணக்கால் உருவாக்கம்.

இவை «செந்தமிழ் மரபு» நூலில் இல்லை; நூல் இசையை «நரம்பின் மறை»க்கு விடுகிறது (எழு. 33). ஆகவே இந்நிரல் நூலின் தொகுப்பில்
(senthamil_marabu/) இல்லை; தனி அடைவு pirankol/. நூலோடு உள்ள தொடர்பு கணக்கு முறை ஒன்றே — கலப்பு அடிமானம் (THOGUPPU §18).

    from pirankol.isai_kanakku import thaalam, thaalangal, melakartha, melakarthagal
    thaalam("திரிபுடை", "சதுஸ்ர")   # ஆதி தாளம் — 8 அட்சரம்
    melakartha(29)                  # தீரசங்கராபரணம் — ஸ ரி2 க3 ம1 ப த2 நி3

மூலங்கள்: karnatik.com «Taala table» (35 தாளத்தின் அட்சர எண்ணிக்கை — சோதனையில் ஒப்பிடப்படுகிறது);
karnatik.com «Melakarta ragas» (72 பெயர்); Spardha School of Music (6 × 6 × 2 = 72 விதி).
"""
from itertools import combinations

# ── சப்த தாளம்: அங்கம் — லகு «|» (ஜாதியால் 3, 4, 5, 7, 9), த்ருதம் «0» (2), அனுத்ருதம் «U» (1)
THAALAM = {"துருவ": "|0||", "மட்டிய": "|0|", "ரூபக": "0|", "ஜம்பை": "|U0", "திரிபுடை": "|00", "அட": "||00", "ஏக": "|"}
JAATHI = {"திஸ்ர": 3, "சதுஸ்ர": 4, "கண்ட": 5, "மிஸ்ர": 7, "சங்கீர்ண": 9}
ANGAM = {"0": 2, "U": 1}


def thaalam(peyar, jaathi):
    """→ {thaalam, jaathi, angam, aksharam, en} ; en = 7 × 5 கலப்பு அடிமானத்தில் 1–35."""
    angam = THAALAM[peyar]
    l = JAATHI[jaathi]
    akshara = sum(l if a == "|" else ANGAM[a] for a in angam)
    en = list(THAALAM).index(peyar) * len(JAATHI) + list(JAATHI).index(jaathi) + 1
    return dict(thaalam=peyar, jaathi=jaathi, angam=angam, aksharam=akshara, en=en)


def thaalangal():
    return [thaalam(t, j) for t in THAALAM for j in JAATHI]


# ── மேளகர்த்தா: சுரத்தானம் — அரைச்சுர நிலை (ஸ = 0, மேல் ஸ = 12)
RI = {"ரி1": 1, "ரி2": 2, "ரி3": 3}
GA = {"க1": 2, "க2": 3, "க3": 4}
MA = {"ம1": 5, "ம2": 6}
DA = {"த1": 8, "த2": 9, "த3": 10}
NI = {"நி1": 9, "நி2": 10, "நி3": 11}


def _inai(a, b):
    """ஒரு சுரம் அடுத்ததற்குக் கீழே இருக்க வேண்டும் — ஏற்கத் தக்க இணைகள், மேளகர்த்தா வரிசைப்படி."""
    return [(x, y) for x in a for y in b if a[x] < b[y]]


RIGA, DANI = _inai(RI, GA), _inai(DA, NI)
assert len(RIGA) == len(DANI) == len(list(combinations(range(4), 2))) == 6     # ஒவ்வொன்றும் C(4,2) = 6

PEYAR = ["கனகாங்கி", "ரத்னாங்கி", "கானமூர்த்தி", "வனஸ்பதி", "மானவதி", "தானரூபி", "சேனாவதி", "ஹனுமத்தோடி", "தேனுகா",
         "நாடகப்பிரியா", "கோகிலப்பிரியா", "ரூபவதி", "காயகப்பிரியா", "வகுளாபரணம்", "மாயாமாளவகௌளை", "சக்கரவாகம்", "சூர்யகாந்தம்",
         "ஹாடகாம்பரி", "ஜங்காரத்வனி", "நடபைரவி", "கீரவாணி", "கரகரப்பிரியா", "கௌரிமனோகரி", "வருணப்பிரியா", "மாரரஞ்சனி",
         "சாருகேசி", "சரசாங்கி", "ஹரிகாம்போஜி", "தீரசங்கராபரணம்", "நாகானந்தினி", "யாகப்பிரியா", "ராகவர்த்தினி", "காங்கேயபூஷணி",
         "வாகதீஸ்வரி", "சூலினி", "சலநாட்டை", "சாலகம்", "ஜலார்ணவம்", "ஜாலவராளி", "நவநீதம்", "பாவனி", "ரகுப்பிரியா", "கவாம்போதி",
         "பவப்பிரியா", "சுபபந்துவராளி", "ஷட்விதமார்க்கிணி", "சுவர்ணாங்கி", "திவ்யமணி", "தவளாம்பரி", "நாமநாராயணி", "காமவர்த்தினி",
         "ராமப்பிரியா", "கமனஸ்ரமா", "விஸ்வம்பரி", "சியாமளாங்கி", "சண்முகப்பிரியா", "சிம்மேந்திரமத்யமம்", "ஹேமவதி", "தர்மவதி",
         "நீதிமதி", "காந்தாமணி", "ரிஷபப்பிரியா", "லதாங்கி", "வாசஸ்பதி", "மேசகல்யாணி", "சித்ராம்பரி", "சுசரித்ரா", "ஜோதிஸ்வரூபிணி",
         "தாதுவர்த்தினி", "நாசிகாபூஷணி", "கோசலம்", "ரசிகப்பிரியா"]
CHAKRAM = ["இந்து", "நேத்ர", "அக்னி", "வேத", "பாண", "ருது", "ரிஷி", "வசு", "பிரம்ம", "திசி", "ருத்ர", "ஆதித்ய"]
assert len(PEYAR) == 72 and len(set(PEYAR)) == 72 and len(CHAKRAM) == 12


def melakartha(n):
    """n (1–72) → {en, peyar, chakram, ilakkam (ம, ரிக, தநி), suram, arohanam, avarohanam, arai}.
    கலப்பு அடிமானம் (2, 6, 6): n − 1 = 36 × ம + 6 × ரிக + தநி."""
    if not 1 <= n <= 72:
        raise ValueError("1 முதல் 72 வரை")
    ma, r = divmod(n - 1, 36)
    rg, dn = divmod(r, 6)
    ri, ga = RIGA[rg]
    da, ni = DANI[dn]
    m = list(MA)[ma]
    suram = ["ஸ", ri, ga, m, "ப", da, ni]
    arai = [0, RI[ri], GA[ga], MA[m], 7, DA[da], NI[ni]]
    return dict(en=n, peyar=PEYAR[n - 1], chakram=CHAKRAM[(n - 1) // 6], ilakkam=(ma, rg, dn), suram=suram,
                arohanam=" ".join(suram + ["ஸ்"]), avarohanam=" ".join(["ஸ்"] + suram[::-1]), arai=arai)


def melakarthagal():
    return [melakartha(n) for n in range(1, 73)]


def en_of(arai):
    """அரைச்சுர அமைப்பு → மேளகர்த்தா எண் (மாற்று வழி); இல்லையெனில் None."""
    for r in melakarthagal():
        if r["arai"] == list(arai):
            return r["en"]
    return None


# ── ஏழ்பெரும்பாலை: ஒரு மேளத்தின் ஏழு சுரத்தையும் முறையே குரலாக்கி (பண்ணுப் பெயர்த்தல்) வரும் ஏழு அமைப்பு
PAALAI = ["செம்பாலை", "படுமலைப்பாலை", "செவ்வழிப்பாலை", "அரும்பாலை", "கோடிப்பாலை", "விளரிப்பாலை", "மேற்செம்பாலை"]
NARAMBU = ["குரல்", "துத்தம்", "கைக்கிளை", "உழை", "இளி", "விளரி", "தாரம்"]


def peyarthal(arai, k):
    """arai (ஏழு அரைச்சுர நிலை) — k-ஆம் சுரத்தைக் குரலாக்கிய அமைப்பு."""
    return sorted((arai[(k + i) % 7] - arai[k]) % 12 for i in range(7))


def paalaigal(thodakkam):
    """thodakkam = செம்பாலையாகக் கொள்ளும் மேள எண். → [(பாலை, அரைச்சுரம், மேள எண் / None, பெயர் / None)] ஏழு."""
    a = melakartha(thodakkam)["arai"]
    out = []
    for k, p in enumerate(PAALAI):
        r = peyarthal(a, k)
        n = en_of(r)
        out.append((p, r, n, PEYAR[n - 1] if n else None))
    return out
