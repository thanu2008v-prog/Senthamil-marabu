#!/usr/bin/env python3
"""Fetch Zenodo DOIs for this repo and patch .zenodo.json, CITATION.cff, README.md.

Usage:
    python3 scripts/fetch_doi.py                 # repo auto-discovered from .zenodo.json
    python3 scripts/fetch_doi.py --repo USER/REPO

Requires network to zenodo.org (public records; works with no auth).
"""
import json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZEN  = "https://zenodo.org/api/records"

def api(q, size=20):
    url = f"{ZEN}?q={urllib.parse.quote(q)}&size={size}&sort=mostrecent"
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read())

def _concept(h):
    return h.get("conceptdoi") or (
        f"10.5281/zenodo.{h['conceptrecid']}" if h.get("conceptrecid") else None)

def find_record(repo):
    repo = repo.rstrip("/").removesuffix(".git")
    for q in (f'related.identifier:"{repo}"',
              f'related.identifier:"{repo}.git"'):
        hits = api(q).get("hits", {}).get("hits", [])
        hits = [h for h in hits if h.get("doi") and _concept(h)]
        if not hits: continue
        hits.sort(key=lambda h: h.get("metadata", {}).get("publication_date", ""), reverse=True)
        h = hits[0]
        return _concept(h), h["doi"], h.get("metadata", {}).get("version"), \
               h.get("metadata", {}).get("title")
    # fallback: ORCID
    m = re.search(r'"orcid"\s*:\s*"(\d{4}-\d{4}-\d{4}-\d{4})"',
                  (ROOT / ".zenodo.json").read_text("utf-8"))
    if m:
        hits = api(f'creators.orcid:"{m[1]}"').get("hits", {}).get("hits", [])
        hits = [h for h in hits if h.get("doi") and _concept(h)]
        if hits:
            h = hits[0]
            return _concept(h), h["doi"], h.get("metadata", {}).get("version"), \
                   h.get("metadata", {}).get("title")
    return None, None, None, None

def patch_zenodo(concept):
    p, d = ROOT / ".zenodo.json", json.loads((ROOT / ".zenodo.json").read_text("utf-8"))
    d["doi"] = concept
    rels = d.setdefault("related_identifiers", [])
    if not any(r.get("identifier") == concept and r.get("relation") == "isIdenticalTo" for r in rels):
        rels.append({"identifier": concept, "relation": "isIdenticalTo", "resource_type": "dataset"})
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"  .zenodo.json  → doi: {concept}")

def patch_cff(concept):
    p, t = ROOT / "CITATION.cff", (ROOT / "CITATION.cff").read_text("utf-8")
    t = (re.sub(r'^doi:.*$', f'doi: {concept}', t, flags=re.M)
         if re.search(r'^doi:\s*\S', t, re.M) else t.rstrip() + f"\ndoi: {concept}\n")
    p.write_text(t, "utf-8")
    print(f"  CITATION.cff  → doi: {concept}")

def patch_readme(concept):
    p, t = ROOT / "README.md", (ROOT / "README.md").read_text("utf-8")
    t = re.sub(
        r'\[!\[DOI\]\(https://zenodo\.org/badge/DOI/[^)]+\.svg\)\]\(https://doi\.org/[^)]+\)',
        f'[![DOI](https://zenodo.org/badge/DOI/{concept}.svg)](https://doi.org/{concept})', t)
    t = re.sub(r'`10\.5281/zenodo\.\d+`', f'`{concept}`', t)
    p.write_text(t, "utf-8")
    print(f"  README.md     → badge: {concept}")

def main():
    repo = sys.argv[sys.argv.index("--repo") + 1] if "--repo" in sys.argv else None
    if not repo:
        d = json.loads((ROOT / ".zenodo.json").read_text("utf-8"))
        for r in d.get("related_identifiers", []):
            if "github.com" in r.get("identifier", ""):
                repo = r["identifier"]; break
    if not repo:
        sys.exit("No GitHub repo found in .zenodo.json; pass --repo USER/REPO")
    print(f"Repo: {repo}")

    concept, version, v, title = find_record(repo)
    if not concept:
        sys.exit(
            "No Zenodo record found for this repo.\n"
            "  (a) enable the GitHub→Zenodo webhook at "
            "https://zenodo.org/account/settings/github/\n"
            "  (b) publish a GitHub release with a v* tag\n"
            "  (c) wait ~2 min after publishing")

    print(f"\nFound:")
    print(f"  Title:    {title}")
    print(f"  Version:  {v}")
    print(f"  Concept:  {concept}")
    print(f"  Version:  {version}\n")

    patch_zenodo(concept); patch_cff(concept); patch_readme(concept)
    print("\nNext:")
    print("  git add scripts/fetch_doi.py .zenodo.json CITATION.cff README.md")
    print(f"  git commit -m 'docs: add Zenodo DOI {concept}'")
    print("  git push")
    print("  gh release create v1.0.1 --title 'v1.0.1 — metadata-only' \\")
    print("    --notes 'DOI + citation metadata (no files changed; same 1602-sutra edition as v1.0.0).'")

if __name__ == "__main__":
    main()