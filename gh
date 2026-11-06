#!/usr/bin/env python3
"""Fill Zenodo DOIs across .zenodo.json, CITATION.cff, README.md.

Usage:
    python3 scripts/set_doi.py <concept_doi> <version_doi>
    python3 scripts/set_doi.py 10.5281/zenodo.18962395 10.5281/zenodo.18962396
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RE = re.compile(r'^10\.5281/zenodo\.\d+$')

def _zenodo(concept):
    p = ROOT / ".zenodo.json"
    d = json.loads(p.read_text("utf-8"))
    d["doi"] = concept
    rels = d.setdefault("related_identifiers", [])
    if not any(r.get("identifier") == concept and r.get("relation") == "isIdenticalTo" for r in rels):
        rels.append({"identifier": concept, "relation": "isIdenticalTo", "resource_type": "dataset"})
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"  .zenodo.json  → doi: {concept}")

def _cff(concept):
    p = ROOT / "CITATION.cff"
    p.write_text(re.sub(r'^doi:.*$', f'doi: {concept}', p.read_text("utf-8"), flags=re.M), "utf-8")
    print(f"  CITATION.cff  → doi: {concept}")

def _readme(concept):
    p = ROOT / "README.md"
    t = p.read_text("utf-8")
    t = re.sub(r'\[!\[DOI\]\(https://zenodo\.org/badge/DOI/[^)]+\.svg\)\]\(https://doi\.org/[^)]+\)',
               f'[![DOI](https://zenodo.org/badge/DOI/{concept}.svg)](https://doi.org/{concept})', t)
    t = re.sub(r'`10\.5281/zenodo\.\d+`', f'`{concept}`', t)
    p.write_text(t, "utf-8")
    print(f"  README.md     → badge + citation: {concept}")

def main():
    if len(sys.argv) != 3: raise SystemExit(__doc__)
    concept, version = sys.argv[1], sys.argv[2]
    for d in (concept, version):
        if not RE.match(d): raise SystemExit(f"bad DOI: {d}")
    print(f"Concept:  {concept}\nVersion:  {version}\n")
    _zenodo(concept); _cff(concept); _readme(concept)
    print("\nNext:\n"
          "  git add .zenodo.json CITATION.cff README.md\n"
          "  git commit -m 'docs: add Zenodo DOI'\n"
          "  git push\n"
          "  gh release create v1.0.1 --title 'v1.0.1 — metadata-only' --notes 'DOI + citation metadata; same files as v1.0.0.'")

if __name__ == "__main__":
    main()