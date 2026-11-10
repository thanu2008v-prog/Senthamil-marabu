"""ஒரே துணிவு (பொருள். 650: "தெற்றென ஒரு பொருள் ஒற்றுமை கொளீஇ / துணிவொடு நிற்றல்").

காண்டிகையின் நிலைக்குறியும் உரையின் "நிலை:" பகுதியும் தனித்தனியே இருந்தபோது 77 இடத்தில்
மாறுபட்டன (பொருள். 654 "மாறுகொளக் கூறல்"). இங்கே இரண்டையும் ஒரே துணிவாக்கி, பதிவின்
நிலையை அத்துணிவிலிருந்தே பெறுகிறோம்.
"""
import re

STAT = ("நூலில் நேரடியாக", "ஒருதலை அன்மை", "ஒருதலை அன்று", "நூலில் இல்லை", "பாட ஐயம்")
NILAI_TAIL = re.compile(r"\s*(?:நிலை|துணிவு):\s*(.*)$", re.S)


def split_text(text):
    """உரைச் சொற்றொடரின் இறுதி "நிலை: …" பகுதியைப் பிரித்தல் → (உரை, நிலைப் பகுதி)."""
    text = (text or "").strip()
    i = text.rfind(" நிலை: ")
    if text.startswith("நிலை: "):
        i = 0
    if i < 0:
        return text, ""
    tail = text[i:].strip()[len("நிலை:"):].strip()
    if len(tail) > 300:                  # "துயிலெடை நிலை" போன்ற சொல் — துணிவுப் பகுதி அன்று
        return text, ""
    return text[:i].strip(), tail


def reconcile(nilai_k, th, aiyam=""):
    th = (th or "").strip().rstrip(".").strip()
    if len(th) > 300:                    # உரைப் பகுதி தவறி இங்கு வந்தது — துணிவு அன்று
        th = ""
    if not th:
        th = nilai_k
    elif not any(s in th for s in STAT):
        th = f"{nilai_k}; {th}"
    if "ஒருதலை" in aiyam and not any(s in th for s in ("ஒருதலை", "பாட ஐயம்")):
        th += "; உரை சுட்டிய ஐயம் ஒருதலை அன்மை"
    if nilai_k == "ஒருதலை அன்மை" and not any(s in th for s in ("ஒருதலை", "பாட ஐயம்", "நூலில் இல்லை")):
        th += "; காண்டிகை சுட்டிய ஐயம் ஒருதலை அன்மை"
    if th.startswith("நூலில் இல்லை"):
        nilai = "நூலில் இல்லை"
    elif "ஒருதலை" in th or "பாட ஐயம்" in th:
        nilai = "ஒருதலை அன்மை"
    elif "நூலில் இல்லை" in th and "நேரடியாக" not in th:
        nilai = "நூலில் இல்லை"
    else:
        nilai = "நூலில் நேரடியாக"
    return th, nilai


def dedup_ethu(porul, ethu):
    """ஏது காண்டிகைப் பொருளையே மீண்டும் கூறினால் (பொருள். 654 "கூறியது கூறல்") அப்பகுதியை நீக்கி,
    முன் சூத்திரத் தொடர்பை (ஏது நடை, 648) மட்டும் வைத்தல்."""
    import difflib
    if not ethu:
        return ethu
    sim = lambda a, b: difflib.SequenceMatcher(None, a, b).ratio()
    m = re.match(r"^(.{0,80}?(?:என்றது|சொன்னது|கூறியது))[;,]\s*(.+)$", ethu, re.S)
    if m and sim(porul, m[2]) > 0.6:
        rest = m[2]
        new_q = [q for q in re.findall(r'"([^"]+)"', rest) if q not in porul]
        new_n = [n for n in re.findall(r"\d+", rest) if n not in porul]
        if not new_q and not new_n:              # புதிதாக எதுவும் இல்லை — கூறியது கூறல்
            return f"{m[1]}; இது அதன் தொடர்ச்சி."
    return ethu
