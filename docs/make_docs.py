"""ஆய்வாளர் ஆவணங்கள் உருவாக்கம்: docs/TARAVU.md (தரவு அகராதி), datapackage.json (Frictionless), docs/DATA_CARD.md.
எண்ணிக்கைகள் எல்லாம் தரவிலிருந்தே கணிக்கப்படுகின்றன. python3 docs/make_docs.py"""
import json, sys, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import senthamil_marabu as sm  # noqa: E402

R = sm.sutras()
C = lambda f: collections.Counter(f(r) for r in R)
info = sm.info()
nil = info["nilai"]; pad = info["padalam"]
vagai = C(lambda r: (r.get("urai") or {}).get("vagai"))
kind = C(lambda r: (r.get("kanini") or {}).get("kind"))
ut = collections.Counter(u["peyar"] for r in R for u in r.get("utthi", []))
n_en = sum(1 for r in R if r["kaandigai"].get("en"))
n_mar = sum(1 for r in R if (r.get("urai") or {}).get("maruthalai"))
n_edu = sum(len(r["kaandigai"].get("eduthukkaattu", [])) for r in R)
n_ut = sum(1 for r in R if r.get("utthi"))

FIELDS = [
    ("id", "உரை", "சூத்திர அடையாளம்: «ezhu.N», «sol.N», «porul.N» — அதிகாரத்துள் தொடர் எண்", "—"),
    ("pindam", "எண்", "பிண்டம் — மூன்று உறுப்பும் அடக்கிய முழு நூல்; இந்நூல் ஒரே பிண்டம் (மதிப்பு எப்போதும் 1)", "பொருள். 470, 474"),
    ("padalam", "உரை", "அதிகாரம்: ezhuthu / sol / porul", "பொருள். 473 (படலம்)"),
    ("othu", "எண்", "அதிகாரத்துள் ஓத்து (இயல்) எண்", "பொருள். 472 (ஓத்து)"),
    ("sutra", "எண்", "ஓத்துக்குள் சூத்திர எண்", "பொருள். 471 (சூத்திரம்)"),
    ("moolam", "உரை", "சூத்திர மூலம், மாற்றமின்றி; அடிகள் «\\n» ஆல் பிரிக்கப்பட்டவை", "பொருள். 652"),
    ("kaandigai.porul", "உரை", "காண்டிகை — சூத்திரப் பொருள்", "பொருள். 647"),
    ("kaandigai.ethu", "உரை", "ஏது நடை (முன்–பின் தொடர்பு, காரணம்), நூலுள் எடுத்துக்காட்டோடு", "பொருள். 648"),
    ("kaandigai.eduthukkaattu[]", "பட்டியல்", "{text, from}: மேற்கோள் உரையும் அது வரும் சூத்திரமும் — from சூத்திரத்தில் எழுத்துக்கு எழுத்து உள்ளது எனச் சரிபார்க்கப்பட்டது", "பொருள். 648"),
    ("kaandigai.en", "பொருள்", "{kooruvathu, enniyathu}: சூத்திரம் கூறும் தொகை, காண்டிகை எண்ணிய தொகை (அரை மாத்திரை போன்றவை பின்னம்)", "பொருள். 656 (தொகுத்துக் கூறல்)"),
    ("urai.vagai", "உரை", "விதி / விலக்கு / விதி-விலக்கு", "பொருள். 645"),
    ("urai.vilakkukkuriyathu[]", "பட்டியல்", "விலக்காயின் எந்தச் சூத்திரத்துக்கு", "பொருள். 645"),
    ("urai.iyaipu[]", "பட்டியல்", "இயைபுச் சூத்திரங்களின் id", "பொருள். 649"),
    ("urai.text", "உரை", "உரை: இயைபு, மறுதலைக் கடாஅ முதலியன. «(645)», «(649)», «(650)» என்ற குறிகள் உரையின் எந்தக் கூறு என்பதைச் சுட்டுகின்றன; «ஆய்வு N» நூலின் «ஆய்வுகள்» பிற்சேர்க்கை எண்", "பொருள். 649, 650"),
    ("urai.maruthalai[]", "பட்டியல்", "{kadaa, maattram}: மறுதலைக் கடாஅவும் விடையும் (கட்டமைந்த வடிவில் உள்ளவை மட்டும்; பிறவை urai.text-இல்)", "பொருள். 650"),
    ("urai.thunivu", "உரை", "ஒரே துணிவு — நிலையும் தீராத கூறும்", "பொருள். 650"),
    ("nilai", "உரை", "துணிவின் நிலை: நூலில் நேரடியாக / ஒருதலை அன்மை / நூலில் இல்லை", "பொருள். 650, 656"),
    ("utthi[]", "பட்டியல்", "{peyar, saanru}: சூத்திரச் சொல்லில் அடையாளம் உள்ள உத்தியும் அச்சொல்லும்; அடையாளம் இல்லாத உத்திகள் குறிக்கப்படுவதில்லை", "பொருள். 644, 656"),
    ("kanini", "பொருள்", "கணினி வகைப்பாடு: kind (rule, enumeration, definition, classification, exception, meta) முதலியன — விதிகளைப் பொறியால் இயக்குவதற்கு", "—"),
    ("links[]", "பட்டியல்", "காண்டிகை சுட்டும் பிற சூத்திரங்கள்", "—"),
]

