"""data_v2/*/*.jsonl → senthamil_marabu/data/sutras.jsonl (Python தொகுப்புக்குள் ஒரே கோப்பு; நூல் வரிசையில்)."""
import json, glob
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
order = {"ezhu": 0, "sol": 1, "porul": 2}
recs = [json.loads(l) for p in sorted(glob.glob(str(ROOT / "data_v2/*/*.jsonl"))) for l in open(p, encoding="utf-8") if l.strip()]
recs.sort(key=lambda r: (order[r["id"].split(".")[0]], int(r["id"].split(".")[1])))
out = ROOT / "senthamil_marabu/data/sutras.jsonl"
out.write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in recs), "utf-8")
print(f"{out.relative_to(ROOT)}: {len(recs)} பதிவு, {out.stat().st_size // 1024} KB")
