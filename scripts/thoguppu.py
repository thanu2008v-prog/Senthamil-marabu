"""ஒரே ஆவணம் — docs/THOGUPPU.md. திட்டங்கள், ஆய்வுகள், அறிக்கைகள் எல்லாம் இதில் பகுதிகளாக.

கையால் எழுதும் பகுதிகள் இக்கோப்பிலேயே திருத்தப்படுகின்றன. நிரல் உருவாக்கும் பகுதிகளை (அறிக்கை, விரிவு, வரைபடம்)
அந்தந்த நிரல் `ezhuthu(திறவு, உரை)` மூலம் தன் குறிகளுக்கு இடையே மட்டும் மாற்றுகிறது:
    <!-- பகுதி:திறவு -->  …  <!-- /பகுதி:திறவு -->
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KOPPU = ROOT / "docs/THOGUPPU.md"
FOOT_RE = re.compile(r"\n+---\n+© 2026 தனுசாந்தன்[^\n]*\n*$")


def _thalaippu_irakku(md):
    """# → ##, ## → ### … (நிரல் தொகுதிகளுக்குள் அல்ல)."""
    out, fence = [], False
    for ln in md.split("\n"):
        if ln.startswith("```"):
            fence = not fence
        if not fence and re.match(r"#{1,5} ", ln):
            ln = "#" + ln
        out.append(ln)
    return "\n".join(out)


def thayaar(md):
    """ஒரு தனி ஆவணத்தை பகுதியாக்க: தனி உரிமை அடிக்குறிப்பை நீக்கி, தலைப்புகளை ஒரு படி இறக்குதல்."""
    return _thalaippu_irakku(FOOT_RE.sub("\n", md).rstrip() + "\n")


def ezhuthu(thiravu, md, irakku=True):
    text = KOPPU.read_text("utf-8")
    a, b = f"<!-- பகுதி:{thiravu} -->", f"<!-- /பகுதி:{thiravu} -->"
    if a not in text or b not in text:
        raise KeyError(f"THOGUPPU.md இல் «{thiravu}» பகுதி இல்லை")
    body = thayaar(md) if irakku else md.rstrip() + "\n"
    i, j = text.index(a) + len(a), text.index(b)
    old = re.search(r"^## .*$", text[i:j], re.M)                 # பகுதித் தலைப்பு (எண்ணோடு) மாறாமல்
    if old:
        body = re.sub(r"^## .*$", lambda _: old.group(0), body, count=1, flags=re.M)
    KOPPU.write_text(text[:i] + "\n" + body + text[j:], "utf-8")


def edu(thiravu):
    """ஒரு பகுதியின் உரை (தனிக் களஞ்சியத்துக்கு எடுத்துச் செல்ல)."""
    text = KOPPU.read_text("utf-8")
    a, b = f"<!-- பகுதி:{thiravu} -->", f"<!-- /பகுதி:{thiravu} -->"
    body = text[text.index(a) + len(a): text.index(b)].strip("\n")
    out, fence = [], False                                   # தலைப்புகளை மீண்டும் ஒரு படி ஏற்றுதல்
    for ln in body.split("\n"):
        if ln.startswith("```"):
            fence = not fence
        if not fence and re.match(r"#{2,6} ", ln):
            ln = ln[1:]
        out.append(ln)
    return "\n".join(out) + "\n"