L = []; A = L.append
A("# தரவு அகராதி — செந்தமிழ் மரபு")
A("")
A(f"பதிப்பு {sm.__version__} · DOI {sm.DOI} · உரிமம்: காண்டிகை, உரை, தொகுப்பு, கணினி வடிவம் CC BY-NC 4.0; சூத்திர மூலம் பொதுவுடைமை.")
A("")
A("## 1. கோப்புகள்")
A("")
A("| கோப்பு | வடிவம் | உள்ளது |")
A("|---|---|---|")
A("| `data_v2/<படலம்>/othu-NN.jsonl` | JSON Lines | மூலத் தரவு — ஓத்துக்கு ஒரு கோப்பு; திருத்தம் இங்கே மட்டும் (sources/ வழியாக scripts/migrate_v2.py) |")
A("| `senthamil_marabu/data/sutras.jsonl` | JSON Lines | அதே தரவு, ஒரே கோப்பில், நூல் வரிசையில் (Python தொகுப்புக்கு) |")
A("| `build/sutras_v2.csv` | CSV (UTF-8) | ஒவ்வொரு சூத்திரமும் ஒரு வரி — அட்டவணை மென்பொருளுக்கு |")
A("| `build/senthamil_v2.db` | SQLite | அட்டவணைகள்: sutra, edu (எடுத்துக்காட்டு), link, maruthalai, utthi; முழு உரைத் தேடல் sutra_fts |")
A("| `build/bundle_v2.json` | JSON | தேடும் செயலிக்கான தொகுப்பு, சுட்டு அட்டவணைகளோடு |")
A("| `schema/sutra.v2.schema.json` | JSON Schema | பதிவு வடிவ வரையறை; ஒவ்வொரு உருவாக்கத்திலும் சரிபார்க்கப்படுகிறது |")
A("| `datapackage.json` | Frictionless Data | கோப்புகளும் புலங்களும் — தரவு மென்பொருள்கள் நேரடியாகப் படிக்க |")
A("")
A("## 2. எண்ணிக்கை")
A("")
A(f"- சூத்திரம் {info['sutras']}: எழுத்து {pad['ezhuthu']}, சொல் {pad['sol']}, பொருள் {pad['porul']}.")
A(f"- நிலை: நூலில் நேரடியாக {nil.get('நூலில் நேரடியாக',0)}, ஒருதலை அன்மை {nil.get('ஒருதலை அன்மை',0)}, நூலில் இல்லை {nil.get('நூலில் இல்லை',0)}.")
A(f"- உரை வகை: " + ", ".join(f"{k} {v}" for k, v in vagai.most_common()) + ".")
A(f"- எடுத்துக்காட்டு மேற்கோள் {n_edu}; தொகை எண் உள்ள காண்டிகை {n_en}; கட்டமைந்த மறுதலைக் கடாஅ {n_mar}; உத்தி அடையாளம் உள்ள சூத்திரம் {n_ut}.")
A("")
A("## 3. புலங்கள் (ஒரு பதிவு)")
A("")
A("| புலம் | வகை | பொருள் | நூற்பா அடிப்படை |")
A("|---|---|---|---|")
for f in FIELDS:
    A(f"| `{f[0]}` | {f[1]} | {f[2]} | {f[3]} |")
