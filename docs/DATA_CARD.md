# Data card — Senthamil Marabu (செந்தமிழ் மரபு)

*An English summary for researchers. The book itself and all commentary are in Tamil.*

**What it is.** All 1602 sutras of the Tolkappiyam (Ezhuthu 483, Sol 463, Porul 656), each with a new commentary written in the structure the Tolkappiyam itself prescribes for commentary (Porul 645–650): *kaandigai* (meaning, reason, internal examples), *urai* (rule/exception, connections, counter-question) and a single *thunivu* (conclusion) with a three-way status: stated in the text (1386), not settled by the text (215), not in the text (1). The only authority used is the text itself; no later commentator is cited.

**Formats.** JSON Lines (`senthamil_marabu/data/sutras.jsonl`, schema in `schema/sutra.v2.schema.json`), CSV (`build/sutras_v2.csv`), SQLite with full-text search (`build/senthamil_v2.db`), Frictionless `datapackage.json`. Field definitions: `docs/TARAVU.md`.

**Python.** `pip install git+https://github.com/thanu2008v-prog/senthamil-marabu` then:

```python
import senthamil_marabu as sm
sm.get('ezhu.1')['moolam']; sm.by_nilai('ஒருதலை அன்மை'); sm.to_dataframe()
from senthamil_marabu import ilakkanam, yappu, kuri, orunguri
ilakkanam.check(text)   # phonotactic rules: word-initial/final letters, consonant clusters (Ezhuthu 22–78)
yappu.check(poem)       # prosody: asai, seer, line class by letter count (Porul 312–404)
kuri.encode(text)       # 16-bit encoding whose bit fields follow the text's letter classes
orunguri.to_model(text) # a Unicode-style character model derived from the text
```

**Quality checks (run on every build).** Sutra text identical to the source; JSON Schema validation; every quoted example verified character-by-character against the cited sutra; the text's own ten defects of a treatise (Porul 654) checked automatically; the grammar checker reports 0 violations on the 1602 sutras themselves, with identical results in Python and in the web page.

**Limitations.** Word segmentation follows the source e-texts (Ezhuthu: an old print; Sol and Porul: Project Madurai); counts that depend on segmentation are marked as unsettled. The Project Madurai text is not covered by this licence.

**Licence.** Commentary, compilation and code: CC BY-NC 4.0 (commercial use only with the author's written permission). Sutras: public domain.

**Cite.** Varnakulasingam, T. (2026). *Senthamil Marabu* (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.24011590
