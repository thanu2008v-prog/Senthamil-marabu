"""Simple local AI console for the Tamil rule corpus.

Usage:
    python ai_console.py

Examples:
    ezhu.3
    தேடு: நிலம்
    மரம் + கிளை
    247 எழுத்தால்
    help
    quit
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import senthamil_marabu as sm


def _short_text(text, limit=180):
    if not text:
        return ""
    text = " ".join(str(text).split())
    return text[:limit] + ("..." if len(text) > limit else "")


def explain_result(result):
    rtype = result.get("type")
    if rtype == "sutra":
        s = result["sutra"]
        lines = [
            f"{s['id']} | {s['padalam']} | ஓது {s['othu']} | சூத்திரம் {s['sutra']}",
            "மூலம்:", _short_text(s.get("moolam", "")),
            "",
            "காண்டிகை:", _short_text(s.get("kaandigai", {}).get("porul", "")),
        ]
        if s.get("links"):
            lines.append(f"குறிப்புகள்: {', '.join(s['links'][:5])}")
        return "\n".join(lines)

    if rtype == "search":
        items = result.get("results", [])
        if not items:
            return "தேடல் முடிவு இல்லை."
        lines = ["தேடல் முடிவுகள்:"]
        for i, item in enumerate(items[:5], 1):
            lines.append(f"{i}. {item['id']} — {_short_text(item.get('moolam',''))}")
        return "\n".join(lines)

    if rtype == "evidence":
        items = result.get("results", [])
        lines = ["நூலில் தொடர்புடைய பகுதிகள் (சொல் பொருத்தம்):"]
        for i, item in enumerate(items[:5], 1):
            s = item["sutra"]
            lines.append(f"{i}. {s['id']} | நிலை: {s.get('nilai', '—')}")
            lines.append(f"   நூற்பா: {_short_text(s.get('moolam', ''), 240)}")
            lines.append(f"   காண்டிகை: {_short_text(s.get('kaandigai', {}).get('porul', ''), 240)}")
            urai = (s.get("urai") or {}).get("text", "")
            if urai:
                lines.append(f"   உரை: {_short_text(urai, 240)}")
            lines.append(f"   பொருந்திய சொற்கள்: {', '.join(item.get('matched_terms', []))}")
        lines.append("இவை நூலில் கண்ட நேரடிப் பகுதிகள்; பொருள் தெளிவில்லையெனில் நூற்பாவைத் திறந்து முழுச் சூழலைப் பார்க்கவும்.")
        return "\n".join(lines)

    if rtype == "not_found":
        return (
            "இந்த வினாவுக்கு நூலில் பொருந்தும் பகுதியைக் கண்டுபிடிக்க முடியவில்லை. "
            "இதனால் நூலில் இல்லை என்று உறுதியாகச் சொல்ல முடியாது; வேறு முக்கியச் சொல்லால் மீண்டும் கேளுங்கள்."
        )

    if rtype == "punarchi":
        items = result.get("results", [])
        if not items:
            return "புணர்ச்சி முடிவு இல்லை."
        lines = ["புணர்ச்சி வாய்ப்புகள்:"]
        for i, item in enumerate(items[:5], 1):
            lines.append(f"{i}. {item['sol']} | நிலை: {item['nilai']}")
            for rule in item.get("vithi", [])[:3]:
                lines.append(f"   - {rule['id']} {rule['vilakkam']}")
        return "\n".join(lines)

    if rtype == "grammar":
        findings = result.get("findings", [])
        if not findings:
            return "இலக்கணப் பிழை இல்லை."
        lines = ["இலக்கணச் சோதனை:"]
        for i, f in enumerate(findings[:5], 1):
            lines.append(f"{i}. {f['word']} | {f['rule']} | {f['nilai']} | {f['msg']}")
        return "\n".join(lines)

    if rtype == "count":
        return f"எண்ணிக்கை: {result.get('count')} | இலக்கு: {result.get('target', '—')}\n{result.get('note', '')}"

    return str(result)


def parse_question(text):
    q = (text or "").strip()
    if not q:
        return ""
    if q.lower() in {"help", "h", "?"}:
        return "help"
    if q.lower() in {"quit", "exit", "bye"}:
        return "quit"
    if q.lower() == "examples":
        return "examples"
    return q


def show_help():
    print("\n".join([
        "நூல்-அடிப்படைக் குரல் உதவி",
        "",
        "சொல்லுகள்:",
        "  ezhu.3                 -> ஒரு நூற்பா",
        "  தேடு: நிலம்             -> சொல்லின் நூல் தேடல்",
        "  மரம் + கிளை            -> புணர்ச்சி",
        "  247 எழுத்தால்          -> எண் வினா",
        "  help                  -> இந்த பட்டியல்",
        "  examples              -> எடுத்துக்காட்டுகள்",
        "  quit                  -> வெளியேறு",
        "",
        "அறிவுரை:",
        "  - நூலின் விதி மட்டும் ஆணையாகும்.",
        "  - 'ஒருதலை அன்மை' = நூல் தீர்க்காதது.",
        "  - 'நூலில் இல்லை' = நூலில் அந்த விதி இல்லை.",
    ]))


def show_examples():
    print("\n".join([
        "எடுத்துக்காட்டுகள்:",
        "  ezhu.3",
        "  sol.2",
        "  porul.5",
        "  தேடு: பொருள்",
        "  மரம் + கிளை",
        "  30 எழுத்தால்",
        "  நன்றி என்றால் 'quit'",
    ]))


def handle(question):
    q = parse_question(question)
    if q == "quit":
        raise KeyboardInterrupt
    if q == "help":
        show_help(); return None
    if q == "examples":
        show_examples(); return None
    if not q:
        return None
    try:
        result = sm.kel(q)
    except Exception as e:
        return f"சிக்கல்: {e}"
    return explain_result(result)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv:
        question = " ".join(argv)
        answer = handle(question)
        if answer:
            print(answer)
        return 0

    print("செந்தமிழ் மரபு — உள்ளக AI உதவி")
    print("இங்கு நூல், விதி, புணர்ச்சி, தேடல் — அனைத்தும் ஒன்று சேரும்.")
    print("'help' எழுதிப் பாருங்கள். 'quit' மூலம் வெளியேறலாம்.\n")
    while True:
        try:
            q = input("nool> ")
        except KeyboardInterrupt:
            print("\nவெளியேறுகிறேன்.")
            break
        except EOFError:
            print("\nEOF. வெளியேறுகிறேன்.")
            break

        answer = handle(q)
        if answer:
            print(answer)
        print("")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        pass