A("")
A("## 4. உத்திகள் (சூத்திரச் சொல் அடையாளத்தால்)")
A("")
A("| உத்தி | சூத்திரம் |")
A("|---|---|")
for k, v in ut.most_common():
    A(f"| {k} | {v} |")
A("")
A("## 5. நம்பகத் தன்மை — ஒவ்வொரு உருவாக்கத்திலும் தானாக (make check)")
A("")
A("- சூத்திர மூலம் மூலப் பாடத்தோடு எழுத்துக்கு எழுத்து ஒப்பு (sources/moolam.json).")
A("- வடிவரையறைச் சோதனை (JSON Schema); எடுத்துக்காட்டு மேற்கோள் ஒவ்வொன்றும் சுட்டிய சூத்திரத்தில் உள்ளது.")
A("- பத்துச் சிதைவுச் சோதனை (பொருள். 654) — scripts/sithaivu.py; முடிவு build/sithaivu.json.")
A("- இலக்கணச் சரிபார்ப்பி நூலின் 1602 சூத்திரத்திலும் «நூலுக்கு மாறு» 0; Python, இணையப் பக்கம் இரண்டும் ஒரே முடிவு (tests/test_api.py).")
A("")
A("## 6. அறிய வேண்டியவை")
A("")
A("- அளவுகோல் இந்நூல் ஒன்றே; பிற உரையாசிரியர் கருத்து இல்லை. நூல் தீர்க்காதது «ஒருதலை அன்மை».")
A("- எழுத்ததிகாரப் பாடம் பழைய அச்சின் சொற்பிரிப்பு (எ.கா. «எழுத்தோ ரன்ன»); சொல், பொருள் அதிகாரப் பாடம் மதுரைத் திட்ட மின்பதிப்பு — அதன் சொற்பிரிப்பைச் சார்ந்த எண்ணிக்கைகள் (சொல், சார்பெழுத்து) ஒருதலை அன்மை.")
A("- மதுரைத் திட்ட மின்பாடம் இவ்வுரிமத்துள் அடங்காது; அவர்களின் நிபந்தனைக்கு உட்பட்டது.")
A("")
A("## 7. மேற்கோள்")
A("")
A(f"வர்ணகுலசிங்கம், தனுசாந்தன் (2026). *செந்தமிழ் மரபு — 1602 நூற்பா, காண்டிகை, உரை* (பதிப்பு {sm.__version__}). Zenodo. https://doi.org/{sm.DOI}")
A("")
A("---")
A("")
A("© 2026 தனுசாந்தன் வர்ணகுலசிங்கம் — உரிமம்: CC BY-NC 4.0; வணிக உரிமை ஆசிரியருக்கு மட்டும்; தொழில்நுட்ப உதவி: Claude (Anthropic).")
(ROOT / "docs/TARAVU.md").write_text("\n".join(L) + "\n", "utf-8")

csv_fields = ["id", "padalam", "othu", "sutra", "moolam", "kaandigai_porul", "kaandigai_ethu", "urai", "vagai", "utthi", "thunivu", "nilai"]
desc = {f[0].split("[")[0].replace("kaandigai.", "kaandigai_").replace("urai.text", "urai").replace("urai.", ""): f[2] for f in FIELDS}
dp = {
    "name": "senthamil-marabu", "title": "செந்தமிழ் மரபு — Senthamil Marabu", "version": sm.__version__,
    "description": "1602 தொல்காப்பிய நூற்பா (Tolkappiyam sutras) with a new commentary (காண்டிகை, உரை, துணிவு) judged solely by the text itself.",
    "id": f"https://doi.org/{sm.DOI}", "homepage": "https://github.com/thanu2008v-prog/senthamil-marabu",
    "licenses": [{"name": "CC-BY-NC-4.0", "path": "https://creativecommons.org/licenses/by-nc/4.0/", "title": "Creative Commons Attribution-NonCommercial 4.0"}],
    "contributors": [{"title": "Thanushanthan Varnakulasingam", "path": "https://orcid.org/0009-0005-4309-7476", "role": "author"}],
    "keywords": ["Tamil", "Tolkappiyam", "தொல்காப்பியம்", "grammar", "prosody", "commentary"], "languages": ["ta"],
    "resources": [
        {"name": "sutras-csv", "path": "build/sutras_v2.csv", "format": "csv", "mediatype": "text/csv", "encoding": "utf-8",
         "schema": {"fields": [{"name": f, "type": "integer" if f in ("othu", "sutra") else "string", "description": desc.get(f, "")} for f in csv_fields],
                    "primaryKey": "id"}},
        {"name": "sutras-jsonl", "path": "senthamil_marabu/data/sutras.jsonl", "format": "jsonl", "mediatype": "application/jsonl",
         "encoding": "utf-8", "description": "முழுப் பதிவுகள் — schema/sutra.v2.schema.json", "schema": "schema/sutra.v2.schema.json"},
        {"name": "sqlite", "path": "build/senthamil_v2.db", "format": "sqlite", "mediatype": "application/vnd.sqlite3",
         "description": "tables: sutra, edu, link, maruthalai, utthi; FTS: sutra_fts"},
    ],
}
(ROOT / "datapackage.json").write_text(json.dumps(dp, ensure_ascii=False, indent=1) + "\n", "utf-8")

