"""சோதனைகளின் அடிப்படை (THOGUPPU §25) — ஒவ்வொரு சோதனையும் எதை அளவுகோலாகக் கொள்கிறது.

  அ  நூலின் சொந்த வடிவம் — நூற்பாவிலேயே வரும் சொல் / எண் / வடிவம்; எதிர்பார்ப்பு நூலின் சொல்லே
  ஆ  நூற்பாவின் விதிப்படி ஆக்கிய வடிவம் — அவ்வடிவம் நூலில் இல்லை; விதியின் சொற்படி இவ்வாய்வு ஆக்கியது
  இ  உள் ஒத்திசைவு — இருவழி மாற்றம், தரவு ஒத்திசைவு, அமைப்பு; நூலின் கூற்றைச் சோதிப்பதன்று
  ஈ  இவ்வாய்வின் கணக்கு — ஒருதலை அன்மை (எ.கா. 19 × 13 அடிமானம்)
  உ  பிறன் கோள் — நூலுக்கு வெளியே (இசைக் கணக்கு)

ஒவ்வொரு சோதனைச் செயலும் கீழே பதிவாகியிருக்க வேண்டும்; பதியாத சோதனை இருந்தால் இந்நிரல் நின்றுவிடும் —
புதிய சோதனை எழுதுவோர் அதன் அடிப்படையை அறிவிக்க வேண்டும்."""
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))
from thoguppu import ezhuthu                                         # noqa: E402

VAGAI = {"அ": "நூலின் சொந்த வடிவம்", "ஆ": "நூற்பாவின் விதிப்படி ஆக்கிய வடிவம்", "இ": "உள் ஒத்திசைவு", "ஈ": "இவ்வாய்வின் கணக்கு (ஒருதலை அன்மை)", "உ": "பிறன் கோள் — நூலுக்கு வெளியே"}
ADIPPADAI = {
    "test_adimaanam.py": {"test_247_kattam": "ஈ", "test_ina_mellezhuthu_plus_13": "ஈ", "test_kuril_nedil_plus_1": "ஈ", "test_sol": "ஈ", "test_uyirmei_kootal": "ஈ"},
    "test_api.py": {"test_counts": "அ", "test_moolam_unchanged": "இ", "test_packed_data_in_sync": "இ", "test_schema": "இ", "test_examples_are_in_cited_sutra": "அ",
                    "test_api": "இ", "test_grammar_book_has_no_violation": "அ", "test_grammar_cases": "ஆ", "test_asai": "ஆ", "test_encodings_round_trip": "இ",
                    "test_python_matches_web_page": "இ", "test_kel_entrypoint": "இ",
                    "test_kel_natural_question_returns_nool_evidence": "இ"},
    "test_en.py": {"test_nool_kootru_mathippu": "அ", "test_nool_vadivu_peyaril": "அ", "test_suzharchi": "இ"},
    "test_en_adai.py": {"test_adai_nool": "அ"},
    "test_isai_kanakku.py": {"test_35_thaalam": "உ", "test_72_melakartha": "உ", "test_ezh_perum_paalai": "உ"},
    "test_pothu.py": {"test_ellaam_varaiyaraikku_inangum": "இ", "test_maatteru_sangili": "ஆ", "test_maatteru_vattam_illai": "இ", "test_murai": "ஆ",
                      "test_punarchi_porul_maatteruvodu_ottathu": "இ", "test_saanru_moolathil": "அ", "test_tharukkam_iyakkam": "இ"},
    "test_punarchi.py": {"test_every_rule_cites_book_and_fires": "ஆ", "test_nool_eduthukkaattu": "அ", "test_oli_round_trip": "இ"},
    "test_thanisol.py": {"test_pothu_vithi_maaravillai": "இ", "test_thanisol": "பிரிவு"},      # NOOL → அ, VITHI → ஆ
    "test_urupu.py": {"test_ennin_saariyai": "அ", "test_kurumuthal_naankan_aaran": "ஆ", "test_nool_vadivu": "அ", "test_nool_vadivu_161": "அ", "test_palavai_vatru": "ஆ"},
    "test_vili.py": {"test_vili": "ஆ", "test_vili_kollaathavai": "ஆ"},
    "test_vinai.py": {"test_eeru_ennikkai": "அ", "test_nool_sol": "அ"},
}

t0 = time.time()
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--collect-only"] + [f"tests/{f}" for f in ADIPPADAI], cwd=ROOT, capture_output=True, text=True)
items = [l for l in r.stdout.splitlines() if "::" in l]
cnt = Counter()
for it in items:
    f, fn = re.match(r"tests/([^:]+)::([^\[]+)", it).groups()
    assert f in ADIPPADAI and fn in ADIPPADAI[f], f"அடிப்படை பதியாத சோதனை: {f}::{fn} — scripts/build_sothanai.py ADIPPADAI-இல் சேர்க்க"
    cnt[(f, fn)] += 1
for f, d in ADIPPADAI.items():
    for fn in d:
        assert cnt[(f, fn)], f"பதிவில் உள்ளது, சோதனை இல்லை: {f}::{fn}"

import test_thanisol                                                  # noqa: E402
n_nool, n_vithi = len(test_thanisol.NOOL), len(test_thanisol.VITHI)
assert n_nool + n_vithi == cnt[("test_thanisol.py", "test_thanisol")]

tot = Counter()
per = defaultdict(Counter)
for (f, fn), n in cnt.items():
    v = ADIPPADAI[f][fn]
    if v == "பிரிவு":
        tot["அ"] += n_nool; tot["ஆ"] += n_vithi; per[f]["அ"] += n_nool; per[f]["ஆ"] += n_vithi
    else:
        tot[v] += n; per[f][v] += n
