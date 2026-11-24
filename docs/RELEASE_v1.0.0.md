# v1.0.0 — செந்தமிழ் மரபு / Senthamil Marabu

**1602 சூத்திரம் · 27 ஓத்து · 3 படலம் · 1 பிண்டம்**

| | |
|---|---|
| **ஆசிரியர்** | தனுசாந்தன் வர்ணகுலசிங்கம் — [ORCID 0009-0005-4309-7476](https://orcid.org/0009-0005-4309-7476) |
| **முதல் நூல்** | தொல்காப்பியம் (பொருள். 640 — முதல்வன் கண்டது) |
| **உரிமம்** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| **Self-verifying** | பொருள். 645–656 → executable checks (`check_nool.py`, `check_urai.py`) |
| **மூலம்** | Immutable — பொருள். 652 (SHA-256 in `sha.log`) |

## கோப்புகள்

| கோப்பு | விவரம் |
|---|---|
| `SENTHAMIL_MARABU.md` | முழு நூல், நூல்மரபு வரிசையில் |
| `SENTHAMIL_MARABU.tei.xml` | TEI P5 archival projection |
| `sha.log` | மூலம் / உரை / காண்டிகை SHA-256 |
| `.zenodo.json` | DataCite metadata |
| `CITATION.cff` | மேற்கோள் template |

## ஆய்வுக்கு

```bash
grep -n "^### ezhu.174" SENTHAMIL_MARABU.md
grep -n "இயைபு: ezhu.173" SENTHAMIL_MARABU.md
sed -n '/^## ஓத்து 6 /,/^## ஓத்து 7 /p' SENTHAMIL_MARABU.md > othu06.md
sqlite3 senthamil_v2.db "SELECT id FROM sutra WHERE moolam LIKE '%உருவு%'"