E_ = []; B = E_.append
B("# Data card — Senthamil Marabu (செந்தமிழ் மரபு)")
B("")
B("*An English summary for researchers. The book itself and all commentary are in Tamil.*")
B("")
B(f"**What it is.** All {info['sutras']} sutras of the Tolkappiyam (Ezhuthu {pad['ezhuthu']}, Sol {pad['sol']}, Porul {pad['porul']}), each with a new commentary written in the structure the Tolkappiyam itself prescribes for commentary (Porul 645–650): *kaandigai* (meaning, reason, internal examples), *urai* (rule/exception, connections, counter-question) and a single *thunivu* (conclusion) with a three-way status: stated in the text ({nil.get('நூலில் நேரடியாக',0)}), not settled by the text ({nil.get('ஒருதலை அன்மை',0)}), not in the text ({nil.get('நூலில் இல்லை',0)}). The only authority used is the text itself; no later commentator is cited.")
B("")
B("**Formats.** JSON Lines (`senthamil_marabu/data/sutras.jsonl`, schema in `schema/sutra.v2.schema.json`), CSV (`build/sutras_v2.csv`), SQLite with full-text search (`build/senthamil_v2.db`), Frictionless `datapackage.json`. Field definitions: `docs/TARAVU.md`.")
B("")
B("**Python.** `pip install git+https://github.com/thanu2008v-prog/senthamil-marabu` then:")
B("")
B("```python")
B("import senthamil_marabu as sm")
B("sm.get('ezhu.1')['moolam']; sm.by_nilai('ஒருதலை அன்மை'); sm.to_dataframe()")
B("from senthamil_marabu import ilakkanam, yappu, kuri, orunguri")
B("ilakkanam.check(text)   # phonotactic rules: word-initial/final letters, consonant clusters (Ezhuthu 22–78)")
B("yappu.check(poem)       # prosody: asai, seer, line class by letter count (Porul 312–404)")
B("kuri.encode(text)       # 16-bit encoding whose bit fields follow the text's letter classes")
B("orunguri.to_model(text) # a Unicode-style character model derived from the text")
B("```")
B("")
B("**Quality checks (run on every build).** Sutra text identical to the source; JSON Schema validation; every quoted example verified character-by-character against the cited sutra; the text's own ten defects of a treatise (Porul 654) checked automatically; the grammar checker reports 0 violations on the 1602 sutras themselves, with identical results in Python and in the web page.")
B("")
B("**Limitations.** Word segmentation follows the source e-texts (Ezhuthu: an old print; Sol and Porul: Project Madurai); counts that depend on segmentation are marked as unsettled. The Project Madurai text is not covered by this licence.")
B("")
B(f"**Licence.** Commentary, compilation and code: CC BY-NC 4.0 (commercial use only with the author's written permission). Sutras: public domain.")
B("")
B(f"**Cite.** Varnakulasingam, T. (2026). *Senthamil Marabu* (v{sm.__version__}). Zenodo. https://doi.org/{sm.DOI}")
(ROOT / "docs/DATA_CARD.md").write_text("\n".join(E_) + "\n", "utf-8")
print("docs: TARAVU.md, DATA_CARD.md, datapackage.json")