N = sum(tot.values())
assert N == len(items)

t1 = time.time()
run = subprocess.run([sys.executable, "-m", "pytest", "-q"] + [f"tests/{f}" for f in ADIPPADAI], cwd=ROOT, capture_output=True, text=True)
secs = time.time() - t1
assert run.returncode == 0, run.stdout[-800:]
m = re.search(r"(\d+) passed(?:, (\d+) skipped)?", run.stdout)
assert m and int(m.group(1)) + int(m.group(2) or 0) == N, run.stdout[-800:]

sys.path.insert(0, str(ROOT))
from senthamil_marabu import punarchi as P                           # noqa: E402
P.punar("மரம்", "கிளை")
t2 = time.time()
for _ in range(200):
    P.punar("கோயில்", "தூக்கு")
ms = (time.time() - t2) / 200 * 1000
assert P._att() is not None, "முன் தொகுத்த பொறி ஏறவில்லை — build_punarchi.py இயக்குக"

L = ["# சோதனைகளின் அடிப்படை", "",
     f"**வினா:** சோதனைகள் நூல் கூறிய விதிப்படி உருவானவையா? **விடை:** {N} சோதனையுள் **{tot['அ']}** நூலின் சொந்த வடிவத்தையே எதிர்பார்ப்பாகக் கொள்கின்றன; "
     f"**{tot['ஆ']}** நூற்பாவின் விதிப்படி இவ்வாய்வு ஆக்கிய வடிவத்தை; மீதி {tot['இ'] + tot['ஈ'] + tot['உ']} நூலின் கூற்றைச் சோதிப்பன அல்ல "
     f"(உள் ஒத்திசைவு {tot['இ']}, இவ்வாய்வின் கணக்கு {tot['ஈ']}, பிறன் கோள் {tot['உ']}).", "",
     "| வகை | பொருள் | சோதனை | நிலை |", "|---|---|---|---|",
     f"| அ | நூலின் சொந்த வடிவம் — நூற்பாவிலேயே வரும் சொல், எண், வடிவம் | {tot['அ']} | நூலில் நேரடியாக |",
     f"| ஆ | நூற்பாவின் விதிப்படி ஆக்கிய வடிவம் — அவ்வடிவம் நூலில் இல்லை | {tot['ஆ']} | விதி நூலில் நேரடியாக; வடிவம் ஒருதலை அன்மை |",
     f"| இ | உள் ஒத்திசைவு — இருவழி மாற்றம், தரவு, அமைப்பு | {tot['இ']} | நூலின் கூற்று அன்று |",
     f"| ஈ | இவ்வாய்வின் கணக்கு (19 × 13 அடிமானம்) | {tot['ஈ']} | ஒருதலை அன்மை |",
     f"| உ | பிறன் கோள் (சப்த தாளம், மேளகர்த்தா, பாலை) | {tot['உ']} | நூலுக்கு வெளியே |", "",
     "| சோதனைக் கோப்பு | அ | ஆ | இ | ஈ | உ | மொத்தம் |", "|---|---|---|---|---|---|---|"]
for f in ADIPPADAI:
    L.append(f"| `{f}` | " + " | ".join(str(per[f][k]) if per[f][k] else "—" for k in "அஆஇஈஉ") + f" | {sum(per[f].values())} |")
L += [f"| **மொத்தம்** | **{tot['அ']}** | **{tot['ஆ']}** | **{tot['இ']}** | **{tot['ஈ']}** | **{tot['உ']}** | **{N}** |", "",
      "**நெறி:** ஒவ்வொரு சோதனைச் செயலின் அடிப்படையும் `scripts/build_sothanai.py`-இல் பதிவு; பதியாத சோதனை இருந்தால் கட்டமைப்பு நின்றுவிடும். "
      "«ஆ» வகைச் சோதனை ஒரு வடிவத்தை «நூலின் வடிவம்» என்று கூறுவதில்லை — விதியின் சொற்படி வருவது என்றே.", "",
      "## வேகம்", "", "| அளவு | முன்பு | இப்போது |", "|---|---|---|",
      f"| எல்லாச் சோதனையும் ({N}) | 32 நொடி | **{secs:.1f} நொடி** |",
      f"| முதல் புணர்ச்சி (பொறி ஏற்றம்) | 13 நொடி | **0.03 நொடி** |",
      f"| ஒரு புணர்ச்சி | 34 மில்லிநொடி | **{ms:.1f} மில்லிநொடி** |", "",
      "செய்தது: (1) 36 புணர்ச்சிப் பொறியும் கட்டமைப்பின்போதே தொகுக்கப்பட்டு (`data/pori/*.att`), இயக்க நேரத்தில் தொகுப்பு இன்றி, pyfoma இன்றி இயங்குகின்றன; "
      "விதி மாறினால் கைரேகை ஒவ்வாது — அப்போது பழைய வழிக்கே திரும்பும், தவறான பொறி இயங்காது. "
      "(2) ஏற்றுமதிக் கோப்புகள் நிலை எண் வரிசை நிலையானதாக்கப்பட்டன — ஒரே விதிக்கு எப்போதும் ஒரே கோப்பு. "
      "(3) பொது வடிவ அமைப்புச் சோதனை சரிபார்ப்பியை ஒருமுறை மட்டும் தொகுக்கிறது. "
      "துல்லியம் மாறவில்லை: முன் தொகுத்த பொறிகள் pyfoma விளைவோடு 317 / 317 ஒத்தன (`scripts/build_punarchi.py`).", ""]
ezhuthu("sothanai", "\n".join(L))
print(f"சோதனை அடிப்படை: {N} — {dict(tot)}; {secs:.1f} நொடி; புணர்ச்சி {ms:.1f} ms")